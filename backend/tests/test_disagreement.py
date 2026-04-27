"""
Tests for disagreement-aware ensemble metadata.
"""

from app.disagreement import build_disagreement_summary


def test_disagreement_detects_split_and_strong_opposition():
    results = [
        {"model": "model-a", "fake_prob": 0.80, "real_prob": 0.20},
        {"model": "model-b", "fake_prob": 0.74, "real_prob": 0.26},
        {"model": "model-c", "fake_prob": 0.00, "real_prob": 1.00},
    ]

    summary = build_disagreement_summary(
        results=results,
        prediction="FAKE",
        avg_fake_probability=70.0,
        avg_real_probability=30.0,
    )

    assert summary["prediction_state"] == "UNCERTAIN"
    assert summary["disagreement_score"] >= 33
    assert summary["vote_counts"]["FAKE"] == 2
    assert summary["vote_counts"]["REAL"] == 1
    assert any(reason.startswith("strong_opposition:") for reason in summary["uncertain_reason"])


def test_disagreement_remains_confident_for_unanimous_result():
    results = [
        {"model": "model-a", "fake_prob": 0.90, "real_prob": 0.10},
        {"model": "model-b", "fake_prob": 0.85, "real_prob": 0.15},
        {"model": "model-c", "fake_prob": 0.88, "real_prob": 0.12},
    ]

    summary = build_disagreement_summary(
        results=results,
        prediction="FAKE",
        avg_fake_probability=87.6,
        avg_real_probability=12.4,
    )

    assert summary["prediction_state"] == "CONFIDENT"
    assert summary["disagreement_score"] == 0.0
    assert summary["uncertain_reason"] == []
