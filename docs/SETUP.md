# Environment Setup Guide

## Prerequisites

- Windows 11
- NVIDIA RTX 5090 (32GB VRAM)
- CUDA 12.9
- Miniconda3 or Anaconda
- Git LFS (for downloading models)

## Step 1: Create Conda Environment

```bash
cd /c/Users/07013/Desktop/vlm-gui-automation
conda create -n vlm-gui python=3.11 -y
conda activate vlm-gui
```

## Step 2: Install PyTorch with CUDA Support

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verify installation:
```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
```

Expected output:
```
PyTorch version: 2.1.x+cu121
CUDA available: True
CUDA version: 12.1
```

## Step 3: Install VLM Dependencies

### Option A: vLLM (Recommended)

```bash
pip install vllm
pip install transformers accelerate bitsandbytes
```

### Option B: LMDeploy (Alternative)

```bash
pip install lmdeploy
```

## Step 4: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Key packages:
- FastAPI + Uvicorn (API server)
- PyAutoGUI (GUI automation)
- Playwright (browser automation)
- Pillow + OpenCV (image processing)

## Step 5: Download VLM Model

### Qwen2.5-VL-32B-Instruct (Primary)

```bash
# Install Git LFS first
git lfs install

# Clone model (this will take a while, ~60GB)
mkdir -p models
cd models
git clone https://huggingface.co/Qwen/Qwen2.5-VL-32B-Instruct
```

### Alternative: Download via Hugging Face CLI

```bash
pip install huggingface-hub
huggingface-cli login  # Optional, for gated models
huggingface-cli download Qwen/Qwen2.5-VL-32B-Instruct --local-dir models/Qwen2.5-VL-32B-Instruct
```

## Step 6: Test VLM Inference

```bash
cd /c/Users/07013/Desktop/vlm-gui-automation
conda activate vlm-gui
python backend/test_vlm.py
```

Expected: VLM loads successfully, inference latency < 5 seconds

## Step 7: Install Frontend Dependencies (Phase 1+)

```bash
cd frontend
npm install
```

## Hardware Verification

Check GPU status:
```bash
nvidia-smi
```

Expected:
- GPU: NVIDIA GeForce RTX 5090
- Memory: 32607 MiB
- CUDA Version: 12.9

## Troubleshooting

### Issue: PyTorch CUDA not available

**Solution**: Reinstall PyTorch with correct CUDA version
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Issue: vLLM installation fails

**Symptom**: "No matching distribution found for vLLM"

**Solution 1**: vLLM may not support Python 3.13+ yet. Use Python 3.11 (already done).

**Solution 2**: Build from source
```bash
pip install git+https://github.com/vllm-project/vllm.git
```

**Solution 3**: Use LMDeploy instead
```bash
pip install lmdeploy
```

### Issue: Out of memory during inference

**Solution**: Enable 4bit quantization
```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-VL-32B-Instruct",
    quantization_config=quantization_config,
    device_map="auto"
)
```

### Issue: Git LFS download too slow

**Solution**: Use mirror or download via browser
- HuggingFace mirror: `export HF_ENDPOINT=https://hf-mirror.com`
- Manual download: Download model files from https://huggingface.co/Qwen/Qwen2.5-VL-32B-Instruct/tree/main

## Development Environment

### VS Code Extensions (Recommended)

- Python
- Pylance
- Jupyter
- ESLint (for frontend)
- Prettier

### Conda Environment Export

Save environment for reproducibility:
```bash
conda env export > environment.yml
```

Recreate from file:
```bash
conda env create -f environment.yml
```

## Next Steps

After completing setup:
1. Run test_vlm.py to verify VLM works
2. Measure inference latency and VRAM usage
3. Proceed to Phase 1: FastAPI server implementation

---

**Last Updated**: 2025-12-11
**Status**: Phase 0 - Environment Setup
