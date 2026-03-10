# Video Feature Guide

## Supported Formats

MP4, AVI, MOV, MKV — max 50 MB

---

## How Video Analysis Works

1. Video is uploaded and saved temporarily
2. Frames are extracted at 1 frame every 30 frames (`VIDEO_FRAME_SAMPLE_RATE`)
3. Each frame is analyzed by the full ensemble
4. Results are aggregated across all frames
5. Final verdict: majority vote weighted by confidence

---

## Configuration

In `backend/app/config.py`:

```python
VIDEO_FRAME_SAMPLE_RATE: int = 30   # Extract 1 frame every N frames
VIDEO_MAX_FRAMES: int = 100          # Max frames to analyze per video
VIDEO_PREDICTION_THRESHOLD: float = 0.7  # Confidence threshold for aggregation
```

---

## Response Fields (Video)

```json
{
  "prediction": "FAKE",
  "frames_analyzed": 45,
  "fake_frames": 38,
  "real_frames": 7,
  "aggregation_method": "weighted_vote",
  "total_processing_time": 42.1,
  "device": "mps"
}
```

---

## Performance

- ~0.85s per frame on Apple M1/M2 (MPS)
- A 30-second video at 30fps = ~30 frames analyzed ≈ 25–30 seconds total
- Increase `VIDEO_FRAME_SAMPLE_RATE` to analyze fewer frames and speed up processing
