@echo off
REM VLM GUI Automation - Start server on port 8002

setlocal

REM プロジェクトルートに移動
cd /d C:\Users\07013\Desktop\vlm-gui-automation\backend

REM 環境設定（ダミー VLM モード）
set USE_DUMMY_VLM=true

echo ==============================================
echo Starting VLM GUI backend on port 8002...
echo ==============================================
echo.

"C:\Users\07013\miniconda3\envs\vlm-gui\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8002

endlocal
