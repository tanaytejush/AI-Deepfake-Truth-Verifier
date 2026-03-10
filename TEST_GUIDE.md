# Test Guide

## Testing via the UI

1. Start both servers (see QUICKSTART.md)
2. Open http://localhost:3000
3. Upload a test image and click **Run Analysis**

**Good test images:**
- AI-generated faces from thispersondoesnotexist.com → should detect as FAKE
- Real photographs from your camera roll → should detect as REAL
- Midjourney/DALL-E generated images → should detect as FAKE

---

## Testing via curl

### Image prediction
```bash
curl -X POST http://localhost:8001/api/v1/predict \
  -F "file=@/path/to/image.jpg"
```

### Video prediction
```bash
curl -X POST http://localhost:8001/api/v1/predict/video \
  -F "file=@/path/to/video.mp4"
```

### Health check
```bash
curl http://localhost:8001/api/v1/health
```

### Statistics
```bash
curl http://localhost:8001/api/v1/statistics
```

### Recent history
```bash
curl http://localhost:8001/api/v1/predictions/recent?limit=10
```

---

## Expected Response (FAKE image)

```json
{
  "prediction": "FAKE",
  "fake_type": "AI-Generated Image",
  "fake_type_detail": "Patterns consistent with AI image synthesis...",
  "fake_tags": ["AI-Generated", "Synthetic"],
  "real_probability": 31.4,
  "fake_probability": 68.6,
  "inference_time": 0.85,
  "device": "mps",
  "ensemble_size": 3
}
```

---

## Backend Logs

```bash
tail -f /tmp/deepfake_backend.log
```

Per-model breakdown is logged for every prediction:
```
↳ ai_vs_real_image_detection: fake=72.1% real=27.9%
↳ Deep-Fake-Detector-v2-Model: fake=68.4% real=31.6%
↳ ai-image-detector-deploy: fake=65.3% real=34.7%
✅ Ensemble (3 models) → FAKE | fake=68.6% real=31.4% | 0.85s
```
