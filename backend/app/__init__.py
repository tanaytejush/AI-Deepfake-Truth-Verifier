"""
AI Deepfake Truth Verifier - Backend API
"""

__version__ = "1.0.0"

from .database import init_db

# Initialize database on import
init_db()
