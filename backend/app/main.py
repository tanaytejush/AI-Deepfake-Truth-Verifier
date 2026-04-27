"""
FastAPI Main Application
Optimized for production use
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import logging
from pathlib import Path
from typing import List, Dict, Optional
import time
import uuid

from .config import settings
from .ml.model_loader import get_model, ModelLoader
from .database import get_db, SessionLocal, Prediction, init_db
from .video_processor import VideoProcessor, save_upload_to_temp, cleanup_temp_file
from .rate_limiter import rate_limiter
from sqlalchemy.orm import Session

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-based image authenticity verification API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    """
    Add request correlation ID and structured latency logging.
    """
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    client_ip = request.client.host if request.client else "unknown"
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "request_failed method=%s path=%s status=%s duration_ms=%s client_ip=%s request_id=%s",
            request.method,
            request.url.path,
            500,
            duration_ms,
            client_ip,
            request_id,
        )
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_complete method=%s path=%s status=%s duration_ms=%s client_ip=%s request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        client_ip,
        request_id,
    )
    return response

# Create upload directory
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    logger.info("🚀 Starting AI-based Image Authenticity Verification System API")
    logger.info(f"📍 Environment: {'Development' if settings.DEBUG else 'Production'}")

    try:
        # Initialize database tables
        init_db()
        logger.info("✅ Database initialized")

        # Load model
        model = get_model()
        logger.info("✅ Model loaded successfully")

        # Warm up model
        model.warm_up()
        logger.info("✅ Model warmed up")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down API")
    model = get_model()
    model.clear_cache()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI-based Image Authenticity Verification System API",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }


@app.get("/api/v1/health")
async def health_check():
    """Liveness check endpoint"""
    return {
        "status": "healthy",
        "service": "api",
        "timestamp": time.time()
    }


@app.get("/api/v1/ready")
async def readiness_check():
    """Readiness check endpoint (models loaded and ready for inference)."""
    try:
        model_info = get_model().get_model_info()
        is_ready = bool(model_info.get("is_loaded"))
        payload = {
            "status": "ready" if is_ready else "starting",
            "model_loaded": is_ready,
            "device": model_info.get("device", "unknown"),
            "timestamp": time.time(),
        }
        return JSONResponse(status_code=200 if is_ready else 503, content=payload)
    except Exception as error:
        logger.error(f"Readiness check failed: {error}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "starting",
                "model_loaded": False,
                "device": "unknown",
                "timestamp": time.time(),
            },
        )


@app.get("/api/v1/model/info")
async def get_model_info():
    """Get model information"""
    model = get_model()
    return model.get_model_info()


def validate_file(file: UploadFile, file_type: str = "image") -> str:
    """
    Validate uploaded file

    Args:
        file: Uploaded file
        file_type: 'image' or 'video'

    Returns:
        File extension
    """
    # Check file extension
    ext = file.filename.split('.')[-1].lower()

    if file_type == "image":
        if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}"
            )
    elif file_type == "video":
        if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid video type. Allowed: {settings.ALLOWED_VIDEO_EXTENSIONS}"
            )
    else:
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )

    return ext


def _get_client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def _enforce_rate_limit(request: Request, route_key: str, max_requests: int) -> None:
    client_id = _get_client_identifier(request)
    limiter_key = f"{route_key}:{client_id}"
    allowed, retry_after = rate_limiter.check(
        limiter_key,
        max_requests,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Rate limit exceeded: max {max_requests} requests every "
                f"{settings.RATE_LIMIT_WINDOW_SECONDS}s"
            ),
            headers={"Retry-After": str(retry_after)},
        )


def _require_admin_clear_token(token: Optional[str]) -> None:
    configured_token = settings.ADMIN_CLEAR_TOKEN.strip()
    if not configured_token:
        raise HTTPException(
            status_code=503,
            detail="Clear endpoint is disabled. Configure ADMIN_CLEAR_TOKEN.",
        )

    if token != configured_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")


@app.post("/api/v1/predict")
async def predict_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Predict if an uploaded image is real or fake

    Args:
        file: Image file (JPG, PNG)

    Returns:
        Prediction results with confidence scores
    """
    try:
        _enforce_rate_limit(request, "predict_image", settings.RATE_LIMIT_IMAGE_PER_WINDOW)

        # Validate file
        validate_file(file, "image")

        # Read image
        contents = await file.read()

        # Check file size
        if len(contents) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_IMAGE_SIZE / 1024 / 1024}MB"
            )

        # Open image
        try:
            image = Image.open(io.BytesIO(contents))
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {str(e)}"
            )

        # Get model and predict
        model = get_model()
        result = model.predict(image)

        # Save to database
        try:
            prediction = Prediction(
                image_name=file.filename,
                prediction=result["prediction"],
                confidence=result["confidence"],
                real_probability=result["real_probability"],
                fake_probability=result["fake_probability"],
                inference_time=result["inference_time"],
                device=result["device"]
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)

            result["id"] = prediction.id

        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()

        # Add metadata
        result["filename"] = file.filename
        result["model"] = "Ensemble"

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/video")
async def predict_video(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Predict if an uploaded video is real or fake

    Args:
        file: Video file (MP4, AVI, MOV, MKV)

    Returns:
        Aggregated prediction results from multiple frames
    """
    temp_file_path = None

    try:
        _enforce_rate_limit(request, "predict_video", settings.RATE_LIMIT_VIDEO_PER_WINDOW)

        # Validate file
        ext = validate_file(file, "video")

        # Read video
        contents = await file.read()

        # Check file size
        if len(contents) > settings.MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Video too large. Max size: {settings.MAX_VIDEO_SIZE / 1024 / 1024}MB"
            )

        # Save to temporary file (required for OpenCV)
        temp_file_path = save_upload_to_temp(contents, f".{ext}")
        logger.info(f"Processing video: {file.filename}")

        # Initialize video processor
        video_processor = VideoProcessor(
            frame_sample_rate=settings.VIDEO_FRAME_SAMPLE_RATE,
            max_frames=settings.VIDEO_MAX_FRAMES
        )

        # Get video info
        video_info = video_processor.get_video_info(temp_file_path)
        logger.info(f"Video info: {video_info}")

        # Extract frames
        start_time = time.time()
        frames = video_processor.extract_frames(temp_file_path)
        extraction_time = time.time() - start_time

        logger.info(f"Extracted {len(frames)} frames in {extraction_time:.2f}s")

        # Get model and predict on each frame
        model = get_model()
        frame_predictions = []

        prediction_start = time.time()
        for idx, frame in enumerate(frames):
            try:
                result = model.predict(frame)
                frame_predictions.append(result)
                logger.debug(f"Frame {idx}: {result['prediction']} ({result['confidence']:.2%})")
            except Exception as e:
                logger.warning(f"Error predicting frame {idx}: {e}")
                continue

        prediction_time = time.time() - prediction_start

        if not frame_predictions:
            raise HTTPException(
                status_code=500,
                detail="Could not analyze any frames from the video"
            )

        # Aggregate predictions
        aggregated = video_processor.aggregate_predictions(
            frame_predictions,
            method="confidence_weighted"
        )

        # Carry fake_type from the frame most confident about being fake
        if aggregated["prediction"] == "FAKE":
            top_frame = max(frame_predictions, key=lambda r: r.get("fake_probability", 0))
            aggregated["fake_type"]        = top_frame.get("fake_type")
            aggregated["fake_type_detail"] = top_frame.get("fake_type_detail")
            aggregated["fake_tags"]        = top_frame.get("fake_tags", [])
        else:
            aggregated["fake_type"]        = None
            aggregated["fake_type_detail"] = None
            aggregated["fake_tags"]        = []

        # Add metadata
        total_time = time.time() - start_time
        aggregated.update({
            "filename": file.filename,
            "model": "Ensemble",
            "video_info": video_info,
            "extraction_time": round(extraction_time, 3),
            "prediction_time": round(prediction_time, 3),
            "total_processing_time": round(total_time, 3),
            "device": frame_predictions[0]["device"] if frame_predictions else "unknown"
        })

        # Save to database
        try:
            prediction = Prediction(
                image_name=file.filename,
                prediction=aggregated["prediction"],
                confidence=aggregated["confidence"],
                real_probability=aggregated["real_probability"],
                fake_probability=aggregated["fake_probability"],
                inference_time=total_time,
                device=aggregated["device"]
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)

            aggregated["id"] = prediction.id

        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()

        return aggregated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if temp_file_path:
            cleanup_temp_file(temp_file_path)


@app.get("/api/v1/predictions/recent")
async def get_recent_predictions(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent predictions"""
    try:
        predictions = db.query(Prediction).order_by(
            Prediction.created_at.desc()
        ).limit(limit).all()

        return {
            "count": len(predictions),
            "predictions": [
                {
                    "id": p.id,
                    "filename": p.image_name,
                    "prediction": p.prediction,
                    "confidence": p.confidence,
                    "real_probability": p.real_probability,
                    "fake_probability": p.fake_probability,
                    "inference_time": p.inference_time,
                    "created_at": p.created_at.isoformat()
                }
                for p in predictions
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get prediction statistics"""
    try:
        from sqlalchemy import func

        total = db.query(func.count(Prediction.id)).scalar()

        real_count = db.query(func.count(Prediction.id)).filter(
            Prediction.prediction == "REAL"
        ).scalar()

        fake_count = db.query(func.count(Prediction.id)).filter(
            Prediction.prediction == "FAKE"
        ).scalar()

        avg_confidence = db.query(func.avg(Prediction.confidence)).scalar()
        avg_inference_time = db.query(func.avg(Prediction.inference_time)).scalar()

        return {
            "total_predictions": total or 0,
            "real_count": real_count or 0,
            "fake_count": fake_count or 0,
            "average_confidence": round(avg_confidence or 0, 2),
            "average_inference_time": round(avg_inference_time or 0, 3)
        }

    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/predictions/clear")
async def clear_predictions(
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
):
    """Clear all predictions (use with caution)"""
    try:
        _require_admin_clear_token(x_admin_token)
        count = db.query(Prediction).delete()
        db.commit()

        return {
            "message": "Predictions cleared",
            "deleted_count": count
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
