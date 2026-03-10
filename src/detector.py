"""
Deepfake Detection Module using Pretrained Model
Uses Hugging Face transformers for inference
"""

import torch
from transformers import pipeline
from PIL import Image
import numpy as np
from typing import Dict, Tuple
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepfakeDetector:
    """
    Deepfake detector using pretrained models from Hugging Face
    """

    def __init__(self, model_name: str = "dima806/deepfake_vs_real_image_detection"):
        """
        Initialize the detector with a pretrained model

        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # Load the model
        logger.info(f"Loading model: {model_name}")
        try:
            self.detector = pipeline(
                "image-classification",
                model=model_name,
                device=0 if self.device == "mps" else -1
            )
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Falling back to CPU...")
            self.detector = pipeline(
                "image-classification",
                model=model_name,
                device=-1  # CPU
            )

    def preprocess_image(self, image_path: str) -> Image.Image:
        """
        Preprocess image for inference

        Args:
            image_path: Path to the image file

        Returns:
            PIL Image object
        """
        try:
            image = Image.open(image_path)

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            logger.info(f"Image loaded: {image.size}")
            return image

        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise

    def predict(self, image_path: str) -> Dict[str, float]:
        """
        Predict if an image is real or fake

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with prediction results
            {
                'prediction': 'REAL' or 'FAKE',
                'confidence': float (0-100),
                'real_probability': float,
                'fake_probability': float
            }
        """
        try:
            # Load and preprocess image
            image = self.preprocess_image(image_path)

            # Run inference
            logger.info("Running inference...")
            results = self.detector(image)

            # Parse results
            result_dict = {item['label']: item['score'] for item in results}

            # Determine prediction
            fake_score = result_dict.get('FAKE', result_dict.get('fake', 0.0))
            real_score = result_dict.get('REAL', result_dict.get('real', 1.0 - fake_score))

            prediction = 'FAKE' if fake_score > real_score else 'REAL'
            confidence = max(fake_score, real_score) * 100

            return {
                'prediction': prediction,
                'confidence': confidence,
                'real_probability': real_score * 100,
                'fake_probability': fake_score * 100,
                'raw_results': results
            }

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise

    def predict_batch(self, image_paths: list) -> list:
        """
        Predict multiple images

        Args:
            image_paths: List of image file paths

        Returns:
            List of prediction dictionaries
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path)
                result['image_path'] = image_path
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                results.append({
                    'image_path': image_path,
                    'error': str(e)
                })

        return results


def main():
    """
    Test the detector with a sample image
    """
    print("=" * 60)
    print("AI Deepfake Truth Verifier - Testing")
    print("=" * 60)

    # Initialize detector
    detector = DeepfakeDetector()

    # Example usage
    print("\nTo test the detector, place an image in the 'data/test_images/' folder")
    print("Then run: python src/detector.py")

    # Check for test images
    test_dir = Path("data/test_images")
    if test_dir.exists():
        test_images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))

        if test_images:
            print(f"\nFound {len(test_images)} test image(s)")
            for img_path in test_images:
                print(f"\n--- Testing: {img_path.name} ---")
                result = detector.predict(str(img_path))

                print(f"Prediction: {result['prediction']}")
                print(f"Confidence: {result['confidence']:.2f}%")
                print(f"Real Probability: {result['real_probability']:.2f}%")
                print(f"Fake Probability: {result['fake_probability']:.2f}%")
        else:
            print("\nNo test images found in data/test_images/")
            print("Please add some .jpg or .png files to test")
    else:
        print(f"\nCreating test_images directory...")
        test_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
