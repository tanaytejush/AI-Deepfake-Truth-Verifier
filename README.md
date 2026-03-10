# AI Deepfake Truth Verifier

An AI-powered deepfake and synthetic image/video detection system built with Vision Transformers and an ensemble of 3 specialized models.

**Developed by tanaytejush**

---

## Features

- Detects AI-generated images (Midjourney, DALL-E, Stable Diffusion) and face-swap deepfakes
- Ensemble of 3 high-accuracy ViT models for maximum reliability
- Real-time video analysis (frame-by-frame)
- Prediction history with SQLite persistence
- Dark-mode UI with animated results and per-model breakdown

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Framer Motion |
| Backend | FastAPI + PyTorch + HuggingFace Transformers |
| Models | Vision Transformer (ViT) ensemble |
| Database | SQLite |
| GPU | Apple Metal (MPS) / CUDA / CPU |

---

## Quick Start

### 1. Start the Backend
```bash
cd backend
PYTHONPATH="./venv/lib/python3.13/site-packages" python3.13 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

### 3. Open the App
Visit **http://localhost:3000**

---

## Ensemble Models

| Model | Accuracy | Specialty |
|---|---|---|
| `dima806/ai_vs_real_image_detection` | 98.25% | General AI-generated vs real |
| `prithivMLmods/Deep-Fake-Detector-v2-Model` | 92.12% | Deepfake / face manipulation |
| `haywoodsloan/ai-image-detector-deploy` | — | Midjourney, DALL-E, Stable Diffusion |

Decision threshold: **55%** fake confidence to call FAKE.

---

## Project Structure

```
deepfake-detector/
├── frontend/          # React + Vite app (port 3000)
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── ImageUpload.jsx
│   │       ├── ResultsDisplay.jsx
│   │       ├── Statistics.jsx
│   │       └── History.jsx
│   └── .env           # VITE_API_URL=http://localhost:8001
└── backend/           # FastAPI app (port 8001)
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   ├── ml/
    │   │   └── model_loader.py
    │   └── routers/
    ├── models/cache/  # Downloaded model weights (~1.4 GB)
    └── train/         # Fine-tuning scripts
```
