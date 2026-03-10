# Quick Start Guide

## Prerequisites

- Python 3.13
- Node.js 18+
- ~2 GB disk space for model weights

---

## Start the Backend

```bash
cd backend
PYTHONPATH="./venv/lib/python3.13/site-packages" python3.13 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

First startup downloads model weights (~1.4 GB total). Subsequent starts load from cache in ~10 seconds.

---

## Start the Frontend

```bash
cd frontend
npm run dev
```

Opens at **http://localhost:3000**

---

## Using the App

1. Go to the **Analyze** tab
2. Drop an image or video onto the upload area (or click to browse)
   - Images: JPG, PNG (max 10 MB)
   - Videos: MP4, MOV, AVI, MKV (max 50 MB)
3. Click **Run Analysis**
4. Results show:
   - REAL or FAKE verdict
   - Type of fake (AI-Generated, Deepfake, Modern Generator)
   - Per-model confidence breakdown
5. View past results in the **History** tab
6. See aggregate stats in the **Statistics** tab

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/predict` | Analyze an image |
| POST | `/api/v1/predict/video` | Analyze a video |
| GET | `/api/v1/statistics` | Aggregate stats |
| GET | `/api/v1/predictions/recent` | Recent history |
| DELETE | `/api/v1/predictions/clear` | Clear history |
| GET | `/api/v1/health` | Health check |
