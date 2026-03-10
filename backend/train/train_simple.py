"""
Simple Fine-tuning Script for Deepfake Detection
Memory-efficient version using streaming
"""

import torch
from transformers import (
    AutoModelForImageClassification,
    AutoImageProcessor,
    TrainingArguments,
    Trainer
)
from datasets import load_dataset
from PIL import Image
import numpy as np
import evaluate

# Configuration
MODEL_NAME = "dima806/deepfake_vs_real_image_detection"
OUTPUT_DIR = "./trained_model"
NUM_SAMPLES = 500  # Small subset for demo
BATCH_SIZE = 8
EPOCHS = 1

print("=" * 50)
print("Deepfake Detection - Simple Training")
print("=" * 50)

# Setup device
if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
print(f"Using device: {device}")

# Load processor
print(f"\nLoading model: {MODEL_NAME}")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

# Load model
model = AutoModelForImageClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
    id2label={0: "real", 1: "fake"},
    label2id={"real": 0, "fake": 1},
    ignore_mismatched_sizes=True
)

# Load dataset with streaming to save memory
print("\nLoading dataset (streaming mode)...")
dataset = load_dataset(
    "prithivMLmods/AI-vs-Deepfake-vs-Real",
    split="train",
    streaming=True
)

# Process and collect samples
print(f"Collecting {NUM_SAMPLES} samples...")
train_data = []
val_data = []
count = 0

for item in dataset:
    if count >= NUM_SAMPLES:
        break

    # Map labels: Real(2) = 0, AI(0) or Deepfake(1) = 1 (fake)
    label = 0 if item['label'] == 2 else 1

    # 80% train, 20% val
    if count % 5 == 0:
        val_data.append({'image': item['image'], 'label': label})
    else:
        train_data.append({'image': item['image'], 'label': label})

    count += 1
    if count % 500 == 0:
        print(f"  Processed {count}/{NUM_SAMPLES} samples...")

print(f"\nTrain samples: {len(train_data)}")
print(f"Val samples: {len(val_data)}")

# Preprocessing function
def preprocess(example):
    image = example['image'].convert('RGB')
    inputs = processor(images=image, return_tensors="pt")
    return {
        'pixel_values': inputs['pixel_values'].squeeze(0),
        'labels': torch.tensor(example['label'])
    }

# Create simple datasets
from torch.utils.data import Dataset

class SimpleDataset(Dataset):
    def __init__(self, data, processor):
        self.data = data
        self.processor = processor

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        image = item['image'].convert('RGB')
        inputs = self.processor(images=image, return_tensors="pt")
        return {
            'pixel_values': inputs['pixel_values'].squeeze(0),
            'labels': torch.tensor(item['label'])
        }

train_dataset = SimpleDataset(train_data, processor)
val_dataset = SimpleDataset(val_data, processor)

# Free memory
del train_data, val_data

# Metric
accuracy = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)

# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    learning_rate=3e-5,
    warmup_steps=50,
    weight_decay=0.01,
    logging_steps=25,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    push_to_hub=False,
    report_to="none",
    dataloader_num_workers=0,  # Avoid multiprocessing issues
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

# Train
print("\n" + "=" * 50)
print("Starting training...")
print("=" * 50)

trainer.train()

# Save
print(f"\nSaving model to: {OUTPUT_DIR}")
trainer.save_model(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)

# Final evaluation
print("\n" + "=" * 50)
print("Final Evaluation")
print("=" * 50)
results = trainer.evaluate()
print(f"Accuracy: {results['eval_accuracy']:.4f}")

print("\n✅ Training complete!")
print(f"Model saved to: {OUTPUT_DIR}")
