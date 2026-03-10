# Developer Guide

**Developed by tanaytejush**

---

## Adding a New Model to the Ensemble

1. Find a HuggingFace model that works with `AutoModelForImageClassification`
2. Check its label mapping:
   ```python
   from transformers import AutoModelForImageClassification
   model = AutoModelForImageClassification.from_pretrained("model-id", cache_dir="./models/cache")
   print(model.config.id2label)
   ```
3. Add it to `ENSEMBLE_MODELS` in `backend/app/config.py`
4. Add its label override to `MODEL_LABEL_OVERRIDES` in the same file
5. Add its specialty description to `MODEL_SPECIALTIES` in `backend/app/ml/model_loader.py`
6. Restart the backend

---

## Adjusting Detection Sensitivity

In `backend/app/ml/model_loader.py`:
```python
prediction = "FAKE" if avg_fake >= 0.55 else "REAL"
```
- Lower (e.g. `0.50`) → catches more fakes, more false positives on real images
- Higher (e.g. `0.65`) → fewer false positives, misses borderline fakes

---

## Frontend Components

| Component | Purpose |
|---|---|
| `App.jsx` | Layout, tabs (Analyze/Statistics/History), watermark |
| `Header.jsx` | Top bar with title and model status |
| `ImageUpload.jsx` | File drop zone, preview, analyze button |
| `ResultsDisplay.jsx` | Verdict, fake type, per-model breakdown bars |
| `Statistics.jsx` | Aggregate detection stats |
| `History.jsx` | Recent predictions list |

---

## Backend Routers

Located in `backend/app/routers/`:
- `predict.py` — `/api/v1/predict` (image) and `/api/v1/predict/video`
- `predictions.py` — history and clear endpoints
- `statistics.py` — aggregate stats endpoint

---

## Database

SQLite at `backend/deepfake_detector.db`. Schema managed by SQLAlchemy.
Each prediction stores: filename, prediction, confidence, real/fake probability, inference time, created_at.

---

## Known Limitations

- Models struggle with highly stylized AI art (illustrations, anime-style)
- Modern generators (Midjourney v7, Flux Dev) achieve 18-24% detection rates industry-wide
- Video analysis samples every 30 frames (configurable via `VIDEO_FRAME_SAMPLE_RATE` in config)
