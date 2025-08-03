@echo off
REM install_dependencies.bat
REM Windows batch script to install Python, Node.js/npm, and all project dependencies automatically

REM Check for Python
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Installing Python via winget...
    winget install -e --id Python.Python.3 || (
        echo winget not found or failed. Please install Python manually.
        exit /b 1
    )
)

REM Check for pip
where pip >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo pip not found. Installing pip...
    python -m ensurepip --upgrade
)

REM Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Check for Node.js
where node >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Node.js not found. Installing Node.js via winget...
    winget install -e --id OpenJS.NodeJS.LTS || (
        echo winget not found or failed. Please install Node.js manually.
        exit /b 1
    )
)

REM Check for npm
where npm >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo npm not found. Node.js install may have failed. Please install Node.js manually.
    exit /b 1
)

REM Install UI dependencies
cd ui
npm install
cd ..

echo All dependencies installed!
