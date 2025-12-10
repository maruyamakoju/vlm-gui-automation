# VLM GUI Automation Agent

**Vision Language Model-based GUI automation for Japanese enterprises**

## Overview

This project enables non-technical users to automate GUI tasks using natural language commands. The system uses Vision Language Models (VLMs) to understand screen content and generate action plans, with human approval before execution.

## Target Users

- Japanese SME back-office staff (non-engineers)
- Initial focus: Chrome browser + Excel automation

## Architecture

- **Frontend**: Electron + React + TypeScript
- **Backend**: Python + FastAPI
- **VLM Service**: Qwen2.5-VL-32B-Instruct (4bit/8bit quantization)
- **Action Executor**: PyAutoGUI, pywinauto, Playwright
- **Inference**: vLLM / LMDeploy on RTX 5090

## Development Phases

### Phase 0: Environment Setup (Week 1) - **IN PROGRESS**
- [x] Create project structure
- [ ] Set up Qwen2.5-VL-32B-Instruct on RTX 5090
- [ ] vLLM / LMDeploy inference server
- [ ] Python development environment

### Phase 1: Basic VLM Integration (Weeks 2-4)
- [ ] FastAPI server with `/analyze_screen` endpoint
- [ ] Screenshot capture and VLM inference
- [ ] Basic Electron UI
- [ ] Action Executor v0 (PyAutoGUI single-click automation)

### Phase 2: Plan Generation (Weeks 5-8)
- [ ] GPT-4 Orchestrator for multi-step plan generation
- [ ] Plan approval workflow in GUI
- [ ] Feedback revision loop ("こうして")

### Phase 3: Rule Engine & Safety (Weeks 9-12)
- [ ] Safety constraints and validation
- [ ] Rule Engine for action approval
- [ ] Error handling and recovery

### Phase 4: Excel Integration (Weeks 13-18)
- [ ] Excel automation support
- [ ] Cell reading/writing via openpyxl

### Phase 5: PoC Packaging (Weeks 19-24)
- [ ] Windows installer
- [ ] Demo scenarios
- [ ] Customer presentation materials

## Hardware Requirements

- NVIDIA RTX 5090 (24GB VRAM)
- Windows 11
- 32GB+ RAM recommended

## Business Model

Custom VLM fine-tuning service for Japanese enterprises:
- ¥300万-2000万 per project
- Data sovereignty (on-premise deployment)
- Japanese language optimization
- Cost reduction vs GPT-4V

## License

Proprietary - All rights reserved

---

**Status**: Phase 0 - Environment Setup (2025-12-11)
