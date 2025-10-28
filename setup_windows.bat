@echo off
REM Setup script for Windows users
REM Copies project from WSL to Windows and installs dependencies

echo ========================================
echo Legal Advisory MCP Server Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Python found!
python --version
echo.

REM Create project directory in user's home
set PROJECT_DIR=%USERPROFILE%\legal-advisory-v5
echo [2/4] Setting up project directory: %PROJECT_DIR%

if exist "%PROJECT_DIR%" (
    echo     Directory already exists
) else (
    echo     Creating directory...
    mkdir "%PROJECT_DIR%"
)
echo.

REM Copy files from WSL (if applicable)
echo [3/4] Copying project files...
echo     (This assumes WSL is accessible)
echo     If this fails, manually copy from WSL to Windows
echo.

wsl cp -r /home/claude/legal-advisory-v5/* "%PROJECT_DIR%/" 2>nul
if errorlevel 1 (
    echo     WARNING: Could not copy from WSL automatically
    echo     Please manually copy project files to: %PROJECT_DIR%
    echo.
    echo     In WSL, run:
    echo     cp -r /home/claude/legal-advisory-v5 /mnt/c/Users/%USERNAME%/
    echo.
    pause
) else (
    echo     Files copied successfully!
)
echo.

REM Install Python dependencies
echo [4/4] Installing Python dependencies...
cd "%PROJECT_DIR%"
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Project location: %PROJECT_DIR%
echo.
echo NEXT STEPS:
echo 1. Open Claude Desktop configuration file:
echo    %APPDATA%\Claude\claude_desktop_config.json
echo.
echo 2. Add this configuration:
echo.
echo {
echo   "mcpServers": {
echo     "singapore-legal-rag": {
echo       "command": "python",
echo       "args": ["-m", "backend.mcp.servers.legal_mcp_server"],
echo       "cwd": "%PROJECT_DIR%",
echo       "env": {
echo         "PYTHONPATH": "%PROJECT_DIR%"
echo       }
echo     }
echo   }
echo }
echo.
echo 3. Restart Claude Desktop completely
echo.
echo 4. Test with query: "Calculate costs for a $50,000 High Court default judgment"
echo.
echo For detailed instructions, see:
echo %PROJECT_DIR%\CLAUDE_DESKTOP_SETUP.md
echo.
pause
