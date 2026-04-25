#!/bin/bash
# install_dependencies.sh
# Cross-platform script to install backend and UI dependencies

set -e

# If the script is sourced or run without execute permissions, print a helpful message
if [ ! -x "$0" ]; then
    echo "zsh: permission denied: $0"
    echo "To fix: run the following command and try again:"
    echo "    chmod +x $0"
    echo "Then run:"
    echo "    ./$(basename $0)"
    chmod +x "$0" 2>/dev/null
    if [ ! -x "$0" ]; then
        echo "Failed to set executable permissions automatically. Please run: chmod +x $0 and then re-run the script."
        exit 1
    fi
    exec "$0" "$@"
    exit
fi

# Detect OS
OS="$(uname -s)"


# Install Homebrew if missing (macOS only)
install_brew_if_missing() {
    if [[ "$OS" == "Darwin" ]]; then
        if ! command -v brew &>/dev/null; then
            echo "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            # Add Homebrew to PATH for current session
            if [[ -d "/opt/homebrew/bin" ]]; then
                export PATH="/opt/homebrew/bin:$PATH"
            elif [[ -d "/usr/local/bin" ]]; then
                export PATH="/usr/local/bin:$PATH"
            fi
        fi
    fi
}

# Install Python if missing (macOS/Linux only)
install_python_if_missing() {
    if command -v python3 &>/dev/null; then
        PYTHON=python3
    elif command -v python &>/dev/null; then
        PYTHON=python
    else
        echo "Python is not installed. Attempting to install Python..."
        if [[ "$OS" == "Darwin" ]]; then
            install_brew_if_missing
            brew install python
        elif [[ "$OS" == "Linux" ]]; then
            if command -v apt-get &>/dev/null; then
                sudo apt-get update && sudo apt-get install -y python3 python3-pip
                PYTHON=python3
            elif command -v yum &>/dev/null; then
                sudo yum install -y python3 python3-pip
                PYTHON=python3
            else
                echo "Unsupported Linux package manager. Please install Python manually."
                exit 1
            fi
        else
            echo "Unsupported OS. Please install Python manually."
            exit 1
        fi
    fi
}

# Install Node.js/npm if missing (macOS/Linux only)
install_node_if_missing() {
    if command -v node &>/dev/null && command -v npm &>/dev/null; then
        return
    fi
    echo "Node.js and/or npm not found. Attempting to install Node.js..."
    if [[ "$OS" == "Darwin" ]]; then
        install_brew_if_missing
        brew install node
    elif [[ "$OS" == "Linux" ]]; then
        if command -v apt-get &>/dev/null; then
            sudo apt-get update && sudo apt-get install -y nodejs npm
        elif command -v yum &>/dev/null; then
            sudo yum install -y nodejs npm
        else
            echo "Unsupported Linux package manager. Please install Node.js and npm manually."
            exit 1
        fi
    else
        echo "Unsupported OS. Please install Node.js and npm manually."
        exit 1
    fi
}

# Backend dependencies
install_backend() {
    echo "Installing Python backend dependencies..."
    if command -v python3 &>/dev/null; then
        PYTHON=python3
    elif command -v python &>/dev/null; then
        PYTHON=python
    else
        echo "Python is not installed. Please install Python 3.7+ first."
        exit 1
    fi
    if [ ! -d ".venv" ]; then
        $PYTHON -m venv .venv
    fi
    ./.venv/bin/python -m pip install --upgrade pip
    ./.venv/bin/python -m pip install -r requirements.txt
}

# UI dependencies
install_ui() {
    echo "Installing UI (React) dependencies..."
    cd ui
    if command -v npm &>/dev/null; then
        npm install --legacy-peer-deps
    else
        echo "npm is not installed. Please install Node.js and npm first."
        exit 1
    fi
    cd ..
}

# Create .env template files if they don't exist
create_env_files() {
    if [ ! -f "backend/.env" ]; then
        echo "Creating backend/.env template..."
        cat > backend/.env <<'EOF'
MAIN_GROUP_TELEGRAM_TOKEN=
MAIN_GROUP_TELEGRAM_CHAT_ID=
SAT_K1_TELEGRAM_TOKEN=
SAT_K1_TELEGRAM_CHAT_ID=
SAT_K2_TELEGRAM_TOKEN=
SAT_K2_TELEGRAM_CHAT_ID=
SUN_K1_TELEGRAM_TOKEN=
SUN_K1_TELEGRAM_CHAT_ID=
SUN_K2_TELEGRAM_TOKEN=
SUN_K2_TELEGRAM_CHAT_ID=
CODA_API_KEY=
BKMS_ID=
BKMS_EMAIL=
BKMS_PASSWORD=
BKMS_ACCESS_TYPE=
SATURDAY_K1_TABLE_ID=
SATURDAY_K2_TABLE_ID=
SUNDAY_K1_TABLE_ID=
SUNDAY_K2_TABLE_ID=
CODA_DOC_ID=
GOSHTHI_9_10_TABLE_ID=
GOSHTHI_11_12_TABLE_ID=
GOSHTHI_COLLEGE_1_2_TABLE_ID=
GOSHTHI_COLLEGE_3_4_TABLE_ID=
BOT_TRIGGER_TOKEN=
PUBLIC_BASE_URL=
EOF
        echo "  → backend/.env created. Fill in your values before running the app."
    else
        echo "  → backend/.env already exists, skipping."
    fi

    if [ ! -f "ui/.env" ]; then
        echo "Creating ui/.env template..."
        cat > ui/.env <<'EOF'
# API URL - leave unset to auto-detect local 127.0.0.1:8000
# REACT_APP_API_URL=http://127.0.0.1:8000
REACT_APP_BKMS_TOKEN=
REACT_APP_SHOW_USER_UPDATE_BOT=
EOF
        echo "  → ui/.env created. Fill in your values before running the app."
    else
        echo "  → ui/.env already exists, skipping."
    fi
}

# Main
install_python_if_missing
install_node_if_missing
install_backend
install_ui
create_env_files

echo "All dependencies installed!"
