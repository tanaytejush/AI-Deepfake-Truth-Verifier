# Full Project Explanation — AI Deepfake Truth Verifier

**Developed by tanaytejush**

This document explains everything about the project — what it does, how it works, what AI is being used, and why every decision was made. Written to be understood by anyone, technical or not.

---

## Part 1 — What Is This Project?

### The Problem
The internet is flooded with AI-generated images and videos that look completely real. Tools like Midjourney, DALL-E, and Stable Diffusion can generate photorealistic faces, scenes, and videos in seconds. This creates serious problems — fake news, identity fraud, misinformation, and manipulation.

The human eye cannot reliably tell the difference between a real photograph and a high-quality AI-generated image anymore. We need machines to do it.

### The Solution
This project is an AI system that analyzes any image or video and tells you:
- Is it **REAL** or **FAKE**?
- If fake — *what kind* of fake is it? (AI-generated? Face-swap deepfake? Modern generator like Midjourney?)
- Which AI models detected it, and how confident each one was?

It runs in a web browser. You upload a file, click a button, and get a result in under 1 second.

---

## Part 2 — How the App Works (Big Picture)

```
User uploads image
       │
       ▼
React Frontend (browser, port 3000)
       │  HTTP POST /api/v1/predict
       ▼
FastAPI Backend (Python server, port 8001)
       │
       ├──► Model 1: dima806/ai_vs_real_image_detection
       ├──► Model 2: prithivMLmods/Deep-Fake-Detector-v2-Model
       └──► Model 3: haywoodsloan/ai-image-detector-deploy
                │
                ▼
       Average probabilities
                │
                ▼
       REAL or FAKE + Fake Type
                │
       Save to SQLite database
                │
                ▼
       Return result to browser
                │
                ▼
       Display verdict, fake type,
       per-model breakdown to user
```

---

## Part 3 — The Technology Stack

### Frontend (What You See)
- **React** — JavaScript framework for building the user interface
- **Vite** — Fast development server and build tool
- **Framer Motion** — Smooth animations (floating particles, scan lines, pulsing effects)
- **React Dropzone** — Drag-and-drop file upload
- **React Hot Toast** — Notification popups
- **Axios** — Sends HTTP requests to the backend

### Backend (The Engine)
- **FastAPI** — Python web framework that handles API requests
- **PyTorch** — Deep learning library that runs the AI models
- **HuggingFace Transformers** — Library providing pre-trained AI models
- **PIL (Pillow)** — Image processing (resize, convert, normalize)
- **SQLAlchemy + SQLite** — Database for storing prediction history

### AI Infrastructure
- **Vision Transformer (ViT)** — The neural network architecture used by all 3 models
- **Apple Metal (MPS)** — GPU acceleration on Mac M1/M2 chips for fast inference
- **HuggingFace Hub** — Where models are downloaded from (~1.4 GB total)

---

## Part 4 — What Is a Neural Network?

A neural network is a system of mathematical functions loosely inspired by the human brain. It takes an input (like an image), passes it through many layers of calculations, and produces an output (like "FAKE").

### Neurons and Layers
Each layer contains thousands of mathematical units called neurons. Each neuron:
1. Takes numbers as input
2. Multiplies them by learned weights
3. Adds a bias value
4. Passes the result through an activation function

Layers stack on top of each other. Early layers detect simple patterns (edges, colors). Deeper layers detect complex patterns (faces, textures, semantic content).

### Training
A neural network learns by:
1. Making a prediction on a labeled example
2. Comparing the prediction to the correct answer (computing loss)
3. Adjusting the weights slightly to reduce the error (backpropagation + gradient descent)
4. Repeating millions of times until the model is accurate

This project does NOT train models from scratch. It uses models that were already trained by researchers and made available publicly.

---

## Part 5 — What Is a Vision Transformer (ViT)?

The Vision Transformer is the specific neural network architecture used by all 3 models in this project.

### Background
Before ViT, image classification used Convolutional Neural Networks (CNNs) — networks that scan images with small filters to detect local patterns. In 2020, Google researchers asked: what if we used Transformers (the architecture behind GPT and BERT) on images instead?

The result was ViT — and it outperformed CNNs on many tasks.

### How ViT Processes an Image

**Step 1 — Divide the image into patches**
A 224×224 pixel image is divided into a grid of 16×16 pixel patches.
- 224 ÷ 16 = 14 patches per row
- 14 × 14 = 196 patches total
Each patch becomes a "token" — similar to how a word is a token in text.

**Step 2 — Embed each patch**
Each 16×16 patch (768 pixel values in RGB) is flattened into a 1D vector, then projected through a linear layer into a 768-dimensional embedding. This converts the raw pixel data into a compact representation the model can work with.

**Step 3 — Add position encoding**
Unlike CNNs, Transformers have no built-in sense of spatial order. So each patch embedding gets a positional encoding added — a learned vector that tells the model "you are patch number 47, at row 3, column 5."

**Step 4 — Add a [CLS] token**
A special learnable token called [CLS] (classification) is prepended to the sequence of 196 patch embeddings. By the end of the network, this token will contain a compressed understanding of the entire image.

**Step 5 — Multi-head Self-Attention**
This is the core of the Transformer. Every patch can "attend" to every other patch — meaning the model learns which parts of the image are most relevant to each other.

For deepfake detection, this is crucial. If a face has an unnatural blending boundary, the attention mechanism can connect the face region to the background and detect the inconsistency — something local CNN filters would miss.

**Step 6 — Feed-Forward Layers**
After attention, each token passes through a small feed-forward neural network to further transform the representations.

**Step 7 — Repeat (12 layers total)**
Steps 5 and 6 repeat 12 times in ViT-Base. Each layer refines the understanding of the image.

**Step 8 — Classification**
The [CLS] token's final representation is passed through a linear layer that outputs 2 scores — one for REAL, one for FAKE. These are called logits.

---

## Part 6 — What Is Softmax?

After the model outputs raw scores (logits) for REAL and FAKE, we need to convert those into probabilities.

**Softmax** is the mathematical function that does this.

### Formula
```
probability(class i) = e^(score_i) / sum of e^(all scores)
```

### Example
```
Raw scores (logits):   REAL = -1.5,   FAKE = 3.2
Exponentials:          REAL = 0.22,   FAKE = 24.5
Sum of exponentials:   24.72
Probabilities:         REAL = 0.9%,   FAKE = 99.1%
```

The outputs always sum to 100%. This is what lets us say "the model is 99.1% confident this is fake."

---

## Part 7 — What Is Transfer Learning?

Training a ViT from scratch requires:
- Millions of labeled images
- Weeks of compute time on hundreds of GPUs
- Enormous financial cost

Transfer learning solves this. The idea is simple: a model trained on one large task has already learned general knowledge about images — edges, textures, shapes, lighting, faces. This knowledge transfers to a new task.

### How it works in this project

1. **Pre-training:** Google trains ViT on ImageNet-21k — 14 million images across 21,000 categories. The model learns to recognize thousands of object types. This gives it a rich general understanding of visual content.

2. **Transfer:** The pre-trained model weights are downloaded and used as the starting point.

3. **Replace the head:** The final classification layer (which outputs 21,000 class scores) is replaced with a new one that outputs 2 scores — REAL and FAKE.

4. **Fine-tune:** The entire model (or just the new head) is trained on the specific deepfake dataset. Because the model already understands images, it only needs to learn the difference between real and fake — not how to process images from scratch.

### Why transfer learning produces better results
- The model starts with 14 million images worth of visual knowledge
- Fine-tuning on even 200K deepfake images produces strong results
- Without transfer learning, 200K images would not be enough to train a ViT

---

## Part 8 — What Is Fine-Tuning?

Fine-tuning is the process of continuing to train a pre-trained model on a new, specific dataset.

### Process
```
Pre-trained ViT (knows general images)
              │
     Replace classification head
     (21000 classes → 2 classes: REAL/FAKE)
              │
     Train on deepfake dataset
     (small learning rate to preserve
      existing knowledge)
              │
Fine-tuned deepfake detector
```

### Learning rate matters
During fine-tuning, a very small learning rate is used (e.g. 0.00002). This ensures the model updates its weights gently — preserving the valuable visual knowledge from pre-training while adapting to the new task.

### What each model was fine-tuned on

**dima806/ai_vs_real_image_detection**
Fine-tuned on a large balanced dataset of AI-generated images vs real photographs. Covers multiple AI generators, giving it broad generalization ability. Achieves 98.25% accuracy on its test set.

**prithivMLmods/Deep-Fake-Detector-v2-Model**
Fine-tuned on a deepfake dataset covering facial manipulation, face-swaps, and identity replacement. Updated February 2025. Achieves 92.12% accuracy. Best at catching manipulated faces.

**haywoodsloan/ai-image-detector-deploy**
Fine-tuned specifically on outputs from modern commercial AI generators — Midjourney, DALL-E, Stable Diffusion. Best at catching photorealistic AI images from today's most popular tools.

---

## Part 9 — What Is Ensemble Learning?

An ensemble combines multiple models and aggregates their outputs for a more reliable prediction.

### Why one model is not enough
Every model has blind spots — images it consistently gets wrong due to its training data distribution. A single model trained on one dataset will fail on image types it has never seen.

An ensemble fixes this because:
- Different models were trained on different data
- Their errors are largely independent
- When averaged, errors cancel out and correct predictions reinforce each other

### This project's ensemble approach — Probability Averaging

Each model produces a fake probability (0.0 to 1.0). These are averaged:

```
Model 1 fake probability:  0.72
Model 2 fake probability:  0.68
Model 3 fake probability:  0.65
─────────────────────────────────
Average:                   0.683

0.683 ≥ 0.55 (threshold) → FAKE
```

### Why 55% threshold instead of 50%?
At 50%, even a tiny majority tips the verdict to FAKE. This causes real images (especially professional photos with smooth lighting) to be mislabeled. At 55%, the ensemble needs clearer fake evidence before committing to a FAKE verdict — reducing false positives while still catching clear fakes.

---

## Part 10 — The Three Models Explained

### Model 1 — dima806/ai_vs_real_image_detection
| Property | Value |
|---|---|
| Architecture | ViT-Base/16 |
| Parameters | 86 million |
| Accuracy | 98.25% |
| Input size | 224×224 pixels |
| Labels | {0: REAL, 1: FAKE} |
| Specialty | General AI-generated image detection |

This model was trained on a large, balanced dataset of AI-generated images vs real photographs. It learns the statistical differences between natural images (captured by cameras) and synthetic images (created by neural networks). Natural images have specific noise patterns, lens characteristics, and lighting physics that AI generators subtly violate.

---

### Model 2 — prithivMLmods/Deep-Fake-Detector-v2-Model
| Property | Value |
|---|---|
| Architecture | ViT-Base/16 |
| Parameters | 86 million |
| Accuracy | 92.12% |
| Updated | February 2025 |
| Labels | {0: Realism, 1: Deepfake} |
| Specialty | Face manipulation and deepfakes |

This model specializes in detecting manipulated faces — face-swaps where one person's face is replaced with another's, facial attribute editing, and identity replacement. It was trained on deepfake datasets specifically targeting facial artifacts: blending boundaries, unnatural skin texture, mismatched lighting between face and background.

---

### Model 3 — haywoodsloan/ai-image-detector-deploy
| Property | Value |
|---|---|
| Architecture | ViT-Base/16 |
| Parameters | 86 million |
| Input size | 224×224 pixels |
| Labels | {0: artificial, 1: real} |
| Specialty | Modern AI generators (Midjourney, DALL-E, SD) |

This model was trained on outputs from the most popular modern AI image generators. It learns the specific visual signatures of each generator — Midjourney's characteristic cinematic lighting and perfect composition, DALL-E's specific rendering style, Stable Diffusion's texture patterns. It is the most effective model in the ensemble for catching modern AI-generated photorealistic images.

---

## Part 11 — Fake Type Classification

After the ensemble reaches a FAKE verdict, the system determines *what kind* of fake it is.

### How it works
The model with the highest fake probability is considered the "dominant detector." Each model has a specialty, and the dominant model's specialty becomes the fake type label shown to the user.

```python
top_model = max(results, key=lambda r: r["fake_prob"])
fake_type = MODEL_SPECIALTIES[top_model]["type"]
```

### Fake type categories

**AI-Generated Image**
Detected by `dima806`. The image was synthesized by an AI model — it was never a real photograph. The entire image was generated pixel-by-pixel by a neural network.
Tags: AI-Generated, Synthetic

**Deepfake / Face Manipulation**
Detected by `prithivMLmods`. A real image was taken and a face was replaced or digitally altered using AI. The background may be real, but the face is not.
Tags: Face-Swap, Deepfake

**Modern AI Generator**
Detected by `haywoodsloan`. The image bears the signature of a modern commercial AI generator — Midjourney, DALL-E, or Stable Diffusion.
Tags: Midjourney, DALL-E, Stable Diffusion

---

## Part 12 — Label Override System

Different models use different words for their output classes. Some say "REAL"/"FAKE", some say "Realism"/"Deepfake", some say "artificial"/"human". The label_override system ensures the code always maps to the right index regardless of naming:

```python
MODEL_LABEL_OVERRIDES = {
    "dima806/ai_vs_real_image_detection":        {"real_idx": 0, "fake_idx": 1},
    "prithivMLmods/Deep-Fake-Detector-v2-Model": {"real_idx": 0, "fake_idx": 1},
    "haywoodsloan/ai-image-detector-deploy":     {"real_idx": 1, "fake_idx": 0},
}
```

Without this, a model that puts fake at index 0 instead of index 1 would have its predictions completely inverted — calling every fake image real and every real image fake. This is a critical correctness requirement.

---

## Part 13 — GPU Acceleration (Apple Metal / MPS)

### Why GPU matters
Running a 86-million-parameter ViT on CPU takes 5–8 seconds per model (15–24 seconds for all 3). On an Apple M1/M2 GPU (Metal Performance Shaders — MPS), this drops to under 0.4 seconds per model (~1 second total for the ensemble).

### How it works
PyTorch supports MPS as a compute backend. The model and all input tensors are moved to the MPS device:
```python
device = torch.device("mps")
model = model.to(device)        # 86M parameters live on GPU
inputs = inputs.to(device)      # Image tensor on GPU
outputs = model(**inputs)       # All math runs on GPU
```

The GPU can execute thousands of matrix multiplications in parallel — exactly what transformer attention layers require. This parallelism is why inference is 15x faster than CPU.

---

## Part 14 — The Prediction History System

Every prediction is saved to a SQLite database. This enables:
- The **History tab** — browse all previous predictions
- The **Statistics tab** — total analyzed, fake %, average confidence, inference time

### What gets stored per prediction
- Filename
- Prediction (REAL/FAKE)
- Confidence score
- Real probability
- Fake probability
- Inference time
- Timestamp

---

## Part 15 — Why Deepfake Detection Is Hard

### The Arms Race
AI image generation and AI image detection are in a constant arms race. As detectors improve, generator researchers study the detectors and update their models to avoid triggering them. As generators improve, detector researchers study the new output and retrain detectors.

There is no permanent solution — both sides continuously evolve.

### Detection rates for modern generators (2024 research)
| Generator | Year | Detection Rate |
|---|---|---|
| ProGAN | 2018 | ~95% |
| StyleGAN2 | 2020 | ~80% |
| Stable Diffusion v1 | 2022 | ~70% |
| Midjourney v5 | 2023 | ~45% |
| DALL-E 3 | 2023 | ~31% |
| Midjourney v7 | 2024 | ~24% |
| Flux Dev | 2024 | ~21% |

### Training distribution mismatch
A model only detects what it was trained to detect. A model trained on Stable Diffusion outputs may fail on Midjourney outputs because the artifacts are different. The only solution is training on diverse, up-to-date datasets — which is why using multiple models trained on different data (ensemble) is better than any single model.

### The stylized art problem
All models in this project were trained on photorealistic images. Stylized artwork, illustrations, dark atmospheric images, and anime-style content have fundamentally different statistical properties. These models will under-perform on non-photorealistic AI art — this is a known limitation of all public deepfake detection models as of 2025.

---

## Part 16 — Project Limitations and Future Improvements

### Current limitations
1. Struggles with stylized/non-photorealistic AI art
2. May label heavily edited real photos as fake (aggressive post-processing mimics AI artifacts)
3. Modern generators (Midjourney v7, Flux) have very low detection rates industry-wide
4. Video analysis is slower — frame-by-frame processing

### Potential improvements
1. **Train on GenImage dataset** — 2.7 million images from Midjourney, DALL-E, SD, and 5 other generators — would dramatically improve coverage
2. **Frequency domain analysis** — AI images have detectable artifacts in the DCT/FFT frequency domain that ViT models miss
3. **Weighted ensemble** — give higher-accuracy models more voting weight instead of equal weighting
4. **Larger model** — ViT-Large (307M parameters) would be more accurate but slower
5. **Model updates** — retrain quarterly as new generators emerge

---

## Summary Table

| Term | Simple Explanation |
|---|---|
| Neural Network | A system of math functions that learns patterns from data |
| Vision Transformer (ViT) | Neural network that splits images into patches and uses attention |
| Self-Attention | Mechanism that lets every part of an image "look at" every other part |
| Transfer Learning | Reusing a model trained on one task for a different, related task |
| Fine-Tuning | Continuing training a pre-trained model on new specific data |
| Softmax | Converts raw model scores into probabilities that sum to 100% |
| Binary Classification | Deciding between exactly two categories (REAL or FAKE) |
| Ensemble | Combining multiple models to get a better final prediction |
| Decision Threshold | The minimum fake confidence (55%) required to call something FAKE |
| Label Override | Hardcoded mapping ensuring each model's indices are interpreted correctly |
| Fake Type | Classification of *what kind* of fake was detected |
| MPS / Metal | Apple GPU used to run AI models 15x faster than CPU |
| Logits | Raw unnormalized scores output by the final model layer |
| Model Cache | Folder storing downloaded model weights (~1.4 GB) |
| Inference | Running a trained model on new data to get a prediction |
