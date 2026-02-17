@echo off
echo ==========================================
echo Building Revisor de Textos (Secure Build)
echo ==========================================

REM Ensure we are in the project root
if not exist "main.py" (
    echo Error: main.py not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Run PyInstaller
REM --onefile: Create a single executable
REM --noconsole: Don't show terminal window (GUI app)
REM --clean: Clean cache
REM --name: Executable name
echo Running PyInstaller...
python -m PyInstaller --noconsole ^
            --onefile ^
            --name "RevisorTextos" ^
            --clean ^
            --exclude-module notebook ^
            --exclude-module ipython ^
            --exclude-module pytest ^
            main.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo ==========================================
echo Build complete successfully!
echo Executable located at: dist\RevisorTextos.exe
echo ==========================================
echo.
echo Note: This executable does NOT contain any API keys.
echo The user needs to configure keys in the application settings.
echo.
pause
