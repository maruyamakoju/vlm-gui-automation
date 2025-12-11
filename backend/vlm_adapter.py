"""
VLM Adapter Layer - Unified interface for multiple VLM backends

Phase 5-A: Abstraction layer that allows switching between:
- Dummy VLM (for testing without model)
- Qwen2.5-VL (local model)
- Claude API (cloud VLM)
- Florence-2 (lighter alternative)

This adapter provides a consistent interface regardless of the underlying VLM implementation.
"""

from typing import Any, Dict, Optional, List
from abc import ABC, abstractmethod
from pathlib import Path
from PIL import Image
import os
import time


class BaseVLMClient(ABC):
    """Abstract base class for VLM clients."""

    @abstractmethod
    def analyze_screen(
        self,
        image: Image.Image,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a GUI screenshot and extract actionable information.

        Args:
            image: PIL Image of the screen
            instruction: Natural language instruction (e.g., "Find the submit button")
            context: Optional context dict with keys like:
                - app_name: str (e.g., "Chrome", "Excel")
                - previous_actions: List[str]
                - target_element: str

        Returns:
            Dict with:
                - success: bool
                - summary: str (description of what's visible)
                - elements: List[Dict] (detected UI elements)
                - reasoning: str (VLM's reasoning)
                - processing_time: float (seconds)
        """
        raise NotImplementedError

    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the VLM client is ready for inference."""
        raise NotImplementedError


class DummyVLMClient(BaseVLMClient):
    """Dummy VLM client for testing without a real model."""

    def __init__(self):
        """Initialize dummy VLM client."""
        self.call_count = 0

    def analyze_screen(
        self,
        image: Image.Image,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return dummy analysis results."""
        start_time = time.time()
        time.sleep(0.5)  # Simulate processing time

        self.call_count += 1
        app_name = context.get("app_name", "Unknown") if context else "Unknown"

        return {
            "success": True,
            "summary": f"Dummy VLM mode: Analyzing {app_name} application (call #{self.call_count})",
            "reasoning": "This is a dummy response for testing. No actual VLM inference was performed.",
            "elements": [
                {
                    "type": "button",
                    "text": "Submit",
                    "bbox": [100, 50, 200, 80],
                    "confidence": 0.95,
                    "location": "top-left"
                },
                {
                    "type": "input",
                    "text": "Search or enter URL",
                    "bbox": [300, 50, 800, 80],
                    "confidence": 0.90,
                    "location": "top-center"
                },
                {
                    "type": "button",
                    "text": "Settings",
                    "bbox": [1200, 50, 1250, 80],
                    "confidence": 0.85,
                    "location": "top-right"
                }
            ],
            "processing_time": time.time() - start_time
        }

    def is_ready(self) -> bool:
        """Dummy client is always ready."""
        return True


class QwenVLMClient(BaseVLMClient):
    """VLM client using Qwen2.5-VL model (wraps existing VLMService)."""

    def __init__(self, model_dir: str, device: str = "cuda", use_dummy: bool = False):
        """
        Initialize Qwen VLM client.

        Args:
            model_dir: Path to Qwen model directory
            device: Device to use (cuda/cpu)
            use_dummy: If True, fall back to dummy mode
        """
        from vlm_service import VLMService

        self.vlm_service = VLMService(
            model_dir=model_dir,
            device=device,
            use_dummy=use_dummy
        )

    def analyze_screen(
        self,
        image: Image.Image,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze screen using Qwen2.5-VL model.

        Args:
            image: PIL Image
            instruction: Natural language instruction
            context: Optional context dict

        Returns:
            Standardized analysis result
        """
        # Build prompt from instruction and context
        app_name = context.get("app_name", "") if context else ""
        prompt = self._build_prompt(instruction, app_name)

        # Call underlying VLM service
        result = self.vlm_service.analyze(image=image, prompt=prompt)

        # Standardize output format
        return {
            "success": True,
            "summary": result.get("summary", ""),
            "reasoning": result.get("summary", "")[:200],  # Use summary as reasoning
            "elements": result.get("elements", []),
            "processing_time": result.get("processing_time", 0.0)
        }

    def _build_prompt(self, instruction: str, app_name: str = "") -> str:
        """Build VLM prompt from instruction and context."""
        base_prompt = """Analyze this screenshot and provide:
1. A brief summary of what's visible (2-3 sentences)
2. A list of all interactive UI elements (buttons, links, input fields, menus)

For each element, provide:
- type: button/input/link/menu/dropdown
- text: visible text on the element
- approximate location: top-left/top-right/center/bottom-left/bottom-right

Format your response as JSON."""

        if instruction:
            base_prompt += f"\n\nUser instruction: {instruction}"

        if app_name:
            base_prompt += f"\n\nApplication context: {app_name}"

        return base_prompt

    def is_ready(self) -> bool:
        """Check if Qwen VLM service is ready."""
        return self.vlm_service.is_ready()


# --- Factory function ---

def get_vlm_client(
    backend: Optional[str] = None,
    model_dir: Optional[str] = None,
    device: str = "cuda"
) -> BaseVLMClient:
    """
    Factory function to get VLM client instance.

    Args:
        backend: VLM backend to use. Options:
            - "dummy": Dummy client for testing
            - "qwen": Qwen2.5-VL local model
            - None: Auto-detect from environment (USE_DUMMY_VLM)
        model_dir: Path to model directory (for Qwen backend)
        device: Device to use (cuda/cpu)

    Returns:
        VLM client instance

    Environment variables:
        USE_DUMMY_VLM: "true" to force dummy mode (default: "false")
        VLM_MODEL_DIR: Path to Qwen model directory
    """
    # Auto-detect backend from environment
    if backend is None:
        use_dummy_env = os.getenv("USE_DUMMY_VLM", "false").lower()
        backend = "dummy" if use_dummy_env == "true" else "qwen"

    # Get model directory from environment if not specified
    if model_dir is None:
        model_dir = os.getenv("VLM_MODEL_DIR", "models/Qwen2.5-VL-32B-Instruct")

    # Create client based on backend
    if backend == "dummy":
        print("[VLM Adapter] Using Dummy VLM client")
        return DummyVLMClient()

    elif backend == "qwen":
        print(f"[VLM Adapter] Using Qwen VLM client (model_dir={model_dir})")
        # Check if model exists, fall back to dummy if not
        model_path = Path(model_dir)
        if not model_path.exists() or len(list(model_path.glob("*.safetensors"))) == 0:
            print(f"[VLM Adapter] Qwen model not found, falling back to Dummy mode")
            return DummyVLMClient()

        return QwenVLMClient(
            model_dir=model_dir,
            device=device,
            use_dummy=False
        )

    else:
        raise ValueError(f"Unknown VLM backend: {backend}. Options: dummy, qwen")


# --- Global instance management (singleton pattern) ---

_vlm_client: Optional[BaseVLMClient] = None


def get_global_vlm_client() -> BaseVLMClient:
    """
    Get global VLM client instance.

    Raises:
        RuntimeError: If client not initialized

    Returns:
        Global VLM client instance
    """
    global _vlm_client
    if _vlm_client is None:
        raise RuntimeError(
            "VLM client not initialized. Call init_global_vlm_client() first."
        )
    return _vlm_client


def init_global_vlm_client(
    backend: Optional[str] = None,
    model_dir: Optional[str] = None,
    device: str = "cuda"
) -> BaseVLMClient:
    """
    Initialize global VLM client instance.

    Args:
        backend: VLM backend to use (dummy/qwen/None for auto-detect)
        model_dir: Path to model directory
        device: Device to use (cuda/cpu)

    Returns:
        Initialized VLM client
    """
    global _vlm_client
    _vlm_client = get_vlm_client(backend=backend, model_dir=model_dir, device=device)
    print(f"[VLM Adapter] Global VLM client initialized: {type(_vlm_client).__name__}")
    return _vlm_client


def reset_global_vlm_client():
    """Reset global VLM client (for testing)."""
    global _vlm_client
    _vlm_client = None
