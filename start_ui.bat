@echo off
call D:\ProgramData\anaconda3\condabin\conda.bat activate ai
set AITK_PYTHON_PATH=D:\Anaconda_envs\envs\ai\python.exe
set HF_HOME=D:\huggingface_cache
set HF_HUB_ENABLE_HF_TRANSFER=1
set HF_ENDPOINT=https://hf-mirror.com
set DISABLE_TELEMETRY=YES
cd /d "%~dp0ui"
npm run dev
pause
