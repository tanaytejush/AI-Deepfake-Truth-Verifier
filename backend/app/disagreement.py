"""
Helpers for detecting ensemble disagreement without changing the primary verdict.
"""

from collections import Counter
from typing import Dict, List

from .config import settings


def _normalize_percentage(value: float) -> float:
    """Accept either 0-1 probabilities or 0-100 percentages."""
    return value * 100 if value <= 1 else value


def build_disagreement_summary(
    results: List[Dict],
    prediction: str,
    avg_fake_probability: float,
    avg_real_probability: float,
) -> Dict:
    """
    Build disagreement metadata for the ensemble response.

    This is additive only: the caller can keep `prediction` unchanged and
    surface these fields in the UI as a softer warning.
    """
    if not results:
        return {
            "prediction_state": "CONFIDENT",
            "disagreement_score": 0.0,
            "uncertain_reason": [],
        }

    vote_counts = Counter(
        "FAKE" if result["fake_prob"] >= result["real_prob"] else "REAL"
        for result in results
    )
    majority_votes = max(vote_counts.values())
    majority_ratio = majority_votes / len(results)
    vote_split = 1.0 - majority_ratio

    fake_pct = _normalize_percentage(avg_fake_probability)
    real_pct = _normalize_percentage(avg_real_probability)
    probability_margin = abs(fake_pct - real_pct)

    reasons = []
    if majority_ratio < settings.DISAGREEMENT_MINORITY_VOTE_RATIO:
        reasons.append(f"vote_split:{vote_counts.get('FAKE', 0)}-{vote_counts.get('REAL', 0)}")

    if probability_margin <= settings.DISAGREEMENT_NEAR_THRESHOLD_MARGIN:
        reasons.append(f"near_threshold:{probability_margin:.1f}pp")

    strongest_opposition = 0.0
    opposing_models = []
    for result in results:
        dominant_label = "FAKE" if result["fake_prob"] >= result["real_prob"] else "REAL"
        dominant_confidence = _normalize_percentage(max(result["fake_prob"], result["real_prob"]))

        if dominant_label != prediction and dominant_confidence >= settings.DISAGREEMENT_STRONG_OPPOSITION_THRESHOLD:
            opposing_models.append({
                "model": result["model"],
                "prediction": dominant_label,
                "confidence": round(dominant_confidence, 1),
            })
            strongest_opposition = max(strongest_opposition, dominant_confidence)

    if opposing_models:
        reasons.append(
            "strong_opposition:" + ",".join(
                f"{item['model'].split('/')[-1]}:{item['prediction']} {item['confidence']:.1f}%"
                for item in opposing_models
            )
        )

    proximity_score = 0.0
    if probability_margin <= settings.DISAGREEMENT_NEAR_THRESHOLD_MARGIN:
        proximity_score = (
            (settings.DISAGREEMENT_NEAR_THRESHOLD_MARGIN - probability_margin)
            / settings.DISAGREEMENT_NEAR_THRESHOLD_MARGIN
            * 100
        )

    disagreement_score = max(vote_split * 100, proximity_score, strongest_opposition)
    prediction_state = "UNCERTAIN" if reasons else "CONFIDENT"

    return {
        "prediction_state": prediction_state,
        "disagreement_score": round(disagreement_score, 2),
        "uncertain_reason": reasons,
        "vote_counts": {
            "REAL": vote_counts.get("REAL", 0),
            "FAKE": vote_counts.get("FAKE", 0),
        },
    }
