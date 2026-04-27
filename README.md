# AI Deepfake Truth Verifier

AI-powered deepfake and synthetic media detection for images and videos using a 3-model Vision Transformer ensemble.

**Developed by tanaytejush**

## What It Does

- Detects AI-generated images (Midjourney, DALL-E, Stable Diffusion) and face-swap deepfakes
- Runs an ensemble of 3 ViT models for robust predictions
- Supports video analysis with frame sampling and aggregation
- Stores prediction history in SQLite
- Shows per-model breakdown and confidence scores

## Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Framer Motion |
| Backend | FastAPI + PyTorch + HuggingFace Transformers |
| Models | Vision Transformer (ViT) ensemble |
| Database | SQLite |
| GPU | Apple Metal (MPS) / CUDA / CPU |

## Quick Start (Local)

### 1) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 2) Frontend

```bash
cd frontend
npm run dev
```

### 3) Open

- App: `http://localhost:3000`
- API docs: `http://localhost:8001/docs`

## API Health Endpoints

- Liveness: `GET /api/v1/health`
- Readiness: `GET /api/v1/ready`

## Security and Config

- To protect clear-history endpoint (`DELETE /api/v1/predictions/clear`):
  - Token mode (default): set `ADMIN_CLEAR_TOKEN` (or `ADMIN_CLEAR_TOKENS`) in `backend/.env`
  - JWT mode: set `ADMIN_AUTH_MODE=jwt`, `JWT_SECRET_KEY`, and `ADMIN_JWT_ALLOWED_ROLES`
  - Hybrid mode: set `ADMIN_AUTH_MODE=hybrid` to allow either token or JWT
  - Optionally set `VITE_ADMIN_CLEAR_TOKEN` in `frontend/.env`
- Rate limiting is enabled for prediction endpoints:
  - Default backend is in-memory
  - Optional Redis backend: set `RATE_LIMIT_BACKEND=redis` and `REDIS_URL`
- Default local backend port is `8001`.

## Ensemble Models

| Model | Accuracy | Specialty |
|---|---|---|
| `dima806/ai_vs_real_image_detection` | 98.25% | General AI-generated vs real |
| `prithivMLmods/Deep-Fake-Detector-v2-Model` | 92.12% | Deepfake / face manipulation |
| `haywoodsloan/ai-image-detector-deploy` | — | Midjourney, DALL-E, Stable Diffusion |

Decision threshold: **55%** fake confidence => `FAKE`.

## Project Structure

```text
deepfake-detector/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   └── .env
└── backend/
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   ├── ml/
    │   │   └── model_loader.py
    │   └── rate_limiter.py
    └── .env
```

---

**Watermark: tanaytejush**
