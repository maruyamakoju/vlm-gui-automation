@echo off
REM Activation script for VLM GUI Automation environment

echo ====================================================================
echo VLM GUI Automation - Environment Activation
echo ====================================================================
echo.

REM Activate conda environment
call C:\Users\07013\miniconda3\Scripts\activate.bat vlm-gui

echo Environment activated: vlm-gui
echo Python version:
python --version
echo.
echo GPU status:
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo.
echo Ready to work!
echo ====================================================================
