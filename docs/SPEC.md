# VLM GUI Automation Agent - Technical Specification

**Version**: 0.1.0
**Date**: 2025-12-11
**Status**: Phase 0 - Environment Setup

---

## 1. Project Overview

### Concept
自然言語で指示 → 画面認識 → アクション計画生成 → 人間承認 → 実行

Non-engineer users give natural language commands, the VLM understands screens, generates action plans, and executes with human approval.

### Target Users
- Japanese SME back-office staff (non-engineers)
- Initial focus: Chrome + Excel automation

### Business Model
- Custom VLM fine-tuning service for Japanese enterprises
- Revenue: ¥300万-2000万 per project
- Value proposition: Data sovereignty, Japanese language optimization, cost reduction vs GPT-4V

---

## 2. Requirements

### 2.1 Functional Requirements

**FR1: Natural Language Input**
- User inputs task description in Japanese natural language
- Example: "メールを送信して、添付ファイルをExcelで開いて、A列の合計をB1に入れて"

**FR2: Screen Understanding**
- Capture screenshots automatically
- VLM analyzes screen content
- Identify UI elements (buttons, input fields, menus) with bounding boxes

**FR3: Plan Generation**
- Generate multi-step action plan from user intent + screen state
- Use GPT-4 as orchestrator for complex reasoning
- Output: Structured action sequence (JSON)

**FR4: Human Approval**
- Display plan to user before execution
- User can approve, reject, or modify ("こうして" feedback loop)
- Revise plan based on feedback

**FR5: Action Execution**
- Execute approved actions sequentially
- Support: mouse click, keyboard input, window switching, Excel operations
- Real-time feedback to GUI

**FR6: Error Handling**
- Detect execution failures (element not found, timeout)
- Prompt user for guidance
- Support retry or plan revision

### 2.2 Non-Functional Requirements

**NFR1: Response Time**
- Screen analysis: < 5 seconds
- Plan generation: < 10 seconds
- Action execution: Real-time feedback (per-step confirmation)

**NFR2: Accuracy**
- Screen element detection: > 90%
- Plan correctness: > 80% (before human approval)

**NFR3: Security**
- No data sent to external servers (on-premise VLM)
- All actions logged for audit trail

**NFR4: Usability**
- Japanese UI
- Clear error messages
- Minimal technical jargon

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User (GUI - Electron)                    │
│  - Natural language input                                    │
│  - Plan approval interface                                   │
│  - Real-time execution feedback                              │
└─────────────────┬───────────────────────────────────────────┘
                  │ WebSocket / REST API
┌─────────────────▼───────────────────────────────────────────┐
│              Backend Orchestrator (FastAPI)                  │
│  - Request routing                                           │
│  - State management                                          │
│  - Logging & audit trail                                     │
└─────┬───────────┬───────────────┬───────────────────────────┘
      │           │               │
┌─────▼─────┐ ┌──▼──────────┐ ┌──▼──────────────┐
│   VLM     │ │  GPT-4      │ │  Action         │
│  Service  │ │ Orchestrator│ │  Executor       │
│  (Qwen2.5 │ │             │ │  (PyAutoGUI,    │
│   VL-32B) │ │             │ │   Playwright)   │
└───────────┘ └─────────────┘ └──────────────────┘
      │               │               │
┌─────▼───────────────▼───────────────▼──────────────────────┐
│                  Rule Engine                                 │
│  - Safety constraints (no destructive actions)               │
│  - Action validation                                         │
└──────────────────────────────────────────────────────────────┘
      │
┌─────▼────────────────────────────────────────────────────────┐
│              Database & RAG                                   │
│  - SQLite/PostgreSQL (execution history)                     │
│  - Vector store (Faiss/Qdrant for past action patterns)      │
└───────────────────────────────────────────────────────────────┘
```

### 3.1 Component Details

#### Frontend (Electron + React + TypeScript)
- Chat interface for natural language input
- Plan preview and approval UI
- Real-time execution visualization
- Logs and history viewer

#### Backend Orchestrator (FastAPI)
- `/analyze_screen`: Screenshot → VLM → UI element detection
- `/generate_plan`: User intent + screen state → action sequence
- `/execute_action`: Execute single action with validation
- `/approve_plan`: User approval workflow
- WebSocket: Real-time status updates

#### VLM Service
- Model: Qwen2.5-VL-32B-Instruct (4bit/8bit quantization)
- Inference: vLLM on RTX 5090
- Input: Screenshot (PNG) + prompt
- Output: JSON with UI elements and bounding boxes

#### GPT-4 Orchestrator
- Receives user intent + screen analysis
- Generates multi-step action plan
- Handles complex reasoning (conditionals, loops)

#### Action Executor
- PyAutoGUI: Mouse/keyboard automation
- Playwright: Browser automation
- openpyxl: Excel operations
- pywinauto: Windows GUI automation

#### Rule Engine
- Safety constraints:
  - No file deletion outside workspace
  - No system settings changes
  - No network requests to unknown domains
- Action validation before execution

#### RAG (Future enhancement)
- Store successful action patterns
- Retrieve similar past executions for plan generation

---

## 4. Use Cases

### UC1: Simple Browser Task
**User**: "Googleで'Python vLLM'を検索して、最初のリンクを開いて"

**Steps**:
1. User inputs command
2. System captures Chrome screenshot
3. VLM identifies search box
4. Plan: [click search box, type "Python vLLM", press Enter, wait, click first result]
5. User approves
6. System executes actions sequentially

### UC2: Excel Data Entry
**User**: "このExcelファイルのA列の数値を全部合計してB1に入れて"

**Steps**:
1. System captures Excel screenshot
2. VLM identifies cells A1-A10 with numbers
3. Plan: [click B1, type "=SUM(A:A)", press Enter]
4. User approves
5. System executes

### UC3: Multi-Step Workflow
**User**: "メールを送信して、その後Excelで報告書を作って"

**Steps**:
1. GPT-4 breaks down into sub-tasks
2. Task 1: [open Outlook, click New Email, fill fields, send]
3. Task 2: [open Excel, create new sheet, enter data]
4. User approves full plan
5. System executes with per-step confirmation

---

## 5. Prompt Design

### 5.1 Screen Analysis Prompt (VLM)

```
You are a GUI element detector. Analyze this screenshot and return all interactive elements.

Output format (JSON):
{
  "elements": [
    {
      "type": "button|input|link|menu",
      "text": "displayed text",
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.95
    }
  ],
  "screen_description": "brief description of what's visible"
}

Be precise with bounding boxes. Return all visible UI elements.
```

### 5.2 Plan Generation Prompt (GPT-4)

```
You are an automation planner. Given a user's task and current screen state, generate a step-by-step action plan.

User task: {user_input}
Screen state: {screen_analysis}

Output format (JSON):
{
  "plan": [
    {
      "step": 1,
      "action": "click|type|wait|press_key",
      "target": "element description or coordinates",
      "parameters": {"key": "value"},
      "rationale": "why this step"
    }
  ],
  "estimated_duration": "seconds",
  "risk_level": "low|medium|high"
}

Generate safe, efficient plans. Flag high-risk actions.
```

---

## 6. Rule Engine Design

### Safety Rules

| Rule ID | Description | Action |
|---------|-------------|--------|
| R001 | No file deletion outside workspace | Block + warn user |
| R002 | No system settings changes | Block + warn user |
| R003 | No unknown network requests | Prompt user for approval |
| R004 | No admin-privileged operations | Block + warn user |
| R005 | Confirm destructive Excel operations | Require explicit approval |

### Validation Logic

```python
def validate_action(action: Action) -> ValidationResult:
    if action.type == "delete" and not is_in_workspace(action.target):
        return ValidationResult(allowed=False, reason="R001")

    if action.type == "system_command":
        return ValidationResult(allowed=False, reason="R002")

    if action.type == "network_request" and not is_known_domain(action.url):
        return ValidationResult(allowed=False, reason="R003", requires_user_approval=True)

    return ValidationResult(allowed=True)
```

---

## 7. Development Roadmap

### Phase 0: Environment Setup (Week 1) - **IN PROGRESS**
- [x] Create project structure
- [ ] Install vLLM + Qwen2.5-VL-32B-Instruct
- [ ] Test inference on sample screenshot
- [ ] Verify RTX 5090 performance (latency, VRAM usage)

### Phase 1: VLM Integration (Weeks 2-4)
- [ ] Implement `/analyze_screen` endpoint
- [ ] Screenshot capture utility
- [ ] VLM prompt engineering for UI detection
- [ ] Basic Electron GUI (chat interface)

### Phase 2: Plan Generation (Weeks 5-8)
- [ ] Integrate GPT-4 API for orchestration
- [ ] Implement `/generate_plan` endpoint
- [ ] Plan approval UI in Electron
- [ ] Feedback revision loop ("こうして")

### Phase 3: Action Executor (Weeks 9-12)
- [ ] PyAutoGUI integration (mouse/keyboard)
- [ ] Playwright integration (browser)
- [ ] Rule Engine implementation
- [ ] Error handling and recovery

### Phase 4: Excel Integration (Weeks 13-18)
- [ ] openpyxl wrapper for Excel operations
- [ ] Cell reading/writing/formula insertion
- [ ] Range operations (sum, average, etc.)

### Phase 5: PoC Packaging (Weeks 19-24)
- [ ] Windows installer (MSI or EXE)
- [ ] Demo scenarios (browser + Excel workflows)
- [ ] Customer presentation materials (Japanese)
- [ ] Pricing calculator for custom fine-tuning

---

## 8. Next Steps

**Immediate (Phase 0)**:
1. Complete PyTorch + vLLM installation
2. Download Qwen2.5-VL-32B-Instruct model
3. Run test inference on sample screenshot
4. Measure inference latency and VRAM usage

**Week 2 Start (Phase 1)**:
1. Create FastAPI server skeleton
2. Implement `/analyze_screen` endpoint
3. Build basic Electron app with text input
4. Test end-to-end flow (screenshot → VLM → GUI display)

---

**Document Version**: 0.1.0
**Last Updated**: 2025-12-11
**Author**: Claude Code + User (ultrathink spec)
