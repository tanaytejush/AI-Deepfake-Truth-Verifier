"""
API Endpoint Tests for Deepfake Detector Backend
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_returns_200(self, client):
        """Test root endpoint returns 200"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_root_returns_correct_data(self, client):
        """Test root endpoint returns expected data"""
        response = client.get("/")
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "online"

    def test_root_includes_request_id_header(self, client):
        """Test middleware adds request ID header"""
        response = client.get("/")
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"]

    def test_root_preserves_incoming_request_id(self, client):
        """Test middleware reuses caller-provided request ID"""
        response = client.get("/", headers={"X-Request-ID": "test-request-id"})
        assert response.headers.get("X-Request-ID") == "test-request-id"


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_returns_200(self, client):
        """Test health endpoint returns 200"""
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK

    def test_health_returns_healthy_status(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get("/api/v1/health")
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "api"
        assert "timestamp" in data


class TestReadinessEndpoint:
    """Tests for readiness endpoint"""

    def test_ready_returns_200(self, client):
        """Test readiness endpoint returns 200"""
        response = client.get("/api/v1/ready")
        assert response.status_code == status.HTTP_200_OK

    def test_ready_returns_expected_fields(self, client):
        """Test readiness endpoint returns expected fields"""
        response = client.get("/api/v1/ready")
        data = response.json()

        assert data["status"] == "ready"
        assert data["model_loaded"] is True
        assert "device" in data
        assert "timestamp" in data


class TestModelInfoEndpoint:
    """Tests for model info endpoint"""

    def test_model_info_returns_200(self, client):
        """Test model info endpoint returns 200"""
        response = client.get("/api/v1/model/info")
        assert response.status_code == status.HTTP_200_OK

    def test_model_info_contains_required_fields(self, client):
        """Test model info contains required fields"""
        response = client.get("/api/v1/model/info")
        data = response.json()

        assert "model_name" in data or "is_loaded" in data
        assert "device" in data


class TestImagePrediction:
    """Tests for image prediction endpoint"""

    def test_predict_accepts_jpeg(self, client, sample_image):
        """Test prediction endpoint accepts JPEG images"""
        response = client.post(
            "/api/v1/predict",
            files={"file": ("test.jpg", sample_image, "image/jpeg")}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_predict_accepts_png(self, client, sample_image_png):
        """Test prediction endpoint accepts PNG images"""
        response = client.post(
            "/api/v1/predict",
            files={"file": ("test.png", sample_image_png, "image/png")}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_predict_returns_required_fields(self, client, sample_image):
        """Test prediction returns all required fields"""
        response = client.post(
            "/api/v1/predict",
            files={"file": ("test.jpg", sample_image, "image/jpeg")}
        )
        data = response.json()

        assert "prediction" in data
        assert "confidence" in data
        assert "real_probability" in data
        assert "fake_probability" in data
        assert data["prediction"] in ["REAL", "FAKE"]

    def test_predict_confidence_range(self, client, sample_image):
        """Test prediction confidence is in valid range"""
        response = client.post(
            "/api/v1/predict",
            files={"file": ("test.jpg", sample_image, "image/jpeg")}
        )
        data = response.json()

        assert 0 <= data["confidence"] <= 100
        assert 0 <= data["real_probability"] <= 100
        assert 0 <= data["fake_probability"] <= 100

    def test_predict_rejects_invalid_extension(self, client, invalid_file):
        """Test prediction rejects invalid file extensions"""
        response = client.post(
            "/api/v1/predict",
            files={"file": ("test.txt", invalid_file, "text/plain")}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_predict_rejects_gif(self, client, sample_image):
        """Test prediction rejects GIF files"""
        response = client.post(
            "/api/v1/predict",
            files={"file": ("test.gif", sample_image, "image/gif")}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestStatistics:
    """Tests for statistics endpoint"""

    def test_statistics_returns_200(self, client):
        """Test statistics endpoint returns 200"""
        response = client.get("/api/v1/statistics")
        assert response.status_code == status.HTTP_200_OK

    def test_statistics_returns_required_fields(self, client):
        """Test statistics returns all required fields"""
        response = client.get("/api/v1/statistics")
        data = response.json()

        assert "total_predictions" in data
        assert "real_count" in data
        assert "fake_count" in data
        assert "average_confidence" in data

    def test_statistics_initial_values(self, client):
        """Test statistics initial values are zero or valid"""
        response = client.get("/api/v1/statistics")
        data = response.json()

        assert data["total_predictions"] >= 0
        assert data["real_count"] >= 0
        assert data["fake_count"] >= 0


class TestRecentPredictions:
    """Tests for recent predictions endpoint"""

    def test_recent_predictions_returns_200(self, client):
        """Test recent predictions endpoint returns 200"""
        response = client.get("/api/v1/predictions/recent")
        assert response.status_code == status.HTTP_200_OK

    def test_recent_predictions_returns_list(self, client):
        """Test recent predictions returns a list"""
        response = client.get("/api/v1/predictions/recent")
        data = response.json()

        assert "predictions" in data
        assert isinstance(data["predictions"], list)

    def test_recent_predictions_respects_limit(self, client, sample_image):
        """Test recent predictions respects limit parameter"""
        # Make a prediction first
        client.post(
            "/api/v1/predict",
            files={"file": ("test.jpg", sample_image, "image/jpeg")}
        )

        response = client.get("/api/v1/predictions/recent?limit=5")
        data = response.json()

        assert len(data["predictions"]) <= 5


class TestClearPredictions:
    """Tests for clear predictions endpoint"""

    def test_clear_predictions_returns_200(self, client):
        """Test clear predictions endpoint returns 200"""
        response = client.delete(
            "/api/v1/predictions/clear",
            headers={"X-Admin-Token": "test-clear-token"},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_clear_predictions_returns_count(self, client):
        """Test clear predictions returns deleted count"""
        response = client.delete(
            "/api/v1/predictions/clear",
            headers={"X-Admin-Token": "test-clear-token"},
        )
        data = response.json()

        assert "deleted_count" in data
        assert data["deleted_count"] >= 0

    def test_clear_predictions_requires_token(self, client):
        """Test clear predictions endpoint enforces admin token"""
        response = client.delete("/api/v1/predictions/clear")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestIntegration:
    """Integration tests for prediction workflow"""

    def test_prediction_appears_in_recent(self, client, sample_image):
        """Test that a prediction appears in recent predictions"""
        # Make a prediction
        predict_response = client.post(
            "/api/v1/predict",
            files={"file": ("test.jpg", sample_image, "image/jpeg")}
        )
        assert predict_response.status_code == status.HTTP_200_OK

        # Check recent predictions
        recent_response = client.get("/api/v1/predictions/recent")
        data = recent_response.json()

        assert len(data["predictions"]) > 0

    def test_prediction_updates_statistics(self, client, sample_image):
        """Test that a prediction updates statistics"""
        # Get initial stats
        initial_stats = client.get("/api/v1/statistics").json()
        initial_total = initial_stats["total_predictions"]

        # Make a prediction
        client.post(
            "/api/v1/predict",
            files={"file": ("test.jpg", sample_image, "image/jpeg")}
        )

        # Check updated stats
        updated_stats = client.get("/api/v1/statistics").json()

        assert updated_stats["total_predictions"] == initial_total + 1

    def test_clear_resets_statistics(self, client, sample_image):
        """Test that clearing predictions resets statistics"""
        # Make a prediction
        client.post(
            "/api/v1/predict",
            files={"file": ("test.jpg", sample_image, "image/jpeg")}
        )

        # Clear predictions
        client.delete(
            "/api/v1/predictions/clear",
            headers={"X-Admin-Token": "test-clear-token"},
        )

        # Check stats are reset
        stats = client.get("/api/v1/statistics").json()

        assert stats["total_predictions"] == 0
        assert stats["real_count"] == 0
        assert stats["fake_count"] == 0
