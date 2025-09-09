"""
Database models and repository interfaces for the railway system.

This module defines the database schema and repository interfaces
following the architecture guidelines for clean separation of concerns.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import enum

from .models import Train, Section, Station, Decision, SystemState, TrainType, TrainStatus, SectionStatus

Base = declarative_base()


class TrainTypeEnum(enum.Enum):
    """Database enum for train types."""
    EXPRESS = "express"
    PASSENGER = "passenger"
    FREIGHT = "freight"
    SPECIAL = "special"


class TrainStatusEnum(enum.Enum):
    """Database enum for train status."""
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    RUNNING = "running"
    STOPPED = "stopped"


class SectionStatusEnum(enum.Enum):
    """Database enum for section status."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    BLOCKED = "blocked"


class StationModel(Base):
    """Database model for stations."""
    __tablename__ = "stations"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    platforms = Column(Integer, nullable=False, default=1)
    is_junction = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_sections = relationship("SectionModel", foreign_keys="SectionModel.from_station_id", back_populates="from_station")
    to_sections = relationship("SectionModel", foreign_keys="SectionModel.to_station_id", back_populates="to_station")


class SectionModel(Base):
    """Database model for railway sections."""
    __tablename__ = "sections"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    from_station_id = Column(PostgresUUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    to_station_id = Column(PostgresUUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    length_km = Column(Float, nullable=False)
    max_speed_kmh = Column(Integer, nullable=False)
    tracks = Column(Integer, nullable=False, default=1)
    status = Column(SQLEnum(SectionStatusEnum), default=SectionStatusEnum.AVAILABLE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_station = relationship("StationModel", foreign_keys=[from_station_id], back_populates="from_sections")
    to_station = relationship("StationModel", foreign_keys=[to_station_id], back_populates="to_sections")


class TrainModel(Base):
    """Database model for trains."""
    __tablename__ = "trains"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    number = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    train_type = Column(SQLEnum(TrainTypeEnum), nullable=False)
    max_speed = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)  # in meters
    current_section_id = Column(PostgresUUID(as_uuid=True), ForeignKey("sections.id"), nullable=True)
    current_station_id = Column(PostgresUUID(as_uuid=True), ForeignKey("stations.id"), nullable=True)
    status = Column(SQLEnum(TrainStatusEnum), default=TrainStatusEnum.ON_TIME)
    scheduled_departure = Column(DateTime, nullable=True)
    actual_departure = Column(DateTime, nullable=True)
    scheduled_arrival = Column(DateTime, nullable=True)
    actual_arrival = Column(DateTime, nullable=True)
    delay_minutes = Column(Integer, default=0)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    current_section = relationship("SectionModel", foreign_keys=[current_section_id])
    current_station = relationship("StationModel", foreign_keys=[current_station_id])


class DecisionModel(Base):
    """Database model for decisions."""
    __tablename__ = "decisions"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    train_id = Column(PostgresUUID(as_uuid=True), ForeignKey("trains.id"), nullable=False)
    action = Column(String(50), nullable=False)
    target_section_id = Column(PostgresUUID(as_uuid=True), ForeignKey("sections.id"), nullable=True)
    target_station_id = Column(PostgresUUID(as_uuid=True), ForeignKey("stations.id"), nullable=True)
    estimated_time = Column(DateTime, nullable=True)
    reason = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False, default=0.0)
    applied = Column(Boolean, default=False)
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    train = relationship("TrainModel")
    target_section = relationship("SectionModel", foreign_keys=[target_section_id])
    target_station = relationship("StationModel", foreign_keys=[target_station_id])


class SystemStateModel(Base):
    """Database model for system state snapshots."""
    __tablename__ = "system_states"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    state_data = Column(Text, nullable=False)  # JSON serialized state
    optimization_result = Column(Text, nullable=True)  # JSON serialized result
    created_at = Column(DateTime, default=datetime.utcnow)


# Repository Interfaces (following clean architecture)

class StationRepository(ABC):
    """Abstract repository for station operations."""
    
    @abstractmethod
    def get_by_id(self, station_id: UUID) -> Optional[Station]:
        """Get station by ID."""
        pass
    
    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Station]:
        """Get station by code."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Station]:
        """Get all stations."""
        pass
    
    @abstractmethod
    def create(self, station: Station) -> Station:
        """Create a new station."""
        pass
    
    @abstractmethod
    def update(self, station: Station) -> Station:
        """Update an existing station."""
        pass


class SectionRepository(ABC):
    """Abstract repository for section operations."""
    
    @abstractmethod
    def get_by_id(self, section_id: UUID) -> Optional[Section]:
        """Get section by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Section]:
        """Get all sections."""
        pass
    
    @abstractmethod
    def get_by_stations(self, from_station_id: UUID, to_station_id: UUID) -> Optional[Section]:
        """Get section between two stations."""
        pass
    
    @abstractmethod
    def create(self, section: Section) -> Section:
        """Create a new section."""
        pass
    
    @abstractmethod
    def update(self, section: Section) -> Section:
        """Update an existing section."""
        pass


class TrainRepository(ABC):
    """Abstract repository for train operations."""
    
    @abstractmethod
    def get_by_id(self, train_id: UUID) -> Optional[Train]:
        """Get train by ID."""
        pass
    
    @abstractmethod
    def get_by_number(self, number: str) -> Optional[Train]:
        """Get train by number."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Train]:
        """Get all trains."""
        pass
    
    @abstractmethod
    def get_active_trains(self) -> List[Train]:
        """Get currently active trains."""
        pass
    
    @abstractmethod
    def create(self, train: Train) -> Train:
        """Create a new train."""
        pass
    
    @abstractmethod
    def update(self, train: Train) -> Train:
        """Update an existing train."""
        pass


class DecisionRepository(ABC):
    """Abstract repository for decision operations."""
    
    @abstractmethod
    def get_by_id(self, decision_id: UUID) -> Optional[Decision]:
        """Get decision by ID."""
        pass
    
    @abstractmethod
    def get_by_train(self, train_id: UUID) -> List[Decision]:
        """Get decisions for a specific train."""
        pass
    
    @abstractmethod
    def get_pending_decisions(self) -> List[Decision]:
        """Get decisions that haven't been applied yet."""
        pass
    
    @abstractmethod
    def create(self, decision: Decision) -> Decision:
        """Create a new decision."""
        pass
    
    @abstractmethod
    def mark_applied(self, decision_id: UUID) -> bool:
        """Mark a decision as applied."""
        pass


class SystemStateRepository(ABC):
    """Abstract repository for system state operations."""
    
    @abstractmethod
    def save_state(self, state: SystemState) -> UUID:
        """Save system state snapshot."""
        pass
    
    @abstractmethod
    def get_latest_state(self) -> Optional[SystemState]:
        """Get the latest system state."""
        pass
    
    @abstractmethod
    def get_states_by_time_range(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[SystemState]:
        """Get system states within a time range."""
        pass


# Database Configuration

class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close database connections."""
        self.engine.dispose()
