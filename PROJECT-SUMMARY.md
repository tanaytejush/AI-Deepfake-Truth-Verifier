# Project Summary — AI Deepfake Truth Verifier

**Developed by tanaytejush**

---

## What It Does

Analyzes images and videos to determine whether they are real or AI-generated/manipulated using an ensemble of 3 Vision Transformer models.

---

## How It Works

1. User uploads an image or video through the React frontend
2. The file is sent to the FastAPI backend via `/api/v1/predict`
3. The ensemble runs all 3 models on the image in sequence
4. Each model outputs a fake/real probability
5. Probabilities are averaged; if avg fake ≥ 55% → verdict is FAKE
6. The dominant model determines the *type* of fake detected
7. Result is returned with verdict, fake type, tags, and per-model breakdown
8. Saved to SQLite for history and statistics

---

## Ensemble Architecture

```
Image Input
    │
    ├─► dima806/ai_vs_real_image_detection      → fake prob (98.25% acc)
    ├─► prithivMLmods/Deep-Fake-Detector-v2-Model → fake prob (92.12% acc)
    └─► haywoodsloan/ai-image-detector-deploy   → fake prob (Midjourney/DALL-E/SD)
         │
         └─► Average → if ≥ 55% → FAKE else REAL
```

---

## Fake Type Classification

| Dominant Model | Fake Type Shown |
|---|---|
| `dima806/ai_vs_real_image_detection` | AI-Generated Image |
| `prithivMLmods/Deep-Fake-Detector-v2-Model` | Deepfake / Face Manipulation |
| `haywoodsloan/ai-image-detector-deploy` | Modern AI Generator (Midjourney/DALL-E/SD) |

---

## API Response

```json
{
  "prediction": "FAKE",
  "fake_type": "Modern AI Generator",
  "fake_type_detail": "Signatures of a modern generator detected...",
  "fake_tags": ["Midjourney", "DALL-E", "Stable Diffusion"],
  "real_probability": 28.4,
  "fake_probability": 71.6,
  "per_model": [
    { "model": "ai_vs_real_image_detection", "specialty": "AI-Generated Image", "fake_prob": 68.2, "real_prob": 31.8 },
    { "model": "Deep-Fake-Detector-v2-Model", "specialty": "Deepfake / Face Manipulation", "fake_prob": 74.1, "real_prob": 25.9 },
    { "model": "ai-image-detector-deploy", "specialty": "Modern AI Generator", "fake_prob": 72.5, "real_prob": 27.5 }
  ],
  "inference_time": 0.82,
  "device": "mps",
  "ensemble_size": 3
}
```
