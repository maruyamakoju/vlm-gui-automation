@echo off
REM VLM GUI Automation - Run quality test suite (8/8)

setlocal

cd /d C:\Users\07013\Desktop\vlm-gui-automation\backend

echo ==============================================
echo Running product quality tests (8/8)...
echo ==============================================
echo.

"C:\Users\07013\miniconda3\envs\vlm-gui\python.exe" test_product_quality.py

endlocal
