"""
VLM Service - Screen Analysis using Qwen2.5-VL-32B-Instruct

Handles VLM model loading and screen analysis.
"""

from pathlib import Path
from typing import Dict, Any, List
from PIL import Image
import torch
import time


class VLMService:
    """Service for VLM-based screen analysis."""

    def __init__(self, model_dir: str, device: str = "cuda", use_dummy: bool = False):
        """
        Initialize VLM service.

        Args:
            model_dir: Path to model directory
            device: Device to use (cuda/cpu)
            use_dummy: If True, use dummy responses for testing
        """
        self.model_dir = Path(model_dir)
        self.device = device
        self.use_dummy = use_dummy
        self.model = None
        self.processor = None

        if not use_dummy:
            self._load_model()

    def _load_model(self):
        """Load Qwen2.5-VL-32B-Instruct model."""
        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"Model directory not found: {self.model_dir}\n"
                f"Run: python scripts/download_model.py"
            )

        print(f"Loading VLM model from {self.model_dir}...")
        start_time = time.time()

        try:
            from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

            # Load processor
            self.processor = AutoProcessor.from_pretrained(
                str(self.model_dir),
                trust_remote_code=True
            )
            print("[OK] Processor loaded")

            # Load model with 4bit quantization
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                str(self.model_dir),
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True
            )
            print("[OK] Model loaded")

            load_time = time.time() - start_time
            print(f"Model loading time: {load_time:.2f}s")

            # Check memory usage
            if torch.cuda.is_available():
                memory_used = torch.cuda.memory_allocated(0) / 1e9
                print(f"GPU memory used: {memory_used:.2f} GB")

        except Exception as e:
            print(f"[ERROR] Model loading failed: {e}")
            print("Falling back to dummy mode")
            self.use_dummy = True

    def analyze(self, image: Image.Image, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze screen image and extract UI elements.

        Args:
            image: PIL Image of the screen
            prompt: Optional custom prompt (uses default if None)

        Returns:
            Dict with:
                - summary: str (screen description)
                - elements: List[Dict] (detected UI elements)
                - processing_time: float (seconds)
        """
        start_time = time.time()

        if self.use_dummy:
            return self._dummy_analyze(image)

        # Default prompt for screen analysis
        if prompt is None:
            prompt = """Analyze this screenshot and provide:
1. A brief summary of what's visible (2-3 sentences)
2. A list of all interactive UI elements (buttons, links, input fields, menus)

For each element, provide:
- type: button/input/link/menu/dropdown
- text: visible text on the element
- approximate location: top-left/top-right/center/bottom-left/bottom-right

Format your response as JSON."""

        try:
            # Prepare inputs
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]

            # Apply chat template
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Prepare model inputs
            inputs = self.processor(
                text=[text],
                images=[image],
                return_tensors="pt"
            ).to(self.device)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    do_sample=False  # Greedy decoding for consistency
                )

            # Decode response
            generated_text = self.processor.batch_decode(
                outputs,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]

            # Parse response
            result = self._parse_vlm_output(generated_text)
            result["processing_time"] = time.time() - start_time

            return result

        except Exception as e:
            print(f"[ERROR] VLM inference failed: {e}")
            return {
                "summary": f"Error during analysis: {str(e)}",
                "elements": [],
                "processing_time": time.time() - start_time
            }

    def _dummy_analyze(self, image: Image.Image) -> Dict[str, Any]:
        """Dummy analysis for testing without model."""
        time.sleep(0.5)  # Simulate processing time

        return {
            "summary": "ダミーモード: Chrome ブラウザが表示されています。検索バーと複数のタブが見えます。",
            "elements": [
                {
                    "type": "button",
                    "text": "新しいタブ",
                    "bbox": [100, 50, 200, 80],
                    "confidence": 0.95
                },
                {
                    "type": "input",
                    "text": "検索またはURLを入力",
                    "bbox": [300, 50, 800, 80],
                    "confidence": 0.90
                },
                {
                    "type": "button",
                    "text": "設定",
                    "bbox": [1200, 50, 1250, 80],
                    "confidence": 0.85
                }
            ],
            "processing_time": 0.5
        }

    def _parse_vlm_output(self, text: str) -> Dict[str, Any]:
        """
        Parse VLM output into structured format.

        Args:
            text: Raw VLM output text

        Returns:
            Dict with summary and elements
        """
        # TODO: Implement robust JSON parsing
        # For now, extract text-based summary and create basic structure

        # Try to extract JSON if present
        import json
        import re

        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return {
                    "summary": data.get("summary", text[:200]),
                    "elements": data.get("elements", [])
                }
            except json.JSONDecodeError:
                pass

        # Fallback: text-based extraction
        return {
            "summary": text[:500],  # First 500 chars as summary
            "elements": []  # Will be improved with better prompt engineering
        }

    def is_ready(self) -> bool:
        """Check if service is ready for inference."""
        return self.use_dummy or (self.model is not None and self.processor is not None)


# Global instance (will be initialized in main.py)
_vlm_service: VLMService = None


def get_vlm_service() -> VLMService:
    """Get global VLM service instance."""
    global _vlm_service
    if _vlm_service is None:
        raise RuntimeError("VLM service not initialized. Call init_vlm_service() first.")
    return _vlm_service


def init_vlm_service(model_dir: str, device: str = "cuda", use_dummy: bool = False):
    """Initialize global VLM service."""
    global _vlm_service
    _vlm_service = VLMService(model_dir=model_dir, device=device, use_dummy=use_dummy)
    return _vlm_service
