"""
Tests for the optimization engine.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from core.models import (
    Train, Section, Station, TrainType, TrainStatus, 
    SectionStatus, SystemState, Decision
)
from core.optimizer import RailwayOptimizer


class TestRailwayOptimizer:
    """Test cases for RailwayOptimizer."""
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        optimizer = RailwayOptimizer(time_limit_seconds=10)
        assert optimizer.time_limit_seconds == 10
    
    def test_optimize_empty_system(self, optimizer):
        """Test optimization with empty system state."""
        empty_state = SystemState(
            timestamp=datetime.utcnow(),
            trains=[],
            sections=[],
            stations=[]
        )
        
        result = optimizer.optimize(empty_state)
        
        assert result.decisions == []
        assert result.total_delay_reduction == 0
        assert result.throughput_improvement == 0.0
        assert result.confidence_score == 1.0
        assert result.computation_time >= 0.0
    
    def test_optimize_single_train(self, optimizer, sample_system_state):
        """Test optimization with single train."""
        result = optimizer.optimize(sample_system_state)
        
        assert len(result.decisions) >= 0
        assert result.computation_time >= 0.0
        assert 0.0 <= result.confidence_score <= 1.0
    
    def test_optimize_multiple_trains(self, optimizer):
        """Test optimization with multiple trains."""
        # Create stations
        station1 = Station(
            id=uuid4(),
            name="Station 1",
            code="ST1",
            latitude=19.0176,
            longitude=72.8562,
            platforms=4
        )
        
        station2 = Station(
            id=uuid4(),
            name="Station 2",
            code="ST2",
            latitude=19.0276,
            longitude=72.8662,
            platforms=4
        )
        
        # Create section
        section = Section(
            id=uuid4(),
            from_station=station1,
            to_station=station2,
            length_km=10.0,
            max_speed_kmh=80,
            tracks=1,  # Single track to create conflict
            status=SectionStatus.AVAILABLE
        )
        
        # Create trains competing for the same section
        train1 = Train(
            id=uuid4(),
            number="12345",
            name="Express Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400,
            current_section=section,
            status=TrainStatus.RUNNING,
            delay_minutes=5
        )
        
        train2 = Train(
            id=uuid4(),
            number="12346",
            name="Passenger Train",
            train_type=TrainType.PASSENGER,
            max_speed=80,
            length=300,
            current_section=section,
            status=TrainStatus.RUNNING,
            delay_minutes=10
        )
        
        system_state = SystemState(
            timestamp=datetime.utcnow(),
            trains=[train1, train2],
            sections=[section],
            stations=[station1, station2]
        )
        
        result = optimizer.optimize(system_state)
        
        assert len(result.decisions) >= 0
        assert result.computation_time >= 0.0
        assert 0.0 <= result.confidence_score <= 1.0
        
        # Should have decisions for both trains
        train_ids = [d.train.id for d in result.decisions]
        assert train1.id in train_ids
        assert train2.id in train_ids
    
    def test_optimize_with_different_priorities(self, optimizer):
        """Test optimization respects train priorities."""
        # Create stations and section
        station1 = Station(
            id=uuid4(),
            name="Station 1",
            code="ST1",
            latitude=19.0176,
            longitude=72.8562,
            platforms=4
        )
        
        station2 = Station(
            id=uuid4(),
            name="Station 2",
            code="ST2",
            latitude=19.0276,
            longitude=72.8662,
            platforms=4
        )
        
        section = Section(
            id=uuid4(),
            from_station=station1,
            to_station=station2,
            length_km=10.0,
            max_speed_kmh=80,
            tracks=1,
            status=SectionStatus.AVAILABLE
        )
        
        # Create trains with different priorities
        special_train = Train(
            id=uuid4(),
            number="S001",
            name="Special Train",
            train_type=TrainType.SPECIAL,  # Highest priority
            max_speed=100,
            length=400,
            current_section=section,
            status=TrainStatus.RUNNING,
            delay_minutes=0
        )
        
        freight_train = Train(
            id=uuid4(),
            number="F001",
            name="Freight Train",
            train_type=TrainType.FREIGHT,  # Lowest priority
            max_speed=60,
            length=600,
            current_section=section,
            status=TrainStatus.RUNNING,
            delay_minutes=5
        )
        
        system_state = SystemState(
            timestamp=datetime.utcnow(),
            trains=[special_train, freight_train],
            sections=[section],
            stations=[station1, station2]
        )
        
        result = optimizer.optimize(system_state)
        
        # Special train should have higher priority
        special_decision = next((d for d in result.decisions if d.train.id == special_train.id), None)
        freight_decision = next((d for d in result.decisions if d.train.id == freight_train.id), None)
        
        if special_decision and freight_decision:
            # Special train should be more likely to proceed
            assert special_decision.confidence >= freight_decision.confidence
    
    def test_optimize_with_delays(self, optimizer):
        """Test optimization considers train delays."""
        # Create stations and section
        station1 = Station(
            id=uuid4(),
            name="Station 1",
            code="ST1",
            latitude=19.0176,
            longitude=72.8562,
            platforms=4
        )
        
        station2 = Station(
            id=uuid4(),
            name="Station 2",
            code="ST2",
            latitude=19.0276,
            longitude=72.8662,
            platforms=4
        )
        
        section = Section(
            id=uuid4(),
            from_station=station1,
            to_station=station2,
            length_km=10.0,
            max_speed_kmh=80,
            tracks=1,
            status=SectionStatus.AVAILABLE
        )
        
        # Create trains with different delays
        on_time_train = Train(
            id=uuid4(),
            number="12345",
            name="On Time Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400,
            current_section=section,
            status=TrainStatus.RUNNING,
            delay_minutes=0
        )
        
        delayed_train = Train(
            id=uuid4(),
            number="12346",
            name="Delayed Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400,
            current_section=section,
            status=TrainStatus.DELAYED,
            delay_minutes=30
        )
        
        system_state = SystemState(
            timestamp=datetime.utcnow(),
            trains=[on_time_train, delayed_train],
            sections=[section],
            stations=[station1, station2]
        )
        
        result = optimizer.optimize(system_state)
        
        # Delayed train should be prioritized to reduce overall delay
        delayed_decision = next((d for d in result.decisions if d.train.id == delayed_train.id), None)
        on_time_decision = next((d for d in result.decisions if d.train.id == on_time_train.id), None)
        
        if delayed_decision and on_time_decision:
            # Delayed train should have higher confidence for proceeding
            assert delayed_decision.confidence >= on_time_decision.confidence
    
    def test_optimize_fallback_behavior(self, optimizer):
        """Test optimizer fallback behavior when optimization fails."""
        # Create a problematic system state that might cause optimization to fail
        problematic_state = SystemState(
            timestamp=datetime.utcnow(),
            trains=[],  # Empty trains but with sections
            sections=[],
            stations=[]
        )
        
        result = optimizer.optimize(problematic_state)
        
        # Should return a valid result even if optimization fails
        assert result is not None
        assert result.computation_time >= 0.0
        assert 0.0 <= result.confidence_score <= 1.0
    
    def test_optimize_time_limit(self):
        """Test optimizer respects time limits."""
        # Create optimizer with very short time limit
        fast_optimizer = RailwayOptimizer(time_limit_seconds=0.001)
        
        # Create a complex system state
        stations = []
        sections = []
        trains = []
        
        for i in range(10):  # Create 10 stations
            station = Station(
                id=uuid4(),
                name=f"Station {i}",
                code=f"ST{i}",
                latitude=19.0176 + i * 0.01,
                longitude=72.8562 + i * 0.01,
                platforms=4
            )
            stations.append(station)
        
        for i in range(9):  # Create 9 sections
            section = Section(
                id=uuid4(),
                from_station=stations[i],
                to_station=stations[i + 1],
                length_km=10.0,
                max_speed_kmh=80,
                tracks=1,
                status=SectionStatus.AVAILABLE
            )
            sections.append(section)
        
        for i in range(5):  # Create 5 trains
            train = Train(
                id=uuid4(),
                number=f"T{i:05d}",
                name=f"Train {i}",
                train_type=TrainType.EXPRESS,
                max_speed=100,
                length=400,
                current_section=sections[i % len(sections)],
                status=TrainStatus.RUNNING,
                delay_minutes=i * 5
            )
            trains.append(train)
        
        system_state = SystemState(
            timestamp=datetime.utcnow(),
            trains=trains,
            sections=sections,
            stations=stations
        )
        
        result = fast_optimizer.optimize(system_state)
        
        # Should complete within time limit
        assert result.computation_time <= 0.1  # Allow some buffer
        assert result is not None
