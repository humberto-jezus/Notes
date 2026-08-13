@echo off
cd /d "%~dp0"
set "PY_EXE="

:: prefer pythonw from venv (no console window)
if exist "%~dp0\venv\Scripts\pythonw.exe" set "PY_EXE=%~dp0\venv\Scripts\pythonw.exe"

:: fallback: derive pythonw from python in venv
if not defined PY_EXE if exist "%~dp0\venv\Scripts\python.exe" set "PY_EXE=%~dp0\venv\Scripts\pythonw.exe"

:: fallback: system pythonw
if not defined PY_EXE (
  where pythonw >nul 2>nul && set "PY_EXE=pythonw"
)

:: fallback: derive pythonw from system python location
if not defined PY_EXE (
  for /f "delims=" %%i in ('where python 2^>nul') do (
    if not defined PY_EXE (
      set "PY_EXE=%%~dpi\pythonw.exe"
      if not exist "%%~dpi\pythonw.exe" set "PY_EXE="
    )
  )
)

if defined PY_EXE (
  start "" "%PY_EXE%" "%~dp0app.py"
) else (
  echo Nenhum interpretador Python encontrado.
  echo Instale o Python ou ajuste o PATH para incluir python.exe.
  pause
)
