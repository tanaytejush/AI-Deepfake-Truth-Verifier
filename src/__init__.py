"""
AI Deepfake Truth Verifier
Source package
"""

__version__ = "1.0.0"
__author__ = "AI Deepfake Truth Verifier Team"

from .detector import DeepfakeDetector
from .database import DeepfakeDatabase

__all__ = ['DeepfakeDetector', 'DeepfakeDatabase']
