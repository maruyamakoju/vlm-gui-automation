#!/usr/bin/env python3
"""
Script to integrate unified error handler into main.py
"""

import re

# Read main.py
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add import after loop executors
import_pattern = r"(# Import conditional and loop executors \(Phase 4\)\nfrom conditional_executor import ConditionalExecutor\nfrom loop_executor import LoopExecutor)\n\n(# GPT Orchestrator is optional)"
import_replacement = r"\1\n\n# Import unified error handler (Phase 5)\nfrom error_handler import register_error_handlers, ValidationError, VLMError, NotImplementedError as APINotImplementedError\n\n\2"

content = re.sub(import_pattern, import_replacement, content)

# 2. Register error handlers after CORS middleware
cors_pattern = r"(app\.add_middleware\(\s+CORSMiddleware,\s+allow_origins=\[\"\*\"\],.*?\n\))\n\n(# Initialize Action Executor)"
cors_replacement = r"\1\n\n# Register unified error handlers (Phase 5)\nregister_error_handlers(app)\nlogger.info(\"Unified error handlers registered\")\n\n\2"

content = re.sub(cors_pattern, cors_replacement, content, flags=re.DOTALL)

# 3. Update analyze_screen endpoint to use new exceptions
analyze_pattern = r"(@app\.post\(\"/api/v1/analyze_screen\"\)\nasync def analyze_screen\(file: UploadFile = File\(\.\.\.\)\):.*?)(# Validate file type\s+if file\.content_type not in \(\"image/png\", \"image/jpeg\", \"image/jpg\"\):\s+raise HTTPException\(\s+status_code=400,\s+detail=\"Only PNG/JPEG images are supported\"\s+\))"
analyze_replacement = r'\1# Validate file type\n    if file.content_type not in ("image/png", "image/jpeg", "image/jpg"):\n        raise ValidationError("Only PNG/JPEG images are supported")'

content = re.sub(analyze_pattern, analyze_replacement, content, flags=re.DOTALL)

# 4. Update analyze_screen image loading error
analyze_load_pattern = r"(try:\s+contents = await file\.read\(\)\s+image = Image\.open\(io\.BytesIO\(contents\)\)\.convert\(\"RGB\"\)\s+)except Exception as e:\s+raise HTTPException\(\s+status_code=400,\s+detail=f\"Failed to load image: \{str\(e\)\}\"\s+\)"
analyze_load_replacement = r'\1except Exception as e:\n        raise ValidationError(f"Failed to load image: {str(e)}")'

content = re.sub(analyze_load_pattern, analyze_load_replacement, content, flags=re.DOTALL)

# 5. Update analyze_screen VLM error
analyze_vlm_pattern = r"(try:\s+vlm_client = get_global_vlm_client\(\).*?return result\s+)except Exception as e:\s+raise HTTPException\(\s+status_code=500,\s+detail=f\"Analysis failed: \{str\(e\)\}\"\s+\)"
analyze_vlm_replacement = r'\1except Exception as e:\n        raise VLMError(f"Analysis failed: {str(e)}")'

content = re.sub(analyze_vlm_pattern, analyze_vlm_replacement, content, flags=re.DOTALL)

# Write modified content
with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[OK] Error handler integration complete")
print("  - Added error_handler imports")
print("  - Registered error handlers with app")
print("  - Updated analyze_screen endpoint to use custom exceptions")
