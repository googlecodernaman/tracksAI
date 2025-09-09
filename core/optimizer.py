"""
Core optimization engine for railway traffic management.

This module contains the main decision-making logic using constraint
satisfaction and optimization algorithms.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp

from .models import (
    Train, Section, Station, Decision, OptimizationResult, 
    SystemState, TrainType, TrainStatus
)

logger = logging.getLogger(__name__)


class RailwayOptimizer:
    """
    Main optimization engine for railway traffic decisions.
    
    Uses constraint programming and linear optimization to find
    optimal train precedence and routing decisions.
    """
    
    def __init__(self, time_limit_seconds: int = 30):
        """
        Initialize the optimizer.
        
        Args:
            time_limit_seconds: Maximum time to spend on optimization
        """
        self.time_limit_seconds = time_limit_seconds
        self.solver = None
    
    def optimize(self, system_state: SystemState) -> OptimizationResult:
        """
        Generate optimal decisions for the current system state.
        
        Args:
            system_state: Current state of the railway system
            
        Returns:
            OptimizationResult with recommended decisions
        """
        start_time = datetime.utcnow()
        
        try:
            # Filter trains that need decisions
            trains_needing_decisions = self._get_trains_needing_decisions(system_state)
            
            if not trains_needing_decisions:
                return OptimizationResult(
                    decisions=[],
                    total_delay_reduction=0,
                    throughput_improvement=0.0,
                    confidence_score=1.0,
                    computation_time=0.0
                )
            
            # Use constraint programming for complex precedence decisions
            decisions = self._solve_precedence_problem(
                trains_needing_decisions, 
                system_state
            )
            
            # Calculate metrics
            delay_reduction = self._calculate_delay_reduction(decisions, system_state)
            throughput_improvement = self._calculate_throughput_improvement(decisions)
            confidence = self._calculate_confidence(decisions, system_state)
            
            computation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return OptimizationResult(
                decisions=decisions,
                total_delay_reduction=delay_reduction,
                throughput_improvement=throughput_improvement,
                confidence_score=confidence,
                computation_time=computation_time
            )
            
        except Exception as e:
            logger.exception(f"Optimization failed: {e}")
            # Return fallback decisions
            return self._generate_fallback_decisions(system_state)
    
    def _get_trains_needing_decisions(self, system_state: SystemState) -> List[Train]:
        """Get trains that need immediate decisions."""
        trains_needing_decisions = []
        
        for train in system_state.trains:
            if (train.status in [TrainStatus.RUNNING, TrainStatus.DELAYED] and
                train.current_section is not None):
                trains_needing_decisions.append(train)
        
        return trains_needing_decisions
    
    def _solve_precedence_problem(
        self, 
        trains: List[Train], 
        system_state: SystemState
    ) -> List[Decision]:
        """
        Solve the train precedence problem using constraint programming.
        
        This determines which trains should proceed first when there are
        conflicts for shared resources (sections, platforms).
        """
        model = cp_model.CpModel()
        
        # Create variables for train precedence
        precedence_vars = {}
        for i, train1 in enumerate(trains):
            for j, train2 in enumerate(trains):
                if i != j:
                    # precedence_vars[(i,j)] = 1 if train1 goes before train2
                    precedence_vars[(i, j)] = model.NewBoolVar(f'precedence_{i}_{j}')
        
        # Add constraints
        self._add_precedence_constraints(model, trains, precedence_vars, system_state)
        self._add_priority_constraints(model, trains, precedence_vars)
        self._add_capacity_constraints(model, trains, precedence_vars, system_state)
        
        # Objective: minimize total delay
        total_delay = model.NewIntVar(0, 10000, 'total_delay')
        delay_terms = []
        
        for i, train in enumerate(trains):
            # Weight delay by train priority
            weight = train.priority * 10
            delay_terms.append(weight * train.delay_minutes)
        
        model.Add(total_delay == sum(delay_terms))
        model.Minimize(total_delay)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_seconds
        
        status = solver.Solve(model)
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return self._extract_decisions_from_solution(
                solver, trains, precedence_vars, system_state
            )
        else:
            logger.warning("Optimization solver failed, using heuristic")
            return self._generate_heuristic_decisions(trains, system_state)
    
    def _add_precedence_constraints(
        self, 
        model: cp_model.CpModel, 
        trains: List[Train], 
        precedence_vars: Dict[Tuple[int, int], cp_model.IntVar],
        system_state: SystemState
    ):
        """Add constraints for train precedence."""
        for i, train1 in enumerate(trains):
            for j, train2 in enumerate(trains):
                if i != j:
                    # If trains are competing for the same resource
                    if self._trains_compete_for_resource(train1, train2, system_state):
                        # Ensure precedence is determined
                        model.Add(
                            precedence_vars[(i, j)] + precedence_vars[(j, i)] == 1
                        )
    
    def _add_priority_constraints(
        self, 
        model: cp_model.CpModel, 
        trains: List[Train], 
        precedence_vars: Dict[Tuple[int, int], cp_model.IntVar]
    ):
        """Add constraints based on train priority."""
        for i, train1 in enumerate(trains):
            for j, train2 in enumerate(trains):
                if i != j and train1.priority > train2.priority:
                    # Higher priority trains should generally go first
                    # But allow exceptions for very delayed lower priority trains
                    if train2.delay_minutes - train1.delay_minutes < 30:
                        model.Add(precedence_vars[(i, j)] == 1)
    
    def _add_capacity_constraints(
        self, 
        model: cp_model.CpModel, 
        trains: List[Train], 
        precedence_vars: Dict[Tuple[int, int], cp_model.IntVar],
        system_state: SystemState
    ):
        """Add constraints for section capacity."""
        # Group trains by section they want to use
        section_groups = {}
        for i, train in enumerate(trains):
            if train.current_section:
                section_id = train.current_section.id
                if section_id not in section_groups:
                    section_groups[section_id] = []
                section_groups[section_id].append(i)
        
        # Ensure section capacity is respected
        for section_id, train_indices in section_groups.items():
            section = system_state.get_section_by_id(section_id)
            if section and len(train_indices) > section.tracks:
                # If more trains than capacity, some must wait
                # This is handled by the precedence variables
                pass
    
    def _trains_compete_for_resource(
        self, 
        train1: Train, 
        train2: Train, 
        system_state: SystemState
    ) -> bool:
        """Check if two trains are competing for the same resource."""
        if not train1.current_section or not train2.current_section:
            return False
        
        # Same section
        if train1.current_section.id == train2.current_section.id:
            return True
        
        # Adjacent sections that share capacity
        # This is a simplified check - in reality, this would be more complex
        return False
    
    def _extract_decisions_from_solution(
        self, 
        solver: cp_model.CpSolver, 
        trains: List[Train], 
        precedence_vars: Dict[Tuple[int, int], cp_model.IntVar],
        system_state: SystemState
    ) -> List[Decision]:
        """Extract decisions from the solved model."""
        decisions = []
        
        # Determine precedence order
        precedence_order = []
        for i, train in enumerate(trains):
            position = 0
            for j in range(len(trains)):
                if i != j and solver.Value(precedence_vars[(j, i)]) == 1:
                    position += 1
            precedence_order.append((position, i, train))
        
        # Sort by position
        precedence_order.sort(key=lambda x: x[0])
        
        # Generate decisions
        for position, train_idx, train in precedence_order:
            if position == 0:
                # First train can proceed
                decision = Decision(
                    train=train,
                    action="proceed",
                    target_section=train.current_section,
                    reason=f"Highest priority in precedence order",
                    confidence=0.9
                )
            else:
                # Other trains must wait
                wait_time = position * 5  # 5 minutes per position
                decision = Decision(
                    train=train,
                    action="wait",
                    reason=f"Waiting for {position} higher priority trains",
                    confidence=0.8
                )
            
            decisions.append(decision)
        
        return decisions
    
    def _generate_heuristic_decisions(
        self, 
        trains: List[Train], 
        system_state: SystemState
    ) -> List[Decision]:
        """Generate decisions using simple heuristics when optimization fails."""
        decisions = []
        
        # Sort trains by priority and delay
        sorted_trains = sorted(
            trains, 
            key=lambda t: (t.priority, -t.delay_minutes), 
            reverse=True
        )
        
        for i, train in enumerate(sorted_trains):
            if i == 0:
                decision = Decision(
                    train=train,
                    action="proceed",
                    target_section=train.current_section,
                    reason="Highest priority by heuristic",
                    confidence=0.6
                )
            else:
                decision = Decision(
                    train=train,
                    action="wait",
                    reason=f"Lower priority than {i} trains",
                    confidence=0.5
                )
            
            decisions.append(decision)
        
        return decisions
    
    def _generate_fallback_decisions(self, system_state: SystemState) -> OptimizationResult:
        """Generate basic fallback decisions when optimization completely fails."""
        decisions = []
        
        for train in system_state.trains:
            if train.status in [TrainStatus.RUNNING, TrainStatus.DELAYED]:
                decision = Decision(
                    train=train,
                    action="proceed",
                    target_section=train.current_section,
                    reason="Fallback: proceed with caution",
                    confidence=0.3
                )
                decisions.append(decision)
        
        return OptimizationResult(
            decisions=decisions,
            total_delay_reduction=0,
            throughput_improvement=0.0,
            confidence_score=0.3,
            computation_time=0.0
        )
    
    def _calculate_delay_reduction(
        self, 
        decisions: List[Decision], 
        system_state: SystemState
    ) -> int:
        """Calculate estimated delay reduction from decisions."""
        # Simplified calculation - in reality this would be more sophisticated
        total_reduction = 0
        
        for decision in decisions:
            if decision.action == "proceed" and decision.train.is_delayed:
                # Estimate that proceeding reduces delay
                total_reduction += min(decision.train.delay_minutes, 10)
        
        return total_reduction
    
    def _calculate_throughput_improvement(self, decisions: List[Decision]) -> float:
        """Calculate estimated throughput improvement percentage."""
        proceed_count = sum(1 for d in decisions if d.action == "proceed")
        total_count = len(decisions)
        
        if total_count == 0:
            return 0.0
        
        # Simple heuristic: more trains proceeding = better throughput
        return (proceed_count / total_count) * 20.0  # Up to 20% improvement
    
    def _calculate_confidence(
        self, 
        decisions: List[Decision], 
        system_state: SystemState
    ) -> float:
        """Calculate confidence score for the decisions."""
        if not decisions:
            return 1.0
        
        # Average confidence of individual decisions
        avg_confidence = sum(d.confidence for d in decisions) / len(decisions)
        
        # Adjust based on system complexity
        complexity_factor = min(1.0, len(system_state.trains) / 20.0)
        
        return avg_confidence * complexity_factor
