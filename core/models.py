"""
Core domain models for railway traffic management.

These classes represent the core business entities and contain
pure domain logic without any I/O dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4


class TrainType(Enum):
    """Types of trains with different priorities."""
    EXPRESS = "express"
    PASSENGER = "passenger"
    FREIGHT = "freight"
    SPECIAL = "special"


class TrainStatus(Enum):
    """Current status of a train."""
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    RUNNING = "running"
    STOPPED = "stopped"


class SectionStatus(Enum):
    """Status of a railway section."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    BLOCKED = "blocked"


@dataclass
class Station:
    """Represents a railway station."""
    id: UUID
    name: str
    code: str
    latitude: float
    longitude: float
    platforms: int
    is_junction: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()


@dataclass
class Section:
    """Represents a railway section between two stations."""
    id: UUID
    from_station: Station
    to_station: Station
    length_km: float
    max_speed_kmh: int
    tracks: int
    status: SectionStatus = SectionStatus.AVAILABLE
    current_trains: List['Train'] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()
    
    @property
    def is_available(self) -> bool:
        """Check if section has available capacity."""
        return (self.status == SectionStatus.AVAILABLE and 
                len(self.current_trains) < self.tracks)
    
    def can_accommodate(self, train: 'Train') -> bool:
        """Check if section can accommodate a specific train."""
        return self.is_available and train.max_speed <= self.max_speed_kmh


@dataclass
class Train:
    """Represents a train with its properties and current state."""
    id: UUID
    number: str
    name: str
    train_type: TrainType
    max_speed: int
    length: int  # in meters
    current_section: Optional[Section] = None
    current_station: Optional[Station] = None
    status: TrainStatus = TrainStatus.ON_TIME
    scheduled_departure: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    delay_minutes: int = 0
    priority: int = 1  # Higher number = higher priority
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()
        
        # Set priority based on train type
        priority_map = {
            TrainType.SPECIAL: 4,
            TrainType.EXPRESS: 3,
            TrainType.PASSENGER: 2,
            TrainType.FREIGHT: 1
        }
        self.priority = priority_map.get(self.train_type, 1)
    
    @property
    def is_delayed(self) -> bool:
        """Check if train is currently delayed."""
        return self.delay_minutes > 0
    
    @property
    def estimated_arrival(self) -> Optional[datetime]:
        """Get estimated arrival time considering delays."""
        if self.scheduled_arrival:
            return self.scheduled_arrival + timedelta(minutes=self.delay_minutes)
        return None
    
    def calculate_delay(self, current_time: datetime) -> int:
        """Calculate current delay in minutes."""
        if self.scheduled_departure and self.actual_departure:
            delay = (self.actual_departure - self.scheduled_departure).total_seconds() / 60
            return max(0, int(delay))
        return 0


@dataclass
class Schedule:
    """Represents a train's schedule across multiple stations."""
    id: UUID
    train: Train
    stations: List[Station]
    arrival_times: List[datetime]
    departure_times: List[datetime]
    section_sequence: List[Section]
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()
    
    def get_next_station(self, current_station: Station) -> Optional[Station]:
        """Get the next station in the schedule."""
        try:
            current_index = self.stations.index(current_station)
            if current_index < len(self.stations) - 1:
                return self.stations[current_index + 1]
        except ValueError:
            pass
        return None
    
    def get_section_to_next_station(self, current_station: Station) -> Optional[Section]:
        """Get the section to the next station."""
        next_station = self.get_next_station(current_station)
        if next_station:
            # Find section between current and next station
            for section in self.section_sequence:
                if (section.from_station == current_station and 
                    section.to_station == next_station):
                    return section
        return None


@dataclass
class Decision:
    """Represents a decision made by the system."""
    id: UUID
    train: Train
    action: str  # "proceed", "wait", "reroute", "cross"
    target_section: Optional[Section] = None
    target_station: Optional[Station] = None
    estimated_time: Optional[datetime] = None
    reason: str = ""
    confidence: float = 0.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()


@dataclass
class OptimizationResult:
    """Result of the optimization process."""
    decisions: List[Decision]
    total_delay_reduction: int  # in minutes
    throughput_improvement: float  # percentage
    confidence_score: float  # 0.0 to 1.0
    computation_time: float  # in seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.decisions:
            self.decisions = []


@dataclass
class SystemState:
    """Current state of the railway system."""
    timestamp: datetime
    trains: List[Train]
    sections: List[Section]
    stations: List[Station]
    active_decisions: List[Decision] = field(default_factory=list)
    
    def get_train_by_id(self, train_id: UUID) -> Optional[Train]:
        """Get train by ID."""
        for train in self.trains:
            if train.id == train_id:
                return train
        return None
    
    def get_section_by_id(self, section_id: UUID) -> Optional[Section]:
        """Get section by ID."""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
    
    def get_station_by_id(self, station_id: UUID) -> Optional[Station]:
        """Get station by ID."""
        for station in self.stations:
            if station.id == station_id:
                return station
        return None
