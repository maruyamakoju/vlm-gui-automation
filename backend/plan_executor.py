#!/usr/bin/env python3
"""
Plan Executor - Core execution logic for automation plans
Handles conditional branching, loops, retry logic, and action execution
"""

import logging
import time
from typing import Dict, Any, List, Optional

# Import Phase 4 components
from retry_logic import RetryPolicy, execute_with_retry
from conditional_executor import ConditionalExecutor
from loop_executor import LoopExecutor
from action_executor import ActionExecutor

logger = logging.getLogger(__name__)


def execute_plan_sync(
    plan_data: Dict[str, Any],
    executor: Optional[ActionExecutor] = None,
    conditional_executor: Optional[ConditionalExecutor] = None,
    loop_executor: Optional[LoopExecutor] = None
) -> Dict[str, Any]:
    """
    Execute multi-step action plan with retry support (Phase 4).

    This is the core execution logic extracted from main.py.
    Can be called directly (no HTTP overhead) for internal use.

    For each step:
    1. Check rules (safety)
    2. Execute action (with retry if configured)
    3. Log result

    Args:
        plan_data: Dictionary containing:
            - steps: List[ActionStep] - action steps to execute
            - app_name: str (optional) - application context
            - screen_pattern: str (optional) - screen pattern for rules
        executor: ActionExecutor instance (optional, creates new if None)
        conditional_executor: ConditionalExecutor instance (optional)
        loop_executor: LoopExecutor instance (optional)

    Returns:
        Execution results dictionary:
        {
            "success": bool,
            "executed_steps": int,
            "successful_steps": int,
            "failed_at_step": int or None,
            "results": List[Dict]
        }
    """
    # Initialize executors if not provided
    if executor is None:
        executor = ActionExecutor()
    if conditional_executor is None:
        conditional_executor = ConditionalExecutor()
    if loop_executor is None:
        loop_executor = LoopExecutor(conditional_executor=conditional_executor)

    # Extract steps from plan_data
    steps = plan_data.get("steps", [])
    app_name = plan_data.get("app_name", "default")
    screen_pattern = plan_data.get("screen_pattern")

    results = []
    failed_step = None

    for i, step_data in enumerate(steps, 1):
        # Handle both dict and Pydantic model
        if hasattr(step_data, 'dict'):
            step = step_data.dict()
        else:
            step = step_data

        step_result = {
            "step": step.get("step", i),
            "action": step.get("action"),
            "target": step.get("target"),
            "success": False,
            "message": "",
            "attempts": 1,
            "retry_history": []
        }

        try:
            # Extract retry policy from parameters
            parameters = step.get("parameters", {}) or {}
            retry_cfg = parameters.get("retry")

            # Handle special action types (Phase 4)
            if step["action"] == "conditional":
                # Conditional branching
                # Note: For conditional, we need screen_elements - pass empty for now
                # TODO: Capture actual screen elements before execution
                screen_elements = []
                result = conditional_executor.execute_conditional(
                    step,
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

            elif step["action"] == "loop":
                # Loop execution
                # Note: For loop, we need screen_elements - pass empty for now
                # TODO: Capture actual screen elements before execution
                screen_elements = []
                result = loop_executor.execute_loop(
                    step,
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
                if step["action"] == "click":
                    element = {
                        "type": "button",
                        "text": step["target"],
                        "bbox": [100, 100, 200, 150]  # Dummy bbox
                    }
                    return executor.click_element(element)

                elif step["action"] == "type":
                    text = parameters.get("value", "")
                    return executor.type_text(text)

                elif step["action"] == "wait":
                    duration = parameters.get("duration", 1)
                    time.sleep(duration)
                    return True

                else:
                    logger.warning(f"Unknown action type: {step['action']}")
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
                    f"{step['action']} on {step['target']}",
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
                step_result["message"] = f"{step['action']} {'succeeded' if success else 'failed'}"

                if not success:
                    failed_step = i

        except Exception as e:
            logger.exception(f"Step {i} execution failed with exception")
            step_result["message"] = f"ERROR: {str(e)}"
            failed_step = i

        results.append(step_result)

        # Stop on failure if abort policy
        retry_cfg = step.get("parameters", {}).get("retry") if step.get("parameters") else None
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
