"""
Fine-tune Deepfake Detection Model
Uses 140k Real and Fake Faces dataset
"""

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from transformers import AutoModelForImageClassification, AutoImageProcessor, TrainingArguments, Trainer
from PIL import Image
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
import numpy as np
from datasets import load_dataset
import evaluate

# Configuration
MODEL_NAME = "dima806/deepfake_vs_real_image_detection"
OUTPUT_DIR = "./trained_model"
BATCH_SIZE = 32
EPOCHS = 2
LEARNING_RATE = 3e-5


def setup_device():
    """Setup compute device"""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class DeepfakeDataset(Dataset):
    """Custom dataset for deepfake detection"""

    def __init__(self, image_paths, labels, processor):
        self.image_paths = image_paths
        self.labels = labels
        self.processor = processor

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert('RGB')
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.squeeze(0) for k, v in inputs.items()}
        inputs['labels'] = torch.tensor(self.labels[idx])
        return inputs


def load_local_dataset(data_dir):
    """
    Load dataset from local directory
    Expected structure:
        data_dir/
            real/
                image1.jpg
                image2.jpg
            fake/
                image1.jpg
                image2.jpg
    """
    image_paths = []
    labels = []

    real_dir = Path(data_dir) / "real"
    fake_dir = Path(data_dir) / "fake"

    # Load real images (label = 0)
    if real_dir.exists():
        for img_path in real_dir.glob("*"):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                image_paths.append(str(img_path))
                labels.append(0)

    # Load fake images (label = 1)
    if fake_dir.exists():
        for img_path in fake_dir.glob("*"):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                image_paths.append(str(img_path))
                labels.append(1)

    return image_paths, labels


def compute_metrics(eval_pred):
    """Compute accuracy metric"""
    accuracy = evaluate.load("accuracy")
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)


def train(data_dir=None):
    """Main training function"""
    print("=" * 50)
    print("Deepfake Detection Model Fine-tuning")
    print("=" * 50)

    device = setup_device()
    print(f"Using device: {device}")

    # Load processor and model
    print(f"\nLoading base model: {MODEL_NAME}")
    processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
    model = AutoModelForImageClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2,
        id2label={0: "real", 1: "fake"},
        label2id={"real": 0, "fake": 1},
        ignore_mismatched_sizes=True
    )

    # Load dataset
    if data_dir and Path(data_dir).exists():
        print(f"\nLoading local dataset from: {data_dir}")
        image_paths, labels = load_local_dataset(data_dir)

        if len(image_paths) == 0:
            print("ERROR: No images found in dataset directory!")
            print(f"Expected structure:\n  {data_dir}/real/*.jpg\n  {data_dir}/fake/*.jpg")
            return

        # Split into train/val
        train_paths, val_paths, train_labels, val_labels = train_test_split(
            image_paths, labels, test_size=0.2, random_state=42, stratify=labels
        )

        print(f"Training samples: {len(train_paths)}")
        print(f"Validation samples: {len(val_paths)}")

        # Create datasets
        train_dataset = DeepfakeDataset(train_paths, train_labels, processor)
        val_dataset = DeepfakeDataset(val_paths, val_labels, processor)

    else:
        # Use Hugging Face dataset
        print("\nLoading dataset from Hugging Face: prithivMLmods/AI-vs-Deepfake-vs-Real")
        print("This may take a few minutes to download...")

        dataset = load_dataset("prithivMLmods/AI-vs-Deepfake-vs-Real")

        # Dataset has 'train' split with 'image' and 'label' columns
        # Label: 0=AI, 1=Deepfake, 2=Real
        # We'll map: Real(2) -> 0, AI/Deepfake(0,1) -> 1 (fake)

        all_images = []
        all_labels = []

        print("Processing images...")
        for item in dataset['train']:
            all_images.append(item['image'])
            # Map labels: Real(2) = 0, AI(0) or Deepfake(1) = 1 (fake)
            label = 0 if item['label'] == 2 else 1
            all_labels.append(label)

        print(f"Total images: {len(all_images)}")
        print(f"Real images: {all_labels.count(0)}")
        print(f"Fake images: {all_labels.count(1)}")

        # Split into train/val
        train_imgs, val_imgs, train_lbls, val_lbls = train_test_split(
            all_images, all_labels, test_size=0.2, random_state=42, stratify=all_labels
        )

        print(f"Training samples: {len(train_imgs)}")
        print(f"Validation samples: {len(val_imgs)}")

        # Create simple dataset class for HF images
        class HFImageDataset(Dataset):
            def __init__(self, images, labels, processor):
                self.images = images
                self.labels = labels
                self.processor = processor

            def __len__(self):
                return len(self.images)

            def __getitem__(self, idx):
                image = self.images[idx].convert('RGB')
                inputs = self.processor(images=image, return_tensors="pt")
                inputs = {k: v.squeeze(0) for k, v in inputs.items()}
                inputs['labels'] = torch.tensor(self.labels[idx])
                return inputs

        train_dataset = HFImageDataset(train_imgs, train_lbls, processor)
        val_dataset = HFImageDataset(val_imgs, val_lbls, processor)

        print(f"Training samples: {len(train_dataset)}")
        print(f"Validation samples: {len(val_dataset)}")

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        push_to_hub=False,
        report_to="none",
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

    # Save model
    print(f"\nSaving model to: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    processor.save_pretrained(OUTPUT_DIR)

    # Evaluate
    print("\n" + "=" * 50)
    print("Final Evaluation")
    print("=" * 50)
    results = trainer.evaluate()
    print(f"Accuracy: {results['eval_accuracy']:.4f}")

    print("\n✅ Training complete!")
    print(f"Model saved to: {OUTPUT_DIR}")

    return trainer


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fine-tune deepfake detection model")
    parser.add_argument("--data_dir", type=str, default=None,
                        help="Path to local dataset (with real/ and fake/ subdirs)")
    args = parser.parse_args()

    train(data_dir=args.data_dir)
