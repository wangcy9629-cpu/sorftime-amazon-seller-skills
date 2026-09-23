@echo off
setlocal
set "PY=C:\Users\HUAWEI\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%~dp0server.py" --port 8787 --open
pause
