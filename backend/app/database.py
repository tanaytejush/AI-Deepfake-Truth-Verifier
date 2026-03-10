"""
Database models and connection
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # For SQLite
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()


class Prediction(Base):
    """Prediction model"""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_name = Column(String, nullable=False)
    prediction = Column(String, nullable=False)  # REAL or FAKE
    confidence = Column(Float, nullable=False)
    real_probability = Column(Float)
    fake_probability = Column(Float)
    inference_time = Column(Float)
    device = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Prediction {self.image_name}: {self.prediction} ({self.confidence}%)>"


# Create tables
def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)


# Dependency for FastAPI
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
