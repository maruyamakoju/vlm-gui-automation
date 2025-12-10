#!/usr/bin/env python3
"""
VLM GUI Automation - Backend API Server

FastAPI server providing endpoints for:
- Screen analysis (VLM inference)
- Plan generation (GPT-4 orchestration)
- Action execution
- Plan approval workflow
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from pathlib import Path
from PIL import Image
import io
import os

# Import VLM service
from vlm_service import init_vlm_service, get_vlm_service

# Initialize FastAPI app
app = FastAPI(
    title="VLM GUI Automation API",
    description="Backend API for VLM-based GUI automation",
    version="0.1.0"
)

# Enable CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to Electron app origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Startup/Shutdown Events ---

@app.on_event("startup")
async def startup_event():
    """Initialize VLM service on startup."""
    model_dir = os.getenv("VLM_MODEL_DIR", "models/Qwen2.5-VL-32B-Instruct")
    use_dummy = os.getenv("USE_DUMMY_VLM", "false").lower() == "true"

    print("=" * 70)
    print("INITIALIZING VLM SERVICE")
    print("=" * 70)
    print(f"Model directory: {model_dir}")
    print(f"Dummy mode: {use_dummy}")
    print()

    try:
        init_vlm_service(
            model_dir=model_dir,
            device="cuda" if os.path.exists("/proc/driver/nvidia") or os.name == "nt" else "cpu",
            use_dummy=use_dummy
        )
        print("[OK] VLM service initialized")
    except Exception as e:
        print(f"[WARNING] VLM service initialization failed: {e}")
        print("[INFO] Falling back to dummy mode")
        init_vlm_service(model_dir=model_dir, use_dummy=True)

    print("=" * 70)
    print()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down VLM service...")


# --- Data Models ---

class UIElement(BaseModel):
    """Represents a detected UI element."""
    type: str  # button, input, link, menu, etc.
    text: str
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float


class ScreenAnalysisResponse(BaseModel):
    """Response from screen analysis endpoint."""
    elements: List[UIElement]
    screen_description: str
    processing_time: float


class ActionStep(BaseModel):
    """Single action in a plan."""
    step: int
    action: str  # click, type, wait, press_key, etc.
    target: str
    parameters: Optional[Dict[str, Any]] = {}
    rationale: str


class PlanGenerationResponse(BaseModel):
    """Response from plan generation endpoint."""
    plan: List[ActionStep]
    estimated_duration: int  # seconds
    risk_level: str  # low, medium, high


class ActionExecutionRequest(BaseModel):
    """Request to execute a single action."""
    action: str
    target: str
    parameters: Optional[Dict[str, Any]] = {}


class ActionExecutionResponse(BaseModel):
    """Response from action execution."""
    success: bool
    message: str
    screenshot_after: Optional[str] = None  # Base64 encoded


# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "VLM GUI Automation API",
        "version": "0.1.0",
        "phase": "0 - Environment Setup"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    # TODO: Check VLM model loaded, GPU available, etc.
    return {
        "status": "ok",
        "gpu_available": False,  # TODO: Check torch.cuda.is_available()
        "vlm_loaded": False,  # TODO: Check if model is loaded
        "services": {
            "api": "running",
            "vlm": "not_loaded",
            "executor": "ready"
        }
    }


@app.post("/api/v1/analyze_screen")
async def analyze_screen(file: UploadFile = File(...)):
    """
    Analyze screenshot using VLM.

    Takes a screenshot image and returns detected UI elements with bounding boxes.

    Args:
        file: PNG/JPEG image file

    Returns:
        Dict with summary, elements, and processing_time
    """
    # Validate file type
    if file.content_type not in ("image/png", "image/jpeg", "image/jpg"):
        raise HTTPException(
            status_code=400,
            detail="Only PNG/JPEG images are supported"
        )

    # Read and load image
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load image: {str(e)}"
        )

    # Analyze with VLM
    try:
        vlm = get_vlm_service()
        result = vlm.analyze(image)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/api/v1/generate_plan", response_model=PlanGenerationResponse)
async def generate_plan(
    user_intent: str,
    screen_analysis: Dict[str, Any]
):
    """
    Generate action plan from user intent and screen state.

    Uses GPT-4 as orchestrator to create multi-step action sequence.

    Args:
        user_intent: Natural language task description
        screen_analysis: Output from analyze_screen

    Returns:
        PlanGenerationResponse with action steps
    """
    # TODO: Implement GPT-4 orchestration
    # 1. Format prompt with user intent + screen state
    # 2. Call GPT-4 API
    # 3. Parse response into structured plan
    # 4. Validate plan with Rule Engine
    # 5. Return approved plan

    raise HTTPException(
        status_code=501,
        detail="Plan generation not yet implemented (Phase 2)"
    )


@app.post("/api/v1/execute_action", response_model=ActionExecutionResponse)
async def execute_action(request: ActionExecutionRequest):
    """
    Execute a single action.

    Args:
        request: Action specification

    Returns:
        ActionExecutionResponse with execution result
    """
    # TODO: Implement action executor
    # 1. Validate action with Rule Engine
    # 2. Execute using PyAutoGUI/Playwright
    # 3. Capture screenshot after execution
    # 4. Return result

    raise HTTPException(
        status_code=501,
        detail="Action execution not yet implemented (Phase 3)"
    )


@app.post("/api/v1/approve_plan")
async def approve_plan(plan_id: str, approved: bool, feedback: Optional[str] = None):
    """
    Approve or reject a generated plan.

    Args:
        plan_id: ID of the plan to approve
        approved: Whether user approved the plan
        feedback: Optional feedback for plan revision

    Returns:
        Updated plan or acknowledgment
    """
    # TODO: Implement plan approval workflow
    # 1. Load plan from database
    # 2. If approved: mark as ready for execution
    # 3. If rejected with feedback: regenerate plan with feedback
    # 4. Return updated plan or status

    raise HTTPException(
        status_code=501,
        detail="Plan approval not yet implemented (Phase 2)"
    )


# --- Utility Endpoints ---

@app.get("/api/v1/models/status")
async def model_status():
    """Check VLM model loading status."""
    # TODO: Return actual model status
    return {
        "vlm_loaded": False,
        "model_name": "Qwen2.5-VL-32B-Instruct",
        "quantization": "4bit",
        "device": "cuda:0",
        "memory_used_gb": 0.0
    }


# --- Main Entry Point ---

def main():
    """Start the API server."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )


if __name__ == "__main__":
    main()
