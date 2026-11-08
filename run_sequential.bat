@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run setup_windows.ps1 first. See docs\SEQUENTIAL.md.
  exit /b 1
)
if "%~1"=="" (
  echo Usage: run_sequential.bat national ^| tutorials
  echo The runner resumes its saved state. It stops on any failure.
  exit /b 1
)
if not "%~1"=="national" if not "%~1"=="tutorials" (
  echo Choose national or tutorials.
  exit /b 1
)
".venv\Scripts\python.exe" -m bdgee.batch --mode "%~1" --run
set "BDGEE_EXIT=%ERRORLEVEL%"
if not "%BDGEE_EXIT%"=="0" echo STOPPED: inspect the saved state and worker logs before resuming.
exit /b %BDGEE_EXIT%
