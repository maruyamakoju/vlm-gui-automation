#!/usr/bin/env python3
"""Test script to verify VLM installation and measure performance."""

import torch
import time
from pathlib import Path


def test_cuda():
    """Test CUDA availability."""
    print("=" * 70)
    print("CUDA TEST")
    print("=" * 70)
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU device: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        print(f"Current memory allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
        print("\n✓ CUDA test passed")
    else:
        print("\n✗ CUDA not available - check installation")

    print()


def test_transformers():
    """Test transformers library."""
    print("=" * 70)
    print("TRANSFORMERS TEST")
    print("=" * 70)

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        print("✓ transformers imported successfully")
        print(f"transformers version: {__import__('transformers').__version__}")
    except ImportError as e:
        print(f"✗ transformers import failed: {e}")
        return False

    print()
    return True


def test_vlm_loading():
    """Test loading Qwen2.5-VL model (if available)."""
    print("=" * 70)
    print("VLM MODEL LOADING TEST")
    print("=" * 70)

    model_path = Path("models/Qwen2.5-VL-32B-Instruct")

    if not model_path.exists():
        print(f"✗ Model not found at {model_path}")
        print("  Download model first:")
        print("  git clone https://huggingface.co/Qwen/Qwen2.5-VL-32B-Instruct models/Qwen2.5-VL-32B-Instruct")
        return False

    print(f"Model path: {model_path}")
    print("Loading model... (this may take a while)")

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

        # Use 4bit quantization to fit in memory
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16
        )

        start_time = time.time()

        tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        print("✓ Tokenizer loaded")

        model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            quantization_config=quantization_config,
            device_map="auto",
            torch_dtype=torch.float16
        )

        load_time = time.time() - start_time
        print(f"✓ Model loaded in {load_time:.2f} seconds")

        # Check memory usage
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated(0) / 1e9
            print(f"GPU memory used: {memory_used:.2f} GB")

        print("\n✓ VLM model loading test passed")
        return True

    except Exception as e:
        print(f"\n✗ Model loading failed: {e}")
        return False


def test_inference():
    """Test basic inference."""
    print("=" * 70)
    print("INFERENCE TEST")
    print("=" * 70)
    print("(Skipping for now - requires full model loading)")
    print("Will implement in next phase")
    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "VLM ENVIRONMENT TEST SUITE" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # Test 1: CUDA
    test_cuda()

    # Test 2: Transformers
    if not test_transformers():
        print("\nInstall transformers: pip install transformers accelerate")
        return

    # Test 3: VLM Loading (optional, skipped if model not downloaded)
    test_vlm_loading()

    # Test 4: Inference (future)
    test_inference()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Core dependencies: ✓")
    print("CUDA support: ✓" if torch.cuda.is_available() else "CUDA support: ✗")
    print()
    print("Next steps:")
    print("1. Download VLM model if not done:")
    print("   git clone https://huggingface.co/Qwen/Qwen2.5-VL-32B-Instruct models/Qwen2.5-VL-32B-Instruct")
    print("2. Run this script again to test model loading")
    print("3. Proceed to Phase 1: FastAPI server implementation")
    print()


if __name__ == "__main__":
    main()
