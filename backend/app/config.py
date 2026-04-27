"""
Configuration settings for the application
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI-based Image Authenticity Verification System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False  # Set to True only for development

    # CORS Settings - Add your production domains here
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Model Settings — ensemble of transformers
    MODEL_NAME: str = "umm-maybe/AI-image-detector"  # kept for backward compat
    ENSEMBLE_MODELS: list = [
        "dima806/ai_vs_real_image_detection",         # 98.25% accuracy — AI vs real (ViT)
        "prithivMLmods/Deep-Fake-Detector-v2-Model",  # 92.12% accuracy — updated Feb 2025
        "haywoodsloan/ai-image-detector-deploy",      # Specialized for Midjourney/DALL-E/SD
    ]
    # Explicit label index overrides — removes ambiguity in label mapping
    # Format: model_name -> {real_idx, fake_idx}
    MODEL_LABEL_OVERRIDES: dict = {
        "dima806/ai_vs_real_image_detection":       {"real_idx": 0, "fake_idx": 1},
        "prithivMLmods/Deep-Fake-Detector-v2-Model":{"real_idx": 0, "fake_idx": 1},
        "haywoodsloan/ai-image-detector-deploy":    {"real_idx": 1, "fake_idx": 0},
        "umm-maybe/AI-image-detector":              {"real_idx": 1, "fake_idx": 0},
        "dima806/deepfake_vs_real_image_detection": {"real_idx": 0, "fake_idx": 1},
        "Wvolf/ViT_Deepfake_Detection":             {"real_idx": 0, "fake_idx": 1},
        "prithivMLmods/Deep-Fake-Detector-Model":   {"real_idx": 1, "fake_idx": 0},
        "Organika/sdxl-detector":                   {"real_idx": 1, "fake_idx": 0},
    }
    MODEL_CACHE_DIR: str = "./models/cache"
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_EXTENSIONS: set = {"jpg", "jpeg", "png"}
    ALLOWED_VIDEO_EXTENSIONS: set = {"mp4", "avi", "mov", "mkv"}
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "mp4", "avi", "mov", "mkv"}

    # Video Processing Settings
    VIDEO_FRAME_SAMPLE_RATE: int = 30  # Extract 1 frame every 30 frames
    VIDEO_MAX_FRAMES: int = 100  # Maximum frames to analyze per video
    VIDEO_PREDICTION_THRESHOLD: float = 0.55  # Confidence threshold for aggregation

    # Disagreement handling
    DISAGREEMENT_MINORITY_VOTE_RATIO: float = 0.75
    DISAGREEMENT_NEAR_THRESHOLD_MARGIN: float = 15.0
    DISAGREEMENT_STRONG_OPPOSITION_THRESHOLD: float = 90.0

    # File Upload Settings
    UPLOAD_DIR: Path = Path("./uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Database Settings
    DATABASE_URL: str = "sqlite:///./deepfake_detector.db"

    # Model Optimization
    USE_GPU: bool = True  # Will auto-detect MPS for M1
    BATCH_SIZE: int = 1
    NUM_WORKERS: int = 2

    # Caching
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 1 hour

    # Performance
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 30  # seconds

    # Security
    ADMIN_CLEAR_TOKEN: str = ""
    ADMIN_CLEAR_TOKENS: List[str] = []
    ADMIN_AUTH_MODE: str = "token"  # token | jwt | hybrid
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ADMIN_JWT_ALLOWED_ROLES: List[str] = ["admin"]

    # Rate limiting (per client IP per endpoint)
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_IMAGE_PER_WINDOW: int = 20
    RATE_LIMIT_VIDEO_PER_WINDOW: int = 5
    RATE_LIMIT_BACKEND: str = "memory"  # memory | redis
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
