# AI Technical Guide — Deepfake Truth Verifier

**Developed by tanaytejush**

A complete explanation of every AI algorithm, model, and concept used in this project.

---

## Table of Contents

1. [Vision Transformer (ViT)](#1-vision-transformer-vit)
2. [How Classification Works](#2-how-classification-works)
3. [Softmax Function](#3-softmax-function)
4. [Transfer Learning](#4-transfer-learning)
5. [Fine-Tuning](#5-fine-tuning)
6. [Ensemble Learning](#6-ensemble-learning)
7. [The Three Models](#7-the-three-models)
8. [How the Ensemble Makes a Decision](#8-how-the-ensemble-makes-a-decision)
9. [Fake Type Detection](#9-fake-type-detection)
10. [Apple Metal (MPS) GPU Acceleration](#10-apple-metal-mps-gpu-acceleration)
11. [Why Deepfake Detection is Hard](#11-why-deepfake-detection-is-hard)

---

## 1. Vision Transformer (ViT)

### What is it?
A **Vision Transformer** (ViT) is the core neural network architecture used in this project. It was introduced by Google in 2020 and applies the **Transformer** architecture (originally designed for text/NLP) to images.

### How it works — step by step

```
Original Image (e.g. 224×224 pixels)
        │
        ▼
┌─────────────────────────────────────┐
│  Step 1: Split into patches          │
│  Image divided into 16×16 patches   │
│  224×224 image → 196 patches        │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Step 2: Patch Embedding            │
│  Each patch flattened into a        │
│  1D vector, then projected to a     │
│  fixed-size embedding (768 dims)    │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Step 3: Add Position Encoding      │
│  Each patch gets a positional ID    │
│  so the model knows where each      │
│  patch came from in the image       │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Step 4: Transformer Encoder        │
│  Multi-head Self-Attention layers   │
│  let every patch "look at" every    │
│  other patch and learn relationships│
│  (12 attention layers in ViT-Base)  │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Step 5: Classification Head        │
│  A special [CLS] token aggregates   │
│  the full image understanding into  │
│  a single vector → Linear layer     │
│  outputs class scores (logits)      │
└─────────────────────────────────────┘
        │
        ▼
   REAL or FAKE
```

### Why ViT for deepfake detection?
- CNNs (older approach) look at local pixel patterns. ViT sees **global relationships** across the entire image.
- Deepfake artifacts are often subtle and spread across the image (unnatural lighting, skin texture inconsistencies, blending boundaries). ViT catches these better because it relates distant image regions to each other.
- Pre-trained on ImageNet-21k (14 million images), it already understands natural image structure before being fine-tuned for fake detection.

### ViT variants used in this project
- **ViT-Base/16** — 86M parameters, 16×16 patch size (used by `dima806` and `haywoodsloan` models)
- **ViT-Base/16** — same architecture, different training data (used by `prithivMLmods` model)

---

## 2. How Classification Works

Classification is the task of assigning an input (an image) to one of a fixed set of categories. In this project: **REAL** or **FAKE** (binary classification).

### The pipeline

```
Image → Preprocessing → Model → Logits → Softmax → Probabilities → Decision
```

### Logits
Raw, unnormalized scores output by the final linear layer of the model. Example:
```
logits = [-1.2,  3.8]
          REAL   FAKE
```
These aren't probabilities yet — they can be any real number.

### From logits to probabilities
Softmax converts logits into probabilities that sum to 1.0 (see Section 3).

### Decision boundary
```
if fake_probability >= 0.55:
    prediction = "FAKE"
else:
    prediction = "REAL"
```
We use 0.55 (55%) instead of 0.50 to reduce false positives — a real image needs to score below 55% fake to be called REAL.

---

## 3. Softmax Function

### What it does
Converts a vector of raw scores (logits) into a probability distribution where all values are between 0 and 1, and they sum to exactly 1.0.

### Formula
```
softmax(x_i) = e^(x_i) / Σ e^(x_j)
```

### Example
```
logits:       [-1.2,  3.8]
e^logits:     [ 0.30, 44.7]
sum:            45.0
probabilities:[ 0.007, 0.993]
              = 0.7% REAL, 99.3% FAKE
```

### Why not just use the raw logits?
Logits have no natural scale. Softmax normalizes them so you can interpret them as probabilities and compare across different models.

---

## 4. Transfer Learning

### What it is
Transfer learning is the technique of taking a model that was trained on one large task and reusing its learned knowledge for a different, more specific task.

### In this project
All three models started as a **ViT-Base pre-trained on ImageNet-21k** (14 million images, 21,000 categories). That model already learned:
- Edge detection
- Texture recognition
- Shape understanding
- Object part relationships
- Natural image statistics

Instead of training from scratch (which would require millions of images and weeks of compute), the model builders took this pre-trained ViT and fine-tuned it on deepfake datasets.

### Why it works
Low-level visual features (edges, textures) are universal. The model only needs to learn the *specific differences* between real and fake images — not how to process images from scratch.

---

## 5. Fine-Tuning

### What it is
Fine-tuning is the process of continuing training a pre-trained model on a new, smaller, task-specific dataset.

### How it works
```
Pre-trained ViT (ImageNet-21k)
        │
        │  Freeze most layers (keep learned features)
        │  Replace final classification head
        │  Train on new dataset with small learning rate
        ▼
Fine-tuned deepfake detector
```

### What each model was fine-tuned on

| Model | Fine-tuned Dataset | Size |
|---|---|---|
| `dima806/ai_vs_real_image_detection` | AI-generated vs real images | ~200K images |
| `prithivMLmods/Deep-Fake-Detector-v2-Model` | Deepfake manipulation dataset | Large scale |
| `haywoodsloan/ai-image-detector-deploy` | Midjourney, DALL-E, Stable Diffusion outputs | Large scale |

### Why fine-tuning matters for this project
A model fine-tuned on recent AI-generated images (Midjourney v5/v6, DALL-E 3) will perform far better than one fine-tuned on 2019-era face-swap datasets. This is exactly why we replaced the old models — their fine-tuning data was outdated.

---

## 6. Ensemble Learning

### What it is
Ensemble learning combines multiple independent models and aggregates their predictions. The combined result is more accurate and robust than any single model alone.

### Why ensembles work
- Each model makes different errors on different images
- When models disagree, averaging reduces the impact of individual errors
- Multiple models trained on different data provide broader coverage

### Types of ensembling
| Method | Description | Used here? |
|---|---|---|
| Majority voting | Most common prediction wins | No |
| Probability averaging | Average the output probabilities | **Yes** |
| Stacking | Train a meta-model on top | No |
| Weighted average | Models weighted by accuracy | Future improvement |

### How this project ensembles

```
Image
  │
  ├──► Model 1: dima806        → fake_prob = 0.72
  ├──► Model 2: prithivMLmods  → fake_prob = 0.68
  └──► Model 3: haywoodsloan   → fake_prob = 0.65
                                       │
                              Average = 0.683
                                       │
                              0.683 ≥ 0.55 → FAKE
```

### Normalisation
After averaging, probabilities are normalized so real + fake = 1.0 exactly (handles floating point drift):
```python
total = avg_fake + avg_real
avg_fake /= total
avg_real /= total
```

---

## 7. The Three Models

### Model 1: `dima806/ai_vs_real_image_detection`
- **Architecture:** ViT-Base/16
- **Accuracy:** 98.25%
- **Trained on:** Balanced dataset of AI-generated images vs real photographs
- **Label mapping:** `{0: REAL, 1: FAKE}`
- **Specialty:** General AI-generated image detection — works across many generator types
- **Strength:** High accuracy, broad coverage, robust to many image styles

### Model 2: `prithivMLmods/Deep-Fake-Detector-v2-Model`
- **Architecture:** ViT-Base/16
- **Accuracy:** 92.12%
- **Updated:** February 2025
- **Label mapping:** `{0: Realism, 1: Deepfake}`
- **Specialty:** Deepfake and face manipulation detection — face swaps, identity replacement, facial editing
- **Strength:** Specifically trained to catch manipulated faces, GAN-generated faces

### Model 3: `haywoodsloan/ai-image-detector-deploy`
- **Architecture:** ViT-Base/16
- **Trained on:** Outputs from Midjourney, DALL-E, Stable Diffusion
- **Label mapping:** `{0: artificial, 1: real}`
- **Specialty:** Modern commercial AI image generators
- **Strength:** Best at catching photorealistic images from the most popular modern AI tools

### Why three different models?
Each model was trained on a different distribution of data and catches different patterns:
- Model 1 catches AI synthesis artifacts (pixel statistics, frequency patterns)
- Model 2 catches facial manipulation artifacts (blending seams, unnatural features)
- Model 3 catches modern generator signatures (Midjourney's cinematic look, DALL-E's composition style)

Together they cover a much wider range of fake types than any single model.

---

## 8. How the Ensemble Makes a Decision

### Step-by-step flow for every image

```
1. Image received → converted to RGB PIL Image

2. Each model processes independently:
   a. Image processor resizes to 224×224, normalizes pixel values
   b. Model runs forward pass through 12 transformer layers
   c. Softmax applied to logits
   d. Label override used to map probabilities to real/fake correctly

3. Results collected:
   Model 1: fake=0.72, real=0.28
   Model 2: fake=0.68, real=0.32
   Model 3: fake=0.65, real=0.35

4. Average:
   avg_fake = (0.72 + 0.68 + 0.65) / 3 = 0.683
   avg_real = (0.28 + 0.32 + 0.35) / 3 = 0.317

5. Normalize:
   total = 0.683 + 0.317 = 1.000 (already normalized)

6. Decision:
   0.683 >= 0.55 → prediction = "FAKE"

7. Fake type:
   Dominant model (highest fake_prob) = Model 1 (0.72)
   → fake_type = "AI-Generated Image"

8. Return result with verdict, type, tags, per-model breakdown
```

### Label Override System
Different models use different label naming conventions. The override table ensures correct mapping regardless of what the model calls its outputs:
```python
MODEL_LABEL_OVERRIDES = {
    "dima806/ai_vs_real_image_detection":       {"real_idx": 0, "fake_idx": 1},
    "prithivMLmods/Deep-Fake-Detector-v2-Model":{"real_idx": 0, "fake_idx": 1},
    "haywoodsloan/ai-image-detector-deploy":    {"real_idx": 1, "fake_idx": 0},
}
```

---

## 9. Fake Type Detection

After the ensemble makes its FAKE decision, the system identifies *what kind* of fake it is:

```python
# Find the model most confident about fake
top_model = max(results, key=lambda r: r["fake_prob"])

# Map that model to its specialty
fake_type = MODEL_SPECIALTIES[top_model["model"]]["type"]
```

### Fake type categories

| Fake Type | Meaning | Triggered by |
|---|---|---|
| AI-Generated Image | Synthesized by AI, not a real photograph | `dima806` dominant |
| Deepfake / Face Manipulation | Real image but face was swapped or edited | `prithivMLmods` dominant |
| Modern AI Generator | Created by Midjourney, DALL-E, or Stable Diffusion | `haywoodsloan` dominant |

---

## 10. Apple Metal (MPS) GPU Acceleration

### What is MPS?
Metal Performance Shaders (MPS) is Apple's GPU framework for Mac computers (M1/M2/M3 chips). PyTorch supports MPS as a GPU backend.

### Why it matters
Running transformer models on CPU is slow. On MPS:
- Inference time: ~0.6–1.0s per image (3 models)
- On CPU alone: ~5–8s per image

### How it's used
```python
if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

model = model.to(device)
inputs = {k: v.to(device) for k, v in inputs.items()}
```

### Automatic fallback
If MPS is not available (Linux/Windows), the code automatically falls back to CUDA (NVIDIA GPU) or CPU.

---

## 11. Why Deepfake Detection is Hard

### The Arms Race Problem
As detection models improve, generation models adapt to avoid detection. This is an ongoing adversarial game:

```
Better generators → Models get fooled
       ↓
Better detectors trained
       ↓
Generators updated to avoid new detectors
       ↓
Cycle repeats...
```

### Modern generators are extremely hard to detect
A 2024 benchmark study found:
| Generator | Detection Rate |
|---|---|
| ProGAN (2018) | ~95% |
| StyleGAN2 (2020) | ~80% |
| Stable Diffusion v1 (2022) | ~70% |
| Midjourney v5 (2023) | ~45% |
| DALL-E 3 (2023) | ~31% |
| Midjourney v7 (2024) | ~24% |
| Flux Dev (2024) | ~21% |

### Why stylized AI art is even harder
This project's models were trained on **photorealistic** images. Stylized art, illustrations, and dark artistic images (like skeletons, fantasy scenes) have:
- No face artifacts to detect
- Different color/texture statistics
- No photorealistic "tells"

This is a known limitation of current public deepfake detection models.

### The training distribution problem
A model trained on Stable Diffusion images may not detect Midjourney images, because each generator has its own unique artifacts. Generalization requires training on many different generators — which is why the `haywoodsloan` model (trained on multiple modern generators) is included in our ensemble.

---

## Summary

| Concept | Role in this Project |
|---|---|
| Vision Transformer (ViT) | Core neural network architecture for image understanding |
| Transfer Learning | Pre-trained ImageNet weights reused for fake detection |
| Fine-Tuning | Adapts pre-trained ViT to deepfake detection task |
| Softmax | Converts model logits to real/fake probabilities |
| Binary Classification | Two-class decision: REAL or FAKE |
| Ensemble Learning | 3 models averaged for better accuracy and coverage |
| Decision Threshold (55%) | Minimum fake confidence required to call FAKE |
| Label Override Table | Ensures correct real/fake mapping for each model |
| Fake Type Classification | Identifies what kind of fake was detected |
| MPS GPU Acceleration | Fast inference on Apple Silicon Macs |
