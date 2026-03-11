# ── Stage 1: Build React frontend ────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .

# Empty VITE_API_URL so the built app uses relative paths → nginx proxies /api/
ENV VITE_API_URL=""
RUN npm run build


# ── Stage 2: Final runtime image ─────────────────────────────────────────────
FROM python:3.11-slim

# System dependencies (OpenCV + nginx + supervisor + ffmpeg for video)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy backend source
COPY backend/app /app/backend/app

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy nginx + supervisor configs
COPY nginx-hf.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create required runtime directories
RUN mkdir -p \
    /app/backend/models/cache \
    /app/backend/uploads \
    /app/data \
    /var/log/supervisor

WORKDIR /app/backend

EXPOSE 7860

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
