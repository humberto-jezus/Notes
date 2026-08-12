@echo off
cd /d "%~dp0"
if exist "%~dp0\venv\Scripts\python.exe" (
  "%~dp0\venv\Scripts\python.exe" app.py
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    python app.py
  ) else (
    where python3 >nul 2>nul
    if %errorlevel%==0 (
      python3 app.py
    ) else (
      echo Nenhum interpretador Python encontrado.
      echo Instale o Python ou ajuste o PATH para incluir python.exe.
    )
  )
)
pause
