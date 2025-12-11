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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import VLM service
from vlm_service import init_vlm_service, get_vlm_service

# Import Action Executor
from action_executor import ActionExecutor

# Import Orchestrators and Rule Engine
from orchestrator_simple import SimpleOrchestrator
from rule_engine import RuleEngine
# Import retry logic (Phase 4)
from retry_logic import RetryPolicy, execute_with_retry

# Import conditional and loop executors (Phase 4)
from conditional_executor import ConditionalExecutor
from loop_executor import LoopExecutor

# GPT Orchestrator is optional (requires OPENAI_API_KEY)
try:
    from orchestrator_gpt import GPTOrchestrator
    gpt_available = True
except ImportError:
    gpt_available = False

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

# Initialize Action Executor, Orchestrators, and Rule Engine
executor = ActionExecutor()
orchestrator = SimpleOrchestrator()
rule_engine = RuleEngine()

# Initialize conditional and loop executors (Phase 4)
conditional_executor = ConditionalExecutor()
loop_executor = LoopExecutor(conditional_executor=conditional_executor)

# Initialize GPT Orchestrator if API key available
gpt_orchestrator = None
if gpt_available and os.getenv("OPENAI_API_KEY"):
    try:
        gpt_orchestrator = GPTOrchestrator()
        logger.info("GPT Orchestrator initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize GPT Orchestrator: {e}")
else:
    logger.info("GPT Orchestrator not available (missing OPENAI_API_KEY or import failed)")


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


class ClickElementRequest(BaseModel):
    """Request to click a specific element."""
    element_index: int
    elements: List[Dict[str, Any]]


class AutoClickRequest(BaseModel):
    """Request to automatically select and click element by instruction."""
    user_instruction: str
    elements: List[Dict[str, Any]]


class CheckRuleRequest(BaseModel):
    """Request to check if action is allowed by rules."""
    element: Dict[str, Any]
    app_name: str
    screen_pattern: Optional[str] = None


class GeneratePlanGPTRequest(BaseModel):
    """Request for GPT-based plan generation."""
    user_instruction: str
    screen_description: str
    elements: List[Dict[str, Any]]
    rules: Optional[List[Dict[str, Any]]] = None


class ExecutePlanRequest(BaseModel):
    """Request to execute a multi-step plan."""
    steps: List[ActionStep]
    app_name: str = "default"
    screen_pattern: Optional[str] = None


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


@app.post("/api/v1/click_element")
async def click_element(request: ClickElementRequest):
    """
    Click a specific UI element by index.

    Args:
        request: ClickElementRequest with element_index and elements list

    Returns:
        Success status and message
    """
    idx = request.element_index
    elements = request.elements

    # Validate index
    if idx < 0 or idx >= len(elements):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid element_index: {idx}. Must be between 0 and {len(elements)-1}"
        )

    # Get element and execute click
    element = elements[idx]
    try:
        success = executor.click_element(element)
        if success:
            return {
                "success": True,
                "message": f"Clicked element {idx}: {element.get('type', 'unknown')} '{element.get('text', '')}'",
                "element": element
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Click execution failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Click failed: {str(e)}"
        )


@app.post("/api/v1/auto_click_simple")
async def auto_click_simple(request: AutoClickRequest):
    """
    Automatically select and click element based on natural language instruction.

    Uses simple rule-based matching (Phase 2 v0).
    Will be replaced with GPT-4 orchestrator in Phase 3.

    Args:
        request: AutoClickRequest with user_instruction and elements list

    Returns:
        Success status, selected element, and explanation
    """
    user_instruction = request.user_instruction
    elements = request.elements

    # Get available elements summary
    elements_summary = orchestrator.get_available_elements_summary(elements)

    # Select element using simple orchestrator
    selected_idx = orchestrator.select_element_index(user_instruction, elements)

    if selected_idx is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No matching element found",
                "instruction": user_instruction,
                "available_elements": elements_summary
            }
        )

    # Get selected element
    element = elements[selected_idx]

    # Generate explanation
    explanation = orchestrator.explain_match(user_instruction, element)

    # Execute click
    try:
        success = executor.click_element(element)
        if success:
            return {
                "success": True,
                "message": "Element automatically selected and clicked",
                "instruction": user_instruction,
                "selected_index": selected_idx,
                "selected_element": element,
                "explanation": explanation,
                "available_elements_count": len(elements)
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Click execution failed after element selection"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Auto-click failed: {str(e)}"
        )


# --- Rule Engine Endpoints ---

@app.post("/api/v1/check_rule")
async def check_rule(request: CheckRuleRequest):
    """
    Check if action on element is allowed by rules.

    Args:
        request: CheckRuleRequest with element, app_name, and optional screen_pattern

    Returns:
        Rule check result with allowed status and reason
    """
    try:
        result = rule_engine.check_action_allowed(
            request.element,
            request.app_name,
            request.screen_pattern
        )

        return {
            "success": True,
            "allowed": result.get("allowed", True),
            "reason": result.get("reason"),
            "severity": result.get("severity"),
            "rule_id": result.get("rule_id"),
            "element": request.element
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Rule check failed: {str(e)}"
        )


@app.get("/api/v1/rules/all")
async def get_all_rules():
    """Get all configured rules."""
    try:
        return rule_engine.get_all_rules()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve rules: {str(e)}"
        )


# --- GPT Orchestrator Endpoints ---

@app.post("/api/v1/generate_plan_gpt")
async def generate_plan_gpt(request: GeneratePlanGPTRequest):
    """
    Generate multi-step action plan using GPT-4.

    Requires OPENAI_API_KEY environment variable.

    Args:
        request: GeneratePlanGPTRequest with instruction, screen description, elements

    Returns:
        Generated plan with steps
    """
    if gpt_orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="GPT Orchestrator not available (OPENAI_API_KEY not set or import failed)"
        )

    try:
        plan = gpt_orchestrator.generate_plan(
            user_instruction=request.user_instruction,
            screen_description=request.screen_description,
            elements=request.elements,
            rules=request.rules
        )

        return {
            "success": True,
            "plan": plan,
            "orchestrator": "gpt-4"
        }

    except Exception as e:
        logger.exception("GPT plan generation failed")
        raise HTTPException(
            status_code=500,
            detail=f"GPT plan generation failed: {str(e)}"
        )


@app.post("/api/v1/execute_plan")
async def execute_plan(request: ExecutePlanRequest):
    """
    Execute multi-step action plan with retry support (Phase 4).

    For each step:
    1. Check rules (safety)
    2. Execute action (with retry if configured)
    3. Log result

    Args:
        request: ExecutePlanRequest with steps and app context

    Returns:
        Execution results for all steps
    """
    results = []
    failed_step = None

    for i, step in enumerate(request.steps, 1):
        step_result = {
            "step": step.step,
            "action": step.action,
            "target": step.target,
            "success": False,
            "message": "",
            "attempts": 1,
            "retry_history": []
        }

        try:
            # Extract retry policy from parameters
            retry_cfg = step.parameters.get("retry") if step.parameters else None

            # Handle special action types (Phase 4)
            if step.action == "conditional":
                # Conditional branching
                # Note: For conditional, we need screen_elements - pass empty for now
                # TODO: Capture actual screen elements before execution
                screen_elements = []
                result = conditional_executor.execute_conditional(
                    step.dict(),
                    executor,
                    screen_elements
                )

                step_result["success"] = result.get("success", False)
                step_result["message"] = result.get("message", "")
                step_result["condition_met"] = result.get("condition_met")
                step_result["executed_branch"] = result.get("executed_branch")
                step_result["branch_results"] = result.get("branch_results", [])

                # Skip regular execution path for conditional
                results.append(step_result)

                if not step_result["success"]:
                    failed_step = i
                    break

                continue

            elif step.action == "loop":
                # Loop execution
                # Note: For loop, we need screen_elements - pass empty for now
                # TODO: Capture actual screen elements before execution
                screen_elements = []
                result = loop_executor.execute_loop(
                    step.dict(),
                    executor,
                    screen_elements
                )

                step_result["success"] = result.get("success", False)
                step_result["message"] = result.get("message", "")
                step_result["loop_type"] = result.get("loop_type")
                step_result["iterations"] = result.get("iterations", 0)
                step_result["iteration_results"] = result.get("iteration_results", [])

                # Skip regular execution path for loop
                results.append(step_result)

                if not step_result["success"]:
                    failed_step = i
                    break

                continue

            # Define action execution function
            def execute_action():
                # Simple implementation: create dummy element and execute
                if step.action == "click":
                    element = {
                        "type": "button",
                        "text": step.target,
                        "bbox": [100, 100, 200, 150]  # Dummy bbox
                    }
                    return executor.click_element(element)

                elif step.action == "type":
                    text = step.parameters.get("value", "") if step.parameters else ""
                    return executor.type_text(text)

                elif step.action == "wait":
                    import time
                    duration = step.parameters.get("duration", 1) if step.parameters else 1
                    time.sleep(duration)
                    return True

                else:
                    logger.warning(f"Unknown action type: {step.action}")
                    return False

            # Execute with or without retry
            if retry_cfg:
                # Retry enabled
                policy = RetryPolicy(
                    max_retries=retry_cfg.get("max_retries", 0),
                    retry_delay=retry_cfg.get("retry_delay", 1.0),
                    on_failure=retry_cfg.get("on_failure", "abort")
                )

                retry_result = execute_with_retry(
                    execute_action,
                    f"{step.action} on {step.target}",
                    policy
                )

                step_result["success"] = retry_result["success"]
                step_result["message"] = retry_result["message"]
                step_result["attempts"] = retry_result["attempts"]
                step_result["retry_history"] = retry_result.get("retry_history", [])
                step_result["final_action"] = retry_result.get("final_action", "")

                # Handle on_failure policy
                if not retry_result["success"]:
                    if retry_result["final_action"] == "abort":
                        failed_step = i
                    elif retry_result["final_action"] == "skip":
                        # Continue to next step
                        pass
                    # ask_user would pause here (not implemented yet)
            else:
                # No retry - execute once
                success = execute_action()
                step_result["success"] = success
                step_result["message"] = f"{step.action} {'succeeded' if success else 'failed'}"

                if not success:
                    failed_step = i

        except Exception as e:
            logger.exception(f"Step {i} execution failed with exception")
            step_result["message"] = f"ERROR: {str(e)}"
            failed_step = i

        results.append(step_result)

        # Stop on failure if abort policy
        if failed_step and (not retry_cfg or retry_cfg.get("on_failure") == "abort"):
            break

    # Summary
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)

    return {
        "success": failed_step is None,
        "executed_steps": total_count,
        "successful_steps": success_count,
        "failed_at_step": failed_step,
        "results": results
    }

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



# --- Business Scenario Endpoints (Phase 4) ---

@app.get("/api/v1/business_scenarios")
async def get_business_scenarios():
    """Get list of available business scenarios."""
    try:
        from business_scenarios import get_available_scenarios
        scenarios = get_available_scenarios()
        return {
            "success": True,
            "scenarios": scenarios,
            "count": len(scenarios)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "scenarios": []
        }


@app.post("/api/v1/run_scenario")
async def run_business_scenario(request: dict):
    """Execute a business scenario and return results."""
    try:
        from business_scenarios import run_scenario

        scenario_name = request.get("scenario_name")
        if not scenario_name:
            return {
                "success": False,
                "error": "scenario_name is required"
            }

        # Run scenario
        result = run_scenario(scenario_name)
        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to run scenario: {str(e)}"
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
