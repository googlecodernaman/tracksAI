"""
Tests for core domain models.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from core.models import (
    Train, Section, Station, TrainType, TrainStatus, 
    SectionStatus, Decision, SystemState
)


class TestStation:
    """Test cases for Station model."""
    
    def test_station_creation(self):
        """Test station creation with required fields."""
        station = Station(
            id=uuid4(),
            name="Mumbai Central",
            code="BCT",
            latitude=19.0176,
            longitude=72.8562,
            platforms=8
        )
        
        assert station.name == "Mumbai Central"
        assert station.code == "BCT"
        assert station.platforms == 8
        assert station.is_junction is False  # default value
    
    def test_station_junction(self):
        """Test station with junction flag."""
        station = Station(
            id=uuid4(),
            name="Delhi Junction",
            code="DLI",
            latitude=28.6139,
            longitude=77.2090,
            platforms=12,
            is_junction=True
        )
        
        assert station.is_junction is True


class TestSection:
    """Test cases for Section model."""
    
    def test_section_creation(self, sample_station):
        """Test section creation."""
        station2 = Station(
            id=uuid4(),
            name="Delhi",
            code="DLI",
            latitude=28.6139,
            longitude=77.2090,
            platforms=12
        )
        
        section = Section(
            id=uuid4(),
            from_station=sample_station,
            to_station=station2,
            length_km=1384.0,
            max_speed_kmh=120,
            tracks=2
        )
        
        assert section.length_km == 1384.0
        assert section.max_speed_kmh == 120
        assert section.tracks == 2
        assert section.status == SectionStatus.AVAILABLE
    
    def test_section_availability(self, sample_section):
        """Test section availability logic."""
        assert sample_section.is_available is True
        
        # Add a train to the section
        train = Train(
            id=uuid4(),
            number="12345",
            name="Test Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400
        )
        sample_section.current_trains.append(train)
        
        # Section should still be available if it has capacity
        assert sample_section.is_available is True
        
        # Add another train to exceed capacity
        train2 = Train(
            id=uuid4(),
            number="12346",
            name="Test Train 2",
            train_type=TrainType.PASSENGER,
            max_speed=80,
            length=300
        )
        sample_section.current_trains.append(train2)
        
        # Now section should not be available
        assert sample_section.is_available is False
    
    def test_section_can_accommodate(self, sample_section):
        """Test if section can accommodate a train."""
        train = Train(
            id=uuid4(),
            number="12345",
            name="Test Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400
        )
        
        assert sample_section.can_accommodate(train) is True
        
        # Test with train exceeding speed limit
        fast_train = Train(
            id=uuid4(),
            number="12346",
            name="Fast Train",
            train_type=TrainType.EXPRESS,
            max_speed=150,  # Exceeds section max speed
            length=400
        )
        
        assert sample_section.can_accommodate(fast_train) is False


class TestTrain:
    """Test cases for Train model."""
    
    def test_train_creation(self):
        """Test train creation."""
        train = Train(
            id=uuid4(),
            number="12345",
            name="Rajdhani Express",
            train_type=TrainType.EXPRESS,
            max_speed=120,
            length=500
        )
        
        assert train.number == "12345"
        assert train.name == "Rajdhani Express"
        assert train.train_type == TrainType.EXPRESS
        assert train.priority == 3  # Express trains have priority 3
        assert train.delay_minutes == 0
    
    def test_train_priority_by_type(self):
        """Test train priority assignment by type."""
        special_train = Train(
            id=uuid4(),
            number="S001",
            name="Special Train",
            train_type=TrainType.SPECIAL,
            max_speed=100,
            length=400
        )
        
        express_train = Train(
            id=uuid4(),
            number="E001",
            name="Express Train",
            train_type=TrainType.EXPRESS,
            max_speed=120,
            length=500
        )
        
        passenger_train = Train(
            id=uuid4(),
            number="P001",
            name="Passenger Train",
            train_type=TrainType.PASSENGER,
            max_speed=80,
            length=300
        )
        
        freight_train = Train(
            id=uuid4(),
            number="F001",
            name="Freight Train",
            train_type=TrainType.FREIGHT,
            max_speed=60,
            length=600
        )
        
        assert special_train.priority == 4  # Highest priority
        assert express_train.priority == 3
        assert passenger_train.priority == 2
        assert freight_train.priority == 1  # Lowest priority
    
    def test_train_delay_detection(self):
        """Test train delay detection."""
        train = Train(
            id=uuid4(),
            number="12345",
            name="Test Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400,
            delay_minutes=15
        )
        
        assert train.is_delayed is True
        assert train.delay_minutes == 15
        
        # Test on-time train
        on_time_train = Train(
            id=uuid4(),
            number="12346",
            name="On Time Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400,
            delay_minutes=0
        )
        
        assert on_time_train.is_delayed is False
    
    def test_estimated_arrival(self):
        """Test estimated arrival calculation."""
        scheduled_arrival = datetime(2024, 1, 1, 10, 0, 0)
        train = Train(
            id=uuid4(),
            number="12345",
            name="Test Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400,
            scheduled_arrival=scheduled_arrival,
            delay_minutes=30
        )
        
        expected_arrival = scheduled_arrival + timedelta(minutes=30)
        assert train.estimated_arrival == expected_arrival
    
    def test_delay_calculation(self):
        """Test delay calculation from actual vs scheduled times."""
        scheduled_departure = datetime(2024, 1, 1, 9, 0, 0)
        actual_departure = datetime(2024, 1, 1, 9, 15, 0)  # 15 minutes late
        
        train = Train(
            id=uuid4(),
            number="12345",
            name="Test Train",
            train_type=TrainType.EXPRESS,
            max_speed=100,
            length=400,
            scheduled_departure=scheduled_departure,
            actual_departure=actual_departure
        )
        
        delay = train.calculate_delay(datetime(2024, 1, 1, 9, 20, 0))
        assert delay == 15


class TestDecision:
    """Test cases for Decision model."""
    
    def test_decision_creation(self, sample_train):
        """Test decision creation."""
        decision = Decision(
            id=uuid4(),
            train=sample_train,
            action="proceed",
            reason="Highest priority",
            confidence=0.9
        )
        
        assert decision.train == sample_train
        assert decision.action == "proceed"
        assert decision.reason == "Highest priority"
        assert decision.confidence == 0.9
        assert decision.applied is False


class TestSystemState:
    """Test cases for SystemState model."""
    
    def test_system_state_creation(self, sample_train, sample_section, sample_station):
        """Test system state creation."""
        state = SystemState(
            timestamp=datetime.utcnow(),
            trains=[sample_train],
            sections=[sample_section],
            stations=[sample_station, sample_section.to_station]
        )
        
        assert len(state.trains) == 1
        assert len(state.sections) == 1
        assert len(state.stations) == 2
    
    def test_system_state_lookup(self, sample_system_state, sample_train, sample_section, sample_station):
        """Test system state lookup methods."""
        # Test train lookup
        found_train = sample_system_state.get_train_by_id(sample_train.id)
        assert found_train == sample_train
        
        # Test section lookup
        found_section = sample_system_state.get_section_by_id(sample_section.id)
        assert found_section == sample_section
        
        # Test station lookup
        found_station = sample_system_state.get_station_by_id(sample_station.id)
        assert found_station == sample_station
        
        # Test non-existent lookups
        non_existent_id = uuid4()
        assert sample_system_state.get_train_by_id(non_existent_id) is None
        assert sample_system_state.get_section_by_id(non_existent_id) is None
        assert sample_system_state.get_station_by_id(non_existent_id) is None
