@echo off
cd /d "%~dp0"
set "PY_EXE="
if exist "%~dp0\venv\Scripts\pythonw.exe" set "PY_EXE=%~dp0\venv\Scripts\pythonw.exe"
if not defined PY_EXE if exist "%~dp0\venv\Scripts\python.exe" set "PY_EXE=%~dp0\venv\Scripts\python.exe"
if not defined PY_EXE (
  where pythonw >nul 2>nul && set "PY_EXE=pythonw"
)
if not defined PY_EXE (
  where python >nul 2>nul && set "PY_EXE=python"
)
if not defined PY_EXE (
  where python3 >nul 2>nul && set "PY_EXE=python3"
)
if defined PY_EXE (
  if "%PY_EXE%"=="python" (
    start "" python "%~dp0app.py"
  ) else if "%PY_EXE%"=="python3" (
    start "" python3 "%~dp0app.py"
  ) else (
    start "" "%PY_EXE%" "%~dp0app.py"
  )
) else (
  echo Nenhum interpretador Python encontrado.
  echo Instale o Python ou ajuste o PATH para incluir python.exe.
  pause
)
