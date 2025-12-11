"""
Simple Rule-Based Orchestrator - Button Test Version

This is a minimal orchestrator for testing purposes.
Matches user instructions to UI elements using simple text matching.

Phase 2 v0: Rule-based matching only (no LLM)
Phase 3: Will be replaced with GPT-4 orchestrator
"""

from typing import Dict, Any, List, Optional
import re


class SimpleOrchestrator:
    """Simple rule-based orchestrator for button_test.html."""

    @staticmethod
    def select_element_index(
        user_instruction: str,
        elements: List[Dict[str, Any]]
    ) -> Optional[int]:
        """
        Select element index based on user instruction.

        Args:
            user_instruction: Natural language instruction (Japanese/English)
            elements: List of detected UI elements

        Returns:
            Element index if found, None otherwise
        """
        # Normalize instruction
        instruction_lower = user_instruction.lower()
        instruction_normalized = user_instruction.replace(" ", "").replace("　", "")

        # Try exact text matching first
        for idx, element in enumerate(elements):
            element_text = element.get("text", "").replace(" ", "").replace("　", "")

            # Exact match
            if element_text in instruction_normalized:
                return idx

            # Partial match with confidence
            if element_text and element_text in instruction_lower:
                return idx

        # Try pattern matching for common button patterns
        patterns = [
            (r"ボタン\s*[AaＡａ]", ["ボタンA", "ボタンa", "button a"]),
            (r"ボタン\s*[BbＢｂ]", ["ボタンB", "ボタンb", "button b"]),
            (r"ボタン\s*[CcＣｃ]", ["ボタンC", "ボタンc", "button c"]),
            (r"button\s*[Aa]", ["ボタンA", "ボタンa", "button a"]),
            (r"button\s*[Bb]", ["ボタンB", "ボタンb", "button b"]),
            (r"button\s*[Cc]", ["ボタンC", "ボタンc", "button c"]),
        ]

        for pattern, target_texts in patterns:
            if re.search(pattern, user_instruction, re.IGNORECASE):
                # Find element with matching text
                for idx, element in enumerate(elements):
                    element_text = element.get("text", "")
                    for target in target_texts:
                        if target.lower() in element_text.lower():
                            return idx

        # Try matching by element type + position words
        position_keywords = {
            "first": 0,
            "最初": 0,
            "一番上": 0,
            "1つ目": 0,
            "last": -1,
            "最後": -1,
            "一番下": -1,
        }

        for keyword, pos_index in position_keywords.items():
            if keyword in instruction_lower or keyword in instruction_normalized:
                # Get all buttons
                buttons = [
                    (idx, el) for idx, el in enumerate(elements)
                    if el.get("type") == "button"
                ]
                if buttons:
                    if pos_index == -1:
                        return buttons[-1][0]
                    elif pos_index < len(buttons):
                        return buttons[pos_index][0]

        # No match found
        return None

    @staticmethod
    def explain_match(
        user_instruction: str,
        element: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for why element was selected.

        Args:
            user_instruction: User's instruction
            element: Selected element

        Returns:
            Explanation string
        """
        element_text = element.get("text", "")
        element_type = element.get("type", "unknown")

        return (
            f"指示「{user_instruction}」に対して、"
            f"{element_type} '{element_text}' が選択されました。"
        )

    @staticmethod
    def get_available_elements_summary(elements: List[Dict[str, Any]]) -> str:
        """
        Generate human-readable summary of available elements.

        Args:
            elements: List of UI elements

        Returns:
            Summary string
        """
        if not elements:
            return "要素が検出されませんでした。"

        summary_lines = [f"検出された要素 ({len(elements)}個):"]
        for idx, el in enumerate(elements):
            el_type = el.get("type", "unknown")
            el_text = el.get("text", "")
            summary_lines.append(f"  [{idx}] {el_type}: '{el_text}'")

        return "\n".join(summary_lines)

    @staticmethod
    def revise_plan(
        old_plan: List[Dict[str, Any]],
        user_feedback: str,
        screen_description: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Revise plan based on user feedback (rule-based version).

        Phase 3: Simple rule-based plan revision for common patterns.

        Supported patterns:
        - "先に〜して" / "最初に〜" → Add step at beginning
        - "〜列でフィルタ" / "〜でフィルタ" → Modify filter column
        - "〜を削除" → Remove specific step
        - "〜を追加" → Add new step

        Args:
            old_plan: List of plan steps (dicts)
            user_feedback: User's correction feedback
            screen_description: Optional screen context

        Returns:
            Revised plan (list of dicts)
        """
        # Copy the plan to avoid mutation
        revised = [step.copy() for step in old_plan]

        feedback_lower = user_feedback.lower()
        feedback_normalized = user_feedback.replace(" ", "").replace("　", "")

        # Pattern 1: "先にログインして" / "最初に〜"
        if ("先に" in feedback_normalized or "最初に" in feedback_normalized) and "ログイン" in feedback_normalized:
            login_step = {
                "id": 0,
                "action": "login",
                "target_element_id": "login_form",
                "description": "ログインフォームでログインする",
                "safety_tag": "safe",
                "params": {}
            }
            revised.insert(0, login_step)
            # Re-number IDs
            for i, step in enumerate(revised, start=1):
                step["id"] = i

        # Pattern 2: "税込金額列でフィルタ" / "〜でフィルタ"
        elif ("列" in feedback_normalized or "カラム" in feedback_normalized) and ("フィルタ" in feedback_normalized or "絞" in feedback_normalized):
            # Extract column name (simple heuristic)
            # Find text before "列" or "でフィルタ"
            import re
            column_match = re.search(r'([ぁ-んァ-ヶー一-龯0-9a-zA-Z]+)(?:列|カラム|で|を)(?:フィルタ|絞)', feedback_normalized)
            if column_match:
                column_name = column_match.group(1)
                # Find filter/set_filter action and update params
                for step in revised:
                    if step.get("action") in ("set_filter", "filter", "click"):
                        if "column" in step.get("params", {}):
                            step["params"]["column"] = column_name
                            step["description"] = f"{column_name}列でフィルタする"
                        elif "target" in step.get("params", {}):
                            step["params"]["target"] = column_name
                            step["description"] = f"{column_name}でフィルタする"

        # Pattern 3: "〜を削除" / "〜は要らない"
        elif "削除" in feedback_normalized or "要らない" in feedback_normalized or "消して" in feedback_normalized:
            # Try to identify which step to remove based on description
            steps_to_remove = []
            for i, step in enumerate(revised):
                step_desc = step.get("description", "").replace(" ", "").replace("　", "")
                # Simple match: if any word from feedback appears in description
                feedback_keywords = [w for w in feedback_normalized if len(w) > 1]
                if any(kw in step_desc for kw in feedback_keywords if kw not in ["削除", "要らない", "消して"]):
                    steps_to_remove.append(i)

            # Remove identified steps (in reverse to maintain indices)
            for i in reversed(steps_to_remove):
                revised.pop(i)

            # Re-number IDs
            for i, step in enumerate(revised, start=1):
                step["id"] = i

        # Pattern 4: "〜を追加" / "〜もして"
        elif "追加" in feedback_normalized or "もして" in feedback_normalized:
            # For now, just add a generic step at the end
            # In real implementation, would parse what action to add
            new_step = {
                "id": len(revised) + 1,
                "action": "custom",
                "target_element_id": None,
                "description": f"追加: {user_feedback}",
                "safety_tag": "safe",
                "params": {"original_feedback": user_feedback}
            }
            revised.append(new_step)

        # If no pattern matched, return original plan unchanged
        # (This is acceptable for MVP - not all feedback types are supported)

        return revised
