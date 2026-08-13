@echo off
cd /d "%~dp0"
if exist "%~dp0\venv\Scripts\pythonw.exe" (
  start "" "%~dp0\venv\Scripts\pythonw.exe" app.py
) else (
  for /f "delims=" %%i in ('where python 2^>nul') do (
    if exist "%%~dpi\pythonw.exe" (
      start "" "%%~dpi\pythonw.exe" app.py
      exit /b
    )
  )
  where pythonw >nul 2>nul && start "" pythonw app.py || (
    echo Nenhum interpretador Python encontrado.
    pause
  )
)
