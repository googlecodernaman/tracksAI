"""
Pytest configuration and fixtures for the test suite.
"""

import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from core.models import Train, Section, Station, TrainType, TrainStatus, SectionStatus
from core.optimizer import RailwayOptimizer
from core.database import Base
from api.main import app


@pytest.fixture
def test_db():
    """Create a test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_station():
    """Create a sample station for testing."""
    return Station(
        id=uuid4(),
        name="Test Station",
        code="TST",
        latitude=19.0176,
        longitude=72.8562,
        platforms=4,
        is_junction=False
    )


@pytest.fixture
def sample_section(sample_station):
    """Create a sample section for testing."""
    station2 = Station(
        id=uuid4(),
        name="Test Station 2",
        code="TS2",
        latitude=19.0276,
        longitude=72.8662,
        platforms=2,
        is_junction=False
    )
    
    return Section(
        id=uuid4(),
        from_station=sample_station,
        to_station=station2,
        length_km=10.0,
        max_speed_kmh=80,
        tracks=1,
        status=SectionStatus.AVAILABLE
    )


@pytest.fixture
def sample_train(sample_section):
    """Create a sample train for testing."""
    return Train(
        id=uuid4(),
        number="12345",
        name="Test Express",
        train_type=TrainType.EXPRESS,
        max_speed=100,
        length=400,
        current_section=sample_section,
        status=TrainStatus.RUNNING,
        delay_minutes=5
    )


@pytest.fixture
def sample_system_state(sample_train, sample_section, sample_station):
    """Create a sample system state for testing."""
    from core.models import SystemState
    
    return SystemState(
        timestamp=datetime.utcnow(),
        trains=[sample_train],
        sections=[sample_section],
        stations=[sample_station, sample_section.to_station]
    )


@pytest.fixture
def optimizer():
    """Create an optimizer instance for testing."""
    return RailwayOptimizer(time_limit_seconds=5)
