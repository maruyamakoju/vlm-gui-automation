# Developer Quick Start Guide

**Project:** VLM GUI Automation System
**Last Updated:** 2025-12-12

## Prerequisites

- Python 3.8+
- Miniconda3 with `vlm-gui` environment
- Windows OS (scripts tested on Windows)
- Git

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/<yourname>/vlm-gui-automation.git
cd vlm-gui-automation
```

### 2. Environment Setup

```bash
# Create conda environment
conda create -n vlm-gui python=3.10 -y
conda activate vlm-gui

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in `backend/` directory:

```bash
# Development mode (uses dummy VLM)
USE_DUMMY_VLM=true

# Optional: GPT features (if using OpenAI)
OPENAI_API_KEY=your_api_key_here
```

## Quick Start (Windows)

### Start Server

```bash
cd backend
run_server.bat
```

Server will start on `http://127.0.0.1:8002`

### Run Tests

```bash
cd backend

# Product quality tests (8 tests)
python test_product_quality.py

# Error handler tests (4 tests)
python test_error_handler.py
```

Expected: **12/12 PASS**

### Open Demo

```bash
cd backend
open_demo.bat
```

Or navigate to: `http://127.0.0.1:8002/static/phase4_demo.html`

## Project Structure

```
vlm-gui-automation/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── vlm_adapter.py          # VLM abstraction layer
│   ├── error_handler.py        # Unified error handling
│   ├── conditional_executor.py # Conditional logic
│   ├── loop_executor.py        # Loop execution
│   ├── library.py              # Action library
│   ├── test_product_quality.py # 8 product tests
│   ├── test_error_handler.py   # 4 error tests
│   ├── run_server.bat          # Server startup script
│   ├── run_quality_tests.bat   # Test runner
│   └── open_demo.bat           # Demo launcher
├── frontend/
│   └── static/
│       └── phase4_demo.html    # Demo interface
└── docs/                       # Documentation
```

## API Endpoints

### Health Check
```bash
GET http://127.0.0.1:8002/health
```

### Business Scenarios
```bash
GET http://127.0.0.1:8002/api/v1/business_scenarios
```

### Execute Plan
```bash
POST http://127.0.0.1:8002/api/v1/execute_plan
Content-Type: application/json

{
  "plan": [
    {"type": "click", "params": {"selector": "#button"}}
  ]
}
```

### VLM Screen Analysis
```bash
POST http://127.0.0.1:8002/api/v1/analyze_screen
Content-Type: multipart/form-data

file: <image.png>
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit code, add tests, update documentation.

### 3. Run Tests

```bash
python test_product_quality.py
python test_error_handler.py
```

All tests must pass before committing.

### 4. Commit Changes

```bash
git add .
git commit -m "feat: description of your changes"
```

### 5. Push and Create PR

```bash
git push -u origin feature/your-feature-name
```

Then create Pull Request on GitHub.

## Common Tasks

### Add New Action to Library

1. Edit `backend/library.py`
2. Add action to `LIBRARY` dict
3. Update `test_product_quality.py` if needed
4. Run tests

### Add New API Endpoint

1. Edit `backend/main.py`
2. Use error handlers from `error_handler.py`:
   ```python
   from error_handler import ValidationError, InternalError

   @app.post("/api/v1/your_endpoint")
   async def your_endpoint():
       if invalid_input:
           raise ValidationError("Your error message")
       return {"success": True, "data": result}
   ```
3. Add test to `test_product_quality.py`
4. Run tests

### Switch to Real VLM

1. Edit `backend/.env`:
   ```bash
   USE_DUMMY_VLM=false
   ```
2. Ensure Qwen2-VL model is downloaded
3. Requires GPU with sufficient VRAM

## Troubleshooting

### Port Already in Use

```bash
# Windows: Kill process on port 8002
netstat -ano | findstr :8002
taskkill /PID <pid> /F
```

### Tests Failing

1. Ensure server is running on port 8002
2. Check `USE_DUMMY_VLM=true` in environment
3. Verify all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8002
```

## Phase Status

- **Phase 1-2:** Basic infrastructure (COMPLETE)
- **Phase 3:** Library system (COMPLETE)
- **Phase 4:** Conditional & loop execution (COMPLETE)
- **Phase 5-A:** VLM adapter + unified error handling (COMPLETE)
- **Phase 5-B:** Error handler for all endpoints (IN PROGRESS)
- **Phase 6:** Real VLM integration (PLANNED)

## Documentation

- `PHASE5A_VLM_ADAPTER_SUMMARY.md` - Phase 5-A deliverables
- `backend/ERROR_HANDLER_STATUS.md` - Error handler details
- `PHASE4_COMPLETE.md` - Phase 4 completion summary

## Support

For issues or questions:
1. Check existing documentation in `docs/`
2. Review test files for usage examples
3. Check git commit history for context

## Contributing

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass (12/12)
5. Create descriptive commit messages

---

**Quick Command Reference:**

```bash
# Start development
conda activate vlm-gui
cd backend
run_server.bat

# Run tests
python test_product_quality.py  # 8/8
python test_error_handler.py    # 4/4

# View demo
open_demo.bat
# Or: http://127.0.0.1:8002/static/phase4_demo.html
```
