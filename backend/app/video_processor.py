"""
Video Processing Utilities for Deepfake Detection
Handles frame extraction and video-level prediction aggregation
"""

import cv2
import numpy as np
from PIL import Image
import tempfile
import os
import logging
from typing import List, Dict, Tuple
from pathlib import Path
from .config import settings

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Process videos for deepfake detection"""

    def __init__(self, frame_sample_rate: int = 30, max_frames: int = 100):
        """
        Initialize video processor

        Args:
            frame_sample_rate: Extract 1 frame every N frames
            max_frames: Maximum frames to analyze
        """
        self.frame_sample_rate = frame_sample_rate
        self.max_frames = max_frames

    def extract_frames(self, video_path: str) -> List[Image.Image]:
        """
        Extract frames from video file

        Args:
            video_path: Path to video file

        Returns:
            List of PIL Images
        """
        frames = []
        cap = None

        try:
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0

            logger.info(f"Video info: {total_frames} frames, {fps:.2f} FPS, {duration:.2f}s")

            # Adaptive sample rate: always extract at least 10 frames from short videos
            target_frames = min(self.max_frames, max(10, total_frames // self.frame_sample_rate))
            adaptive_rate = max(1, total_frames // target_frames)
            logger.info(f"Adaptive sampling: 1 frame every {adaptive_rate} frames → ~{target_frames} frames")

            frame_idx = 0
            extracted_count = 0

            while cap.isOpened() and extracted_count < self.max_frames:
                ret, frame = cap.read()

                if not ret:
                    break

                # Sample frames at adaptive rate
                if frame_idx % adaptive_rate == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame_rgb)

                    frames.append(pil_image)
                    extracted_count += 1

                frame_idx += 1

            logger.info(f"Extracted {len(frames)} frames from video")

        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
            raise

        finally:
            if cap is not None:
                cap.release()

        if len(frames) == 0:
            raise ValueError("No frames could be extracted from video")

        return frames

    FAKE_THRESHOLD = settings.VIDEO_PREDICTION_THRESHOLD

    def aggregate_predictions(
        self,
        predictions: List[Dict],
        method: str = "confidence_weighted"
    ) -> Dict:
        """
        Aggregate frame-level predictions to video-level prediction

        Args:
            predictions: List of prediction dictionaries from model
            method: Aggregation method ('majority_vote' or 'confidence_weighted')

        Returns:
            Aggregated prediction dictionary
        """
        if not predictions:
            raise ValueError("No predictions to aggregate")

        if method == "majority_vote":
            return self._majority_vote(predictions)
        elif method == "confidence_weighted":
            return self._confidence_weighted(predictions)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")

    def _aggregate_per_model(self, predictions: List[Dict]) -> List[Dict]:
        """Average per-model probabilities across all frames."""
        if not predictions or "per_model" not in predictions[0]:
            return []

        model_keys = [m["model"] for m in predictions[0]["per_model"]]
        result = []
        for i, key in enumerate(model_keys):
            fake_probs = [p["per_model"][i]["fake_prob"] for p in predictions if len(p.get("per_model", [])) > i]
            real_probs = [p["per_model"][i]["real_prob"] for p in predictions if len(p.get("per_model", [])) > i]
            if not fake_probs:
                continue
            avg_fake = float(np.mean(fake_probs))
            avg_real = float(np.mean(real_probs))
            entry = dict(predictions[0]["per_model"][i])
            entry["fake_prob"] = round(avg_fake, 1)
            entry["real_prob"] = round(avg_real, 1)
            result.append(entry)
        return result

    def _majority_vote(self, predictions: List[Dict]) -> Dict:
        """Aggregate using majority voting"""
        fake_count = sum(1 for p in predictions if p["prediction"] == "FAKE")
        real_count = len(predictions) - fake_count

        avg_fake_prob = float(np.mean([p["fake_probability"] for p in predictions])) / 100
        avg_real_prob = float(np.mean([p["real_probability"] for p in predictions])) / 100

        # Normalize
        total = avg_fake_prob + avg_real_prob
        avg_fake_prob /= total
        avg_real_prob /= total

        prediction = "FAKE" if avg_fake_prob >= self.FAKE_THRESHOLD else "REAL"
        confidence = max(avg_fake_prob, avg_real_prob) * 100

        return {
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "real_probability": round(avg_real_prob * 100, 2),
            "fake_probability": round(avg_fake_prob * 100, 2),
            "frames_analyzed": len(predictions),
            "fake_frames": fake_count,
            "real_frames": real_count,
            "aggregation_method": "majority_vote",
            "per_model": self._aggregate_per_model(predictions),
        }

    def _confidence_weighted(self, predictions: List[Dict]) -> Dict:
        """
        Aggregate using confidence-weighted averaging.
        Higher confidence predictions have more influence.
        """
        total_weight = sum(p["confidence"] for p in predictions)

        if total_weight == 0:
            return self._majority_vote(predictions)

        weighted_fake_prob = sum(
            (p["fake_probability"] / 100) * p["confidence"]
            for p in predictions
        ) / total_weight

        weighted_real_prob = sum(
            (p["real_probability"] / 100) * p["confidence"]
            for p in predictions
        ) / total_weight

        # Normalize
        total = weighted_fake_prob + weighted_real_prob
        weighted_fake_prob /= total
        weighted_real_prob /= total

        # Apply same 55% threshold as image predictions
        prediction = "FAKE" if weighted_fake_prob >= self.FAKE_THRESHOLD else "REAL"
        confidence = max(weighted_fake_prob, weighted_real_prob) * 100

        fake_count = sum(1 for p in predictions if p["prediction"] == "FAKE")
        real_count = len(predictions) - fake_count

        return {
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "real_probability": round(weighted_real_prob * 100, 2),
            "fake_probability": round(weighted_fake_prob * 100, 2),
            "frames_analyzed": len(predictions),
            "fake_frames": fake_count,
            "real_frames": real_count,
            "aggregation_method": "confidence_weighted",
            "average_frame_confidence": round(float(np.mean([p["confidence"] for p in predictions])), 2),
            "per_model": self._aggregate_per_model(predictions),
        }

    def get_video_info(self, video_path: str) -> Dict:
        """
        Get video metadata

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        info = {
            "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        }

        info["duration_seconds"] = info["total_frames"] / info["fps"] if info["fps"] > 0 else 0

        cap.release()

        return info


def save_upload_to_temp(contents: bytes, suffix: str) -> str:
    """
    Save uploaded file contents to temporary file

    Args:
        contents: File contents as bytes
        suffix: File extension (e.g., '.mp4')

    Returns:
        Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(contents)
    temp_file.close()

    return temp_file.name


def cleanup_temp_file(file_path: str):
    """Remove temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Removed temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not remove temp file {file_path}: {e}")
