"""
Pytest configuration and fixtures for backend tests
"""

import pytest
import os
import sys
from pathlib import Path
from PIL import Image
import io
import tempfile

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
import app.main as app_main


# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class MockModel:
    """Lightweight model stub for API tests."""

    def warm_up(self):
        return None

    def clear_cache(self):
        return None

    def get_model_info(self):
        return {
            "model_name": "Ensemble",
            "ensemble_models": ["mock/model"],
            "ensemble_size": 1,
            "is_fine_tuned": False,
            "device": "cpu",
            "is_loaded": True,
            "cache_dir": "./models/cache",
        }

    def predict(self, image):
        return {
            "prediction": "REAL",
            "confidence": 98.0,
            "real_probability": 98.0,
            "fake_probability": 2.0,
            "fake_type": None,
            "fake_type_detail": None,
            "fake_tags": [],
            "inference_time": 0.01,
            "device": "cpu",
            "ensemble_size": 1,
            "models_used": ["mock/model"],
            "per_model": [
                {
                    "model": "mock-model",
                    "full_model": "mock/model",
                    "fake_prob": 2.0,
                    "real_prob": 98.0,
                    "specialty": "Detection Model",
                }
            ],
        }


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    """Create a test client with database override"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    app_main.rate_limiter.reset()

    monkeypatch.setattr(app_main, "get_model", lambda: MockModel())
    app_main.settings.ADMIN_CLEAR_TOKEN = "test-clear-token"
    app_main.settings.RATE_LIMIT_IMAGE_PER_WINDOW = 1000
    app_main.settings.RATE_LIMIT_VIDEO_PER_WINDOW = 1000

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_image():
    """Create a sample test image"""
    img = Image.new('RGB', (224, 224), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr


@pytest.fixture
def sample_image_png():
    """Create a sample PNG test image"""
    img = Image.new('RGB', (224, 224), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


@pytest.fixture
def large_image():
    """Create a large image that exceeds size limits"""
    # Create a large image (larger than 10MB when saved)
    img = Image.new('RGB', (5000, 5000), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


@pytest.fixture
def invalid_file():
    """Create an invalid file (not an image)"""
    return io.BytesIO(b"This is not an image file")


@pytest.fixture
def sample_video_path():
    """Create a minimal valid video file for testing"""
    # Create a temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "test_video.mp4")

    # Create a minimal valid MP4 file (just header)
    # For actual testing, you might want to use a real small video
    # This is a placeholder that won't work for full video processing
    # but can be used for file validation tests

    yield video_path

    # Cleanup
    if os.path.exists(video_path):
        os.remove(video_path)
    os.rmdir(temp_dir)
