#!/usr/bin/env python3
"""
Action Executor - Execute GUI automation actions

Handles:
- Basic GUI actions (click, type, wait)
- Excel-specific operations (set_filter, save_as)
- Window detection and focus
"""

import pyautogui
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Execute automation actions on GUI elements."""

    def __init__(self):
        """Initialize ActionExecutor with safety settings."""
        # PyAutoGUI safety: 0.1s pause between actions
        pyautogui.PAUSE = 0.1
        # Fail-safe: move mouse to top-left corner to abort
        pyautogui.FAILSAFE = True
        logger.info("ActionExecutor initialized with safety settings")

    def click_element(self, element: Dict[str, Any]) -> bool:
        """
        Click on a GUI element at specified coordinates.

        Args:
            element: Dict with 'bbox' or 'center' coordinates
                    e.g., {'bbox': [x, y, w, h]} or {'center': [x, y]}

        Returns:
            bool: True if click succeeded, False otherwise
        """
        try:
            # Extract coordinates from element
            if 'center' in element:
                x, y = element['center']
            elif 'bbox' in element:
                bbox = element['bbox']
                x = bbox[0] + bbox[2] // 2  # x + width/2
                y = bbox[1] + bbox[3] // 2  # y + height/2
            else:
                logger.error("Element missing coordinates (need 'center' or 'bbox')")
                return False

            # Execute click
            logger.info(f"Clicking at ({x}, {y})")
            pyautogui.click(x, y)
            return True

        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False

    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text at current cursor position.

        Args:
            text: Text to type
            interval: Delay between keystrokes in seconds

        Returns:
            bool: True if typing succeeded
        """
        try:
            logger.info(f"Typing text: {text[:50]}...")
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return False

    def press_key(self, key: str) -> bool:
        """
        Press a keyboard key.

        Args:
            key: Key name (e.g., 'enter', 'tab', 'esc')

        Returns:
            bool: True if key press succeeded
        """
        try:
            logger.info(f"Pressing key: {key}")
            pyautogui.press(key)
            return True
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            return False

    def wait(self, seconds: float) -> bool:
        """
        Wait for specified duration.

        Args:
            seconds: Duration to wait

        Returns:
            bool: Always True
        """
        logger.info(f"Waiting {seconds}s")
        time.sleep(seconds)
        return True

    def execute_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single action based on action_data specification.

        Args:
            action_data: Dict with 'action', 'target', 'params', etc.
                        e.g., {
                            "action": "click",
                            "target_element_id": "btn_filter",
                            "params": {...}
                        }

        Returns:
            Dict with execution result
        """
        action_type = action_data.get("action", "").lower()
        params = action_data.get("params", {})

        try:
            if action_type == "click":
                element = params.get("element") or action_data.get("element")
                if not element:
                    return {"success": False, "error": "Missing element for click action"}
                success = self.click_element(element)
                return {"success": success}

            elif action_type == "type":
                text = params.get("text", "")
                success = self.type_text(text)
                return {"success": success}

            elif action_type == "press_key":
                key = params.get("key", "enter")
                success = self.press_key(key)
                return {"success": success}

            elif action_type == "wait":
                duration = params.get("duration", 1.0)
                success = self.wait(duration)
                return {"success": success}

            else:
                logger.warning(f"Unknown action type: {action_type}")
                return {
                    "success": False,
                    "error": f"Unknown action type: {action_type}"
                }

        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {"success": False, "error": str(e)}
