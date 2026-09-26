@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run.py
    goto done
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 run.py
    goto done
)
where python >nul 2>nul
if not errorlevel 1 (
    python run.py
    goto done
)
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" run.py
    goto done
)
echo Python was not found. Install Python 3.10 or newer from:
echo https://www.python.org/downloads/windows/
pause
exit /b 1
:done
if errorlevel 1 pause
