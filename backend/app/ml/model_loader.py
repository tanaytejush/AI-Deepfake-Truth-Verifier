"""
Ensemble Model Loader — runs multiple pre-trained transformers in parallel
and averages their predictions for higher accuracy.
"""

import torch
from transformers import AutoModelForImageClassification, AutoImageProcessor
from PIL import Image
import logging
from pathlib import Path
from typing import Optional, Dict, List
import time
from functools import lru_cache

from ..config import settings

logger = logging.getLogger(__name__)

TRAINED_MODEL_PATH = Path(__file__).parent.parent.parent / "train" / "trained_model"

# Each model's detection specialty — used to explain *what kind* of fake was detected
MODEL_SPECIALTIES = {
    "dima806/ai_vs_real_image_detection": {
        "type": "AI-Generated Image",
        "detail": "Patterns consistent with AI image synthesis (GAN, diffusion model, or neural renderer)",
        "tags": ["AI-Generated", "Synthetic"],
    },
    "prithivMLmods/Deep-Fake-Detector-v2-Model": {
        "type": "Deepfake / Face Manipulation",
        "detail": "Facial manipulation artifacts detected — likely a face-swap or identity replacement",
        "tags": ["Face-Swap", "Deepfake"],
    },
    "haywoodsloan/ai-image-detector-deploy": {
        "type": "Modern AI Generator",
        "detail": "Signatures of a modern generator detected (Midjourney, DALL-E, Stable Diffusion, etc.)",
        "tags": ["Midjourney", "DALL-E", "Stable Diffusion"],
    },
    "umm-maybe/AI-image-detector": {
        "type": "AI-Generated Image",
        "detail": "Image classified as artificially generated rather than a real photograph",
        "tags": ["AI-Generated", "Synthetic"],
    },
}


class SingleModel:
    """Wraps one transformer model + its image processor."""

    def __init__(self, model_name: str, device: torch.device, cache_dir: Path):
        self.model_name = model_name
        self.device = device
        self._model = None
        self._processor = None
        self._load(cache_dir)

    def _load(self, cache_dir: Path):
        logger.info(f"📥 Loading model: {self.model_name}")
        start = time.time()
        self._processor = AutoImageProcessor.from_pretrained(
            self.model_name, cache_dir=cache_dir
        )
        self._model = AutoModelForImageClassification.from_pretrained(
            self.model_name, cache_dir=cache_dir
        ).to(self.device)
        self._model.eval()
        logger.info(f"✅ {self.model_name} loaded in {time.time() - start:.2f}s")

    @torch.no_grad()
    def predict(self, image: Image.Image) -> Dict:
        inputs = self._processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self._model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()[0]

        id2label = self._model.config.id2label
        label2id = self._model.config.label2id

        # 1. Check explicit override table first (most reliable)
        override = settings.MODEL_LABEL_OVERRIDES.get(self.model_name)
        if override:
            real_idx = override["real_idx"]
            fake_idx = override["fake_idx"]
        else:
            # 2. Keyword-based auto-detection
            real_idx, fake_idx = None, None
            for label, idx in label2id.items():
                idx = int(idx)  # normalise string indices (e.g. '0') to int
                label_lower = label.lower()
                if any(w in label_lower for w in ('real', 'genuine', 'authentic', 'human', 'nature')):
                    real_idx = idx
                elif any(w in label_lower for w in ('fake', 'deepfake', 'artificial', 'generated', 'manipulated')):
                    fake_idx = idx

            # 3. Final fallback
            if real_idx is None:
                real_idx = 0
            if fake_idx is None:
                fake_idx = 1

        real_idx = int(real_idx)
        fake_idx = int(fake_idx)
        real_prob = float(probs[real_idx]) if real_idx < len(probs) else 1.0 - float(probs[fake_idx])
        fake_prob = float(probs[fake_idx]) if fake_idx < len(probs) else 1.0 - float(probs[real_idx])

        return {"real_prob": real_prob, "fake_prob": fake_prob, "model": self.model_name}


class ModelLoader:
    """
    Ensemble of multiple deepfake detection transformers.
    Singleton — loaded once at startup, reused for all requests.
    """

    _instance: Optional['ModelLoader'] = None
    _models: List[SingleModel] = []
    _device: Optional[torch.device] = None
    _is_loaded: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_loaded:
            self._setup_device()
            self._load_ensemble()

    def _setup_device(self):
        if torch.backends.mps.is_available() and settings.USE_GPU:
            self._device = torch.device("mps")
            logger.info("✅ Using Apple Metal (MPS) GPU")
        elif torch.cuda.is_available() and settings.USE_GPU:
            self._device = torch.device("cuda")
            logger.info("✅ Using CUDA GPU")
        else:
            self._device = torch.device("cpu")
            logger.info("ℹ️  Using CPU")

    def _load_ensemble(self):
        cache_dir = Path(settings.MODEL_CACHE_DIR)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Use only the configured ensemble models (local fine-tuned model excluded:
        # it was trained on too few images and degrades ensemble accuracy)
        model_names = list(settings.ENSEMBLE_MODELS)

        loaded = []
        for name in model_names:
            try:
                loaded.append(SingleModel(name, self._device, cache_dir))
            except Exception as e:
                logger.warning(f"⚠️  Could not load {name}: {e} — skipping")

        if not loaded:
            raise RuntimeError("No models could be loaded. Check your network connection.")

        self._models = loaded
        self._is_loaded = True
        logger.info(f"✅ Ensemble ready: {len(self._models)} model(s) loaded")

    @torch.no_grad()
    def predict(self, image: Image.Image) -> Dict:
        if not self._is_loaded or not self._models:
            raise RuntimeError("No models loaded")

        start = time.time()
        results = []
        failed = []

        for m in self._models:
            try:
                results.append(m.predict(image))
            except Exception as e:
                logger.warning(f"⚠️  Model {m.model_name} failed on this image: {e}")
                failed.append(m.model_name)

        if not results:
            raise RuntimeError("All models failed to predict")

        # Average fake/real probabilities across all models (equal weight)
        avg_fake = sum(r["fake_prob"] for r in results) / len(results)
        avg_real = sum(r["real_prob"] for r in results) / len(results)

        # Normalise so they sum to 1.0 (handles floating point drift)
        total = avg_fake + avg_real
        avg_fake /= total
        avg_real /= total

        # Require 55% fake confidence before calling FAKE — balanced tradeoff
        prediction = "FAKE" if avg_fake >= 0.55 else "REAL"
        confidence = max(avg_fake, avg_real) * 100

        inference_time = time.time() - start

        # Determine fake type — find the model most confident about fake
        fake_type = None
        fake_type_detail = None
        fake_tags = []
        if prediction == "FAKE":
            top = max(results, key=lambda r: r["fake_prob"])
            specialty = MODEL_SPECIALTIES.get(top["model"])
            if specialty:
                fake_type = specialty["type"]
                fake_type_detail = specialty["detail"]
                fake_tags = specialty["tags"]
            else:
                fake_type = "Manipulated / Synthetic"
                fake_type_detail = "Anomalies detected that are inconsistent with an authentic image"
                fake_tags = ["Manipulated"]

        result = {
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "real_probability": round(avg_real * 100, 2),
            "fake_probability": round(avg_fake * 100, 2),
            "fake_type": fake_type,
            "fake_type_detail": fake_type_detail,
            "fake_tags": fake_tags,
            "inference_time": round(inference_time, 3),
            "device": str(self._device),
            "ensemble_size": len(results),
            "models_used": [r["model"] for r in results],
            "per_model": [
                {
                    "model": r["model"].split("/")[-1],
                    "full_model": r["model"],
                    "fake_prob": round(r["fake_prob"] * 100, 1),
                    "real_prob": round(r["real_prob"] * 100, 1),
                    "specialty": MODEL_SPECIALTIES.get(r["model"], {}).get("type", "Detection Model"),
                }
                for r in results
            ],
        }

        for r in results:
            logger.info(f"   ↳ {r['model'].split('/')[-1]}: fake={r['fake_prob']*100:.1f}% real={r['real_prob']*100:.1f}%")
        logger.info(
            f"✅ Ensemble ({len(results)} models) → {prediction} "
            f"| fake={avg_fake*100:.1f}% real={avg_real*100:.1f}% "
            f"| {inference_time:.2f}s"
        )
        return result

    def warm_up(self):
        try:
            logger.info("🔥 Warming up ensemble...")
            dummy = Image.new("RGB", (224, 224), color="white")
            self.predict(dummy)
            logger.info("✅ Warm-up complete")
        except Exception as e:
            logger.warning(f"⚠️  Warm-up failed: {e}")

    def get_model_info(self) -> Dict:
        return {
            "model_name": "Ensemble",
            "ensemble_models": [m.model_name for m in self._models],
            "ensemble_size": len(self._models),
            "is_fine_tuned": TRAINED_MODEL_PATH.exists(),
            "device": str(self._device),
            "is_loaded": self._is_loaded,
            "cache_dir": settings.MODEL_CACHE_DIR,
        }

    def clear_cache(self):
        if self._device and self._device.type == "cuda":
            torch.cuda.empty_cache()
        elif self._device and self._device.type == "mps":
            torch.mps.empty_cache()


@lru_cache(maxsize=1)
def get_model() -> ModelLoader:
    return ModelLoader()
