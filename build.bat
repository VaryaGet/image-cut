@echo off
chcp 65001 >nul
echo ============================================
echo   Batch Image Processor - Build Script
echo ============================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/3] Building executable...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "BatchImageProcessor" ^
    --add-data "ui;ui" ^
    --add-data "workers;workers" ^
    --add-data "image_processing;image_processing" ^
    --add-data "utils;utils" ^
    --add-data "settings;settings" ^
    --hidden-import rembg ^
    --hidden-import rembg.session_factory ^
    --hidden-import rembg.session_base ^
    --hidden-import onnxruntime ^
    --hidden-import numpy ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --collect-all rembg ^
    --collect-all onnxruntime ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo [3/3] Build successful!
    echo Executable: dist\BatchImageProcessor.exe
) else (
    echo.
    echo BUILD FAILED. Check errors above.
)

pause
