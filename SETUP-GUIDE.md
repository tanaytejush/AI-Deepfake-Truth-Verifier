# Setup Guide

## Backend Setup

The backend uses a Python virtual environment. The venv is already configured — do not reinstall packages carelessly as `pydantic_core` was manually patched for macOS.

### Running the Backend
```bash
cd backend
PYTHONPATH="./venv/lib/python3.13/site-packages" python3.13 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Environment
- Python 3.13 (system install at `/Library/Frameworks/Python.framework/Versions/3.13/`)
- Port: **8001** (port 8000 is reserved for another project)
- GPU: Apple Metal (MPS) auto-detected on M1/M2 Macs

### Model Cache
Downloaded models are stored in `backend/models/cache/` (~1.4 GB).
Models auto-download on first run if cache is missing.

---

## Frontend Setup

```bash
cd frontend
npm install     # only needed first time
npm run dev
```

- Port: **3000**
- API proxy: all `/api/*` requests forwarded to `http://localhost:8001`
- Configured in `frontend/vite.config.js` and `frontend/.env`

### Important: `.env` File
```
VITE_API_URL=http://localhost:8001
```
This must point to port **8001**. Do not change to 8000.

---

## Configuration

### Backend — `backend/app/config.py`
Key settings:
- `ENSEMBLE_MODELS` — list of HuggingFace model IDs in the ensemble
- `MODEL_LABEL_OVERRIDES` — explicit fake/real index mapping per model
- `MODEL_CACHE_DIR` — where downloaded weights are stored

### Decision Threshold — `backend/app/ml/model_loader.py`
```python
prediction = "FAKE" if avg_fake >= 0.55 else "REAL"
```
55% fake confidence required. Adjustable between 0.50–0.65.
