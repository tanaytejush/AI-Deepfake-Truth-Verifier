"""
Database module for storing deepfake detection results
Uses SQLite for lightweight storage
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DeepfakeDatabase:
    """
    SQLite database for storing prediction history
    """

    def __init__(self, db_path: str = "data/deepfake_predictions.db"):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """
        Create tables if they don't exist
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_name TEXT NOT NULL,
                    image_path TEXT,
                    prediction TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    real_probability REAL,
                    fake_probability REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT,
                    processing_time REAL
                )
            """)

            # Create index on timestamp for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON predictions(timestamp)
            """)

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def save_prediction(
        self,
        image_name: str,
        prediction: str,
        confidence: float,
        real_probability: float = None,
        fake_probability: float = None,
        image_path: str = None,
        model_name: str = None,
        processing_time: float = None
    ) -> int:
        """
        Save a prediction to the database

        Args:
            image_name: Name of the image file
            prediction: 'REAL' or 'FAKE'
            confidence: Confidence score (0-100)
            real_probability: Probability of being real
            fake_probability: Probability of being fake
            image_path: Full path to image
            model_name: Name of the model used
            processing_time: Time taken for inference (seconds)

        Returns:
            ID of the inserted record
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO predictions (
                    image_name, image_path, prediction, confidence,
                    real_probability, fake_probability, model_name, processing_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                image_name, image_path, prediction, confidence,
                real_probability, fake_probability, model_name, processing_time
            ))

            record_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Saved prediction for {image_name} (ID: {record_id})")
            return record_id

        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            raise

    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """
        Get recent predictions

        Args:
            limit: Number of records to retrieve

        Returns:
            List of prediction dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM predictions
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            conn.close()

            # Convert to list of dictionaries
            predictions = [dict(row) for row in rows]
            return predictions

        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []

    def get_statistics(self) -> Dict:
        """
        Get overall statistics

        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total predictions
            cursor.execute("SELECT COUNT(*) FROM predictions")
            total = cursor.fetchone()[0]

            # Count by prediction type
            cursor.execute("""
                SELECT prediction, COUNT(*) as count
                FROM predictions
                GROUP BY prediction
            """)
            counts = dict(cursor.fetchall())

            # Average confidence
            cursor.execute("SELECT AVG(confidence) FROM predictions")
            avg_confidence = cursor.fetchone()[0] or 0

            # Average processing time
            cursor.execute("SELECT AVG(processing_time) FROM predictions WHERE processing_time IS NOT NULL")
            avg_time = cursor.fetchone()[0] or 0

            conn.close()

            return {
                'total_predictions': total,
                'real_count': counts.get('REAL', 0),
                'fake_count': counts.get('FAKE', 0),
                'average_confidence': avg_confidence,
                'average_processing_time': avg_time
            }

        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            return {}

    def clear_all(self):
        """
        Clear all predictions (use with caution!)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM predictions")
            conn.commit()
            conn.close()
            logger.info("All predictions cleared")

        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise


def main():
    """
    Test the database module
    """
    print("Testing Database Module")
    print("=" * 60)

    # Initialize database
    db = DeepfakeDatabase()

    # Test saving a prediction
    db.save_prediction(
        image_name="test_image.jpg",
        prediction="FAKE",
        confidence=95.5,
        real_probability=4.5,
        fake_probability=95.5,
        model_name="dima806/deepfake_vs_real_image_detection",
        processing_time=0.15
    )

    # Get statistics
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    print(f"Total Predictions: {stats['total_predictions']}")
    print(f"Real: {stats['real_count']}, Fake: {stats['fake_count']}")
    print(f"Average Confidence: {stats['average_confidence']:.2f}%")
    print(f"Average Processing Time: {stats['average_processing_time']:.3f}s")

    # Get recent predictions
    recent = db.get_recent_predictions(limit=5)
    print(f"\nRecent Predictions ({len(recent)}):")
    for pred in recent:
        print(f"  - {pred['image_name']}: {pred['prediction']} ({pred['confidence']:.2f}%)")


if __name__ == "__main__":
    main()
