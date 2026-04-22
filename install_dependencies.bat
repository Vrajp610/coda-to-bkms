@echo off
REM install_dependencies.bat
REM Windows batch script to install Python, Node.js/npm, and all project dependencies automatically
setlocal

REM If the repo is clean, sync latest changes from origin/master first
where git >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
    git rev-parse --is-inside-work-tree >nul 2>nul
    IF %ERRORLEVEL% EQU 0 (
        git remote get-url origin >nul 2>nul
        IF %ERRORLEVEL% EQU 0 (
            git status --porcelain > "%TEMP%\bkms_git_status.txt"
            FOR %%A IN ("%TEMP%\bkms_git_status.txt") DO SET GIT_STATUS_SIZE=%%~zA
            IF "%GIT_STATUS_SIZE%"=="0" (
                echo Syncing latest code from origin/master...
                git pull --ff-only origin master || echo git pull failed. Continuing with existing local code.
            ) ELSE (
                echo Local git changes detected. Skipping git pull from origin/master.
            )
            del "%TEMP%\bkms_git_status.txt" >nul 2>nul
        )
    )
)

REM Check for Python
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Installing Python via winget...
    winget install -e --id Python.Python.3 || (
        echo winget not found or failed. Please install Python manually.
        exit /b 1
    )
)

REM Create local virtualenv if missing
IF NOT EXIST ".venv\Scripts\python.exe" (
    echo Creating local virtual environment...
    python -m venv .venv || (
        echo Failed to create .venv
        exit /b 1
    )
)

REM Check for pip inside virtualenv
IF NOT EXIST ".venv\Scripts\pip.exe" (
    echo pip not found in .venv. Installing pip...
    .venv\Scripts\python.exe -m ensurepip --upgrade
)

REM Upgrade pip and install backend dependencies inside virtualenv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

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
