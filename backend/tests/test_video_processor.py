"""
Video Processor Tests for Deepfake Detector Backend
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image


class TestVideoProcessorAggregation:
    """Tests for video prediction aggregation methods"""

    @pytest.fixture
    def video_processor(self):
        """Create a VideoProcessor instance"""
        from app.video_processor import VideoProcessor
        return VideoProcessor(frame_sample_rate=30, max_frames=100)

    @pytest.fixture
    def sample_predictions(self):
        """Sample frame predictions for testing aggregation"""
        return [
            {"prediction": "FAKE", "confidence": 0.9, "real_probability": 0.1, "fake_probability": 0.9},
            {"prediction": "FAKE", "confidence": 0.85, "real_probability": 0.15, "fake_probability": 0.85},
            {"prediction": "REAL", "confidence": 0.7, "real_probability": 0.7, "fake_probability": 0.3},
            {"prediction": "FAKE", "confidence": 0.95, "real_probability": 0.05, "fake_probability": 0.95},
            {"prediction": "FAKE", "confidence": 0.8, "real_probability": 0.2, "fake_probability": 0.8},
        ]

    @pytest.fixture
    def balanced_predictions(self):
        """Balanced predictions for edge case testing"""
        return [
            {"prediction": "FAKE", "confidence": 0.9, "real_probability": 0.1, "fake_probability": 0.9},
            {"prediction": "FAKE", "confidence": 0.85, "real_probability": 0.15, "fake_probability": 0.85},
            {"prediction": "REAL", "confidence": 0.9, "real_probability": 0.9, "fake_probability": 0.1},
            {"prediction": "REAL", "confidence": 0.85, "real_probability": 0.85, "fake_probability": 0.15},
        ]

    def test_majority_vote_aggregation(self, video_processor, sample_predictions):
        """Test majority vote aggregation method"""
        result = video_processor.aggregate_predictions(
            sample_predictions,
            method="majority_vote"
        )

        assert result["prediction"] == "FAKE"  # 4 FAKE vs 1 REAL
        assert "confidence" in result
        assert "frames_analyzed" in result
        assert result["frames_analyzed"] == 5

    def test_confidence_weighted_aggregation(self, video_processor, sample_predictions):
        """Test confidence weighted aggregation method"""
        result = video_processor.aggregate_predictions(
            sample_predictions,
            method="confidence_weighted"
        )

        assert result["prediction"] in ["REAL", "FAKE"]
        assert 0 <= result["confidence"] <= 100
        assert "real_probability" in result
        assert "fake_probability" in result

    def test_aggregation_returns_required_fields(self, video_processor, sample_predictions):
        """Test aggregation returns all required fields"""
        result = video_processor.aggregate_predictions(sample_predictions)

        required_fields = [
            "prediction",
            "confidence",
            "real_probability",
            "fake_probability",
            "frames_analyzed",
            "real_frames",
            "fake_frames",
            "aggregation_method"
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_empty_predictions_handling(self, video_processor):
        """Test handling of empty predictions list"""
        with pytest.raises(Exception):
            video_processor.aggregate_predictions([])

    def test_single_prediction_handling(self, video_processor):
        """Test handling of single prediction"""
        single_pred = [
            {"prediction": "REAL", "confidence": 0.95, "real_probability": 0.95, "fake_probability": 0.05}
        ]

        result = video_processor.aggregate_predictions(single_pred)

        assert result["prediction"] == "REAL"
        assert result["frames_analyzed"] == 1


class TestVideoProcessorFrameExtraction:
    """Tests for video frame extraction"""

    @pytest.fixture
    def video_processor(self):
        """Create a VideoProcessor instance"""
        from app.video_processor import VideoProcessor
        return VideoProcessor(frame_sample_rate=30, max_frames=10)

    def test_frame_sample_rate_setting(self, video_processor):
        """Test frame sample rate is set correctly"""
        assert video_processor.frame_sample_rate == 30

    def test_max_frames_setting(self, video_processor):
        """Test max frames is set correctly"""
        assert video_processor.max_frames == 10


class TestTempFileHandling:
    """Tests for temporary file handling"""

    def test_save_upload_creates_file(self):
        """Test save_upload_to_temp creates a file"""
        from app.video_processor import save_upload_to_temp, cleanup_temp_file

        content = b"test content"
        temp_path = save_upload_to_temp(content, ".mp4")

        assert temp_path is not None
        assert temp_path.endswith(".mp4")

        # Cleanup
        cleanup_temp_file(temp_path)

    def test_cleanup_removes_file(self):
        """Test cleanup_temp_file removes the file"""
        from app.video_processor import save_upload_to_temp, cleanup_temp_file
        import os

        content = b"test content"
        temp_path = save_upload_to_temp(content, ".mp4")

        cleanup_temp_file(temp_path)

        assert not os.path.exists(temp_path)

    def test_cleanup_handles_nonexistent_file(self):
        """Test cleanup handles nonexistent file gracefully"""
        from app.video_processor import cleanup_temp_file

        # Should not raise an exception
        cleanup_temp_file("/nonexistent/path/file.mp4")
