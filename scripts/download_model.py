#!/usr/bin/env python3
"""
Download Qwen2.5-VL-32B-Instruct model from Hugging Face.

This script uses huggingface-hub to download the model efficiently
with resume support and progress tracking.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
from tqdm import tqdm


def download_qwen_model():
    """Download Qwen2.5-VL-32B-Instruct model."""

    model_name = "Qwen/Qwen2.5-VL-32B-Instruct"
    local_dir = Path("models/Qwen2.5-VL-32B-Instruct")

    print("=" * 70)
    print("Qwen2.5-VL-32B-Instruct Model Download")
    print("=" * 70)
    print(f"Model: {model_name}")
    print(f"Destination: {local_dir}")
    print()
    print("Note: This model is ~60GB and will take time to download.")
    print("The download supports resume if interrupted.")
    print()

    # Create models directory
    local_dir.parent.mkdir(parents=True, exist_ok=True)

    try:
        print("Starting download...")
        snapshot_download(
            repo_id=model_name,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False,  # Copy files instead of symlinks on Windows
            resume_download=True,  # Enable resume
            max_workers=4  # Parallel downloads
        )

        print()
        print("=" * 70)
        print("Download completed successfully!")
        print("=" * 70)
        print(f"Model saved to: {local_dir.absolute()}")
        print()
        print("Next steps:")
        print("1. Run: python backend/test_vlm.py")
        print("2. Verify model loads correctly")
        print("3. Measure inference latency")
        print()

        return True

    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        print("You can resume by running this script again.")
        return False

    except Exception as e:
        print(f"\n\nError downloading model: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Ensure enough disk space (~60GB)")
        print("3. Try: pip install --upgrade huggingface-hub")
        print("4. Check Hugging Face status: https://status.huggingface.co/")
        return False


def check_model_exists():
    """Check if model already downloaded."""
    model_dir = Path("models/Qwen2.5-VL-32B-Instruct")

    if model_dir.exists():
        print(f"Model directory found: {model_dir}")

        # Check for key files
        config_file = model_dir / "config.json"
        if config_file.exists():
            print("Model appears to be already downloaded.")
            print()
            response = input("Re-download? (y/N): ").strip().lower()
            return response == 'y'

    return True


def main():
    """Main entry point."""

    # Check if we need to download
    if not check_model_exists():
        print("Skipping download.")
        return 0

    # Download model
    success = download_qwen_model()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
