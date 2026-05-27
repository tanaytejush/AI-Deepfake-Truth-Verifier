# AI Deepfake Truth Verifier

## Problem Statement

AI-generated images and face-swap deepfakes are now indistinguishable from real content to the human eye. For platforms operating at scale — social networks, news aggregators, content moderation teams — a wrong verdict on a single viral piece of content can cause real-world harm: defamation, political manipulation, or the suppression of legitimate footage. Existing single-model detectors force a binary Real/Fake verdict regardless of confidence, which is the wrong design choice for a domain where uncertainty should trigger review, not a decision.

## Who It's For

This system is built for **content moderation teams and trust-and-safety analysts** who review flagged media at volume. It is also suitable for integration into automated content pipelines where a third-party deepfake detection verdict is needed before publishing or amplifying content. The audience is an operations team, not a research lab.

## Key Product Decisions

**Why an ensemble of three Vision Transformer models instead of one?**
A single model trained on one dataset will overfit to the artifacts of that dataset's generation method. Different deepfake techniques (diffusion models, GAN face-swaps, full-image synthesis) leave different statistical signatures. Three models trained on diverse data sources vote independently — when they agree, confidence is high. When they disagree, the system knows something is genuinely ambiguous.

**Why introduce an UNCERTAIN verdict state?**
This is the most important product decision in the project. Standard classifiers output a Real or Fake label no matter what. In content moderation, a forced verdict on a low-confidence case creates false precision — the system looks confident when it isn't, which trains operators to over-trust it. By surfacing UNCERTAIN as a first-class output state when model confidence scores diverge beyond a threshold, the system explicitly routes ambiguous cases to human review instead of making a decision it cannot stand behind. Reliability was prioritised over coverage.

**Why full production infrastructure for a student project?**
The system was built with a deployment-first mindset: Docker for reproducibility, nginx as a reverse proxy, GitHub Actions for CI/CD on every push, Redis for rate limiting, and JWT for auth. This reflects the real operational requirements of any moderation tool — it cannot be a notebook that runs once; it has to be a service that is always on, versioned, and protected from abuse.

## Tech Stack

| Layer | Technology |
|---|---|
| Detection models | Vision Transformer (ViT) ensemble — 3 models |
| Model accuracy | Up to 98.25% on benchmark test sets |
| Backend | Python, FastAPI |
| Infrastructure | Docker, nginx |
| CI/CD | GitHub Actions |
| Auth & rate limiting | JWT, Redis |

## How To Run

```bash
# Clone and build
git clone https://github.com/tanaytejush/AI-Deepfake-Truth-Verifier.git
cd AI-Deepfake-Truth-Verifier
docker compose up --build

# The API will be available at http://localhost:80
# POST /verify with a multipart image upload to get a verdict: REAL / FAKE / UNCERTAIN
```

Model weights are downloaded automatically on first run. See `/docs` for the full API reference and confidence threshold configuration.
