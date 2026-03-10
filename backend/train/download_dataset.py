"""
Download and prepare dataset for training
Option 1: CIFAKE from Hugging Face (automatic)
Option 2: 140k Real and Fake Faces from Kaggle (requires kaggle API)
"""

import os
from pathlib import Path
import shutil


def download_cifake():
    """Download CIFAKE dataset from Hugging Face (easiest option)"""
    print("Downloading CIFAKE dataset from Hugging Face...")
    print("This dataset contains Real vs AI-Generated images")

    from datasets import load_dataset

    dataset = load_dataset("cifake", "default", trust_remote_code=True)

    print(f"\n✅ Dataset loaded!")
    print(f"Training samples: {len(dataset['train'])}")
    print(f"Test samples: {len(dataset['test'])}")

    # Show sample distribution
    train_labels = dataset['train']['label']
    print(f"\nTraining distribution:")
    print(f"  Real images: {train_labels.count(0)}")
    print(f"  Fake images: {train_labels.count(1)}")

    return dataset


def download_kaggle_dataset(output_dir="./data"):
    """
    Download 140k Real and Fake Faces from Kaggle
    Requires: pip install kaggle
    And kaggle.json API credentials in ~/.kaggle/
    """
    print("Downloading 140k Real and Fake Faces dataset from Kaggle...")

    try:
        import kaggle
        kaggle.api.authenticate()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Download dataset
        kaggle.api.dataset_download_files(
            'xhlulu/140k-real-and-fake-faces',
            path=output_path,
            unzip=True
        )

        print(f"\n✅ Dataset downloaded to: {output_path}")

        # Reorganize into real/fake folders
        reorganize_kaggle_dataset(output_path)

    except ImportError:
        print("\n❌ Kaggle package not installed!")
        print("Run: pip install kaggle")
        print("Then setup kaggle.json credentials")
    except Exception as e:
        print(f"\n❌ Error downloading: {e}")
        print("Make sure you have kaggle API credentials set up")


def reorganize_kaggle_dataset(data_dir):
    """Reorganize Kaggle dataset into real/fake folders"""
    data_dir = Path(data_dir)

    real_dir = data_dir / "real"
    fake_dir = data_dir / "fake"

    real_dir.mkdir(exist_ok=True)
    fake_dir.mkdir(exist_ok=True)

    # Move files based on folder names in the dataset
    for subdir in data_dir.iterdir():
        if subdir.is_dir() and subdir.name not in ['real', 'fake']:
            if 'real' in subdir.name.lower():
                for f in subdir.glob('*'):
                    if f.is_file():
                        shutil.move(str(f), real_dir / f.name)
            elif 'fake' in subdir.name.lower():
                for f in subdir.glob('*'):
                    if f.is_file():
                        shutil.move(str(f), fake_dir / f.name)

    print(f"Reorganized dataset:")
    print(f"  Real images: {len(list(real_dir.glob('*')))}")
    print(f"  Fake images: {len(list(fake_dir.glob('*')))}")


def prepare_custom_dataset(source_real, source_fake, output_dir="./data"):
    """
    Prepare custom dataset from your own images

    Args:
        source_real: Path to folder containing real images
        source_fake: Path to folder containing fake/AI images
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    real_dir = output_path / "real"
    fake_dir = output_path / "fake"

    real_dir.mkdir(parents=True, exist_ok=True)
    fake_dir.mkdir(parents=True, exist_ok=True)

    # Copy real images
    source_real = Path(source_real)
    for img in source_real.glob("*"):
        if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            shutil.copy(img, real_dir / img.name)

    # Copy fake images
    source_fake = Path(source_fake)
    for img in source_fake.glob("*"):
        if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            shutil.copy(img, fake_dir / img.name)

    print(f"Dataset prepared at: {output_path}")
    print(f"  Real images: {len(list(real_dir.glob('*')))}")
    print(f"  Fake images: {len(list(fake_dir.glob('*')))}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download/prepare training dataset")
    parser.add_argument("--source", type=str, default="huggingface",
                        choices=["huggingface", "kaggle"],
                        help="Dataset source")
    parser.add_argument("--output", type=str, default="./data",
                        help="Output directory for dataset")

    args = parser.parse_args()

    if args.source == "huggingface":
        download_cifake()
        print("\n📌 To train, run:")
        print("   python train_model.py")
    else:
        download_kaggle_dataset(args.output)
        print("\n📌 To train, run:")
        print(f"   python train_model.py --data_dir {args.output}")
