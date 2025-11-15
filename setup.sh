#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
PORT=8000
URL="http://localhost:${PORT}"
VENV_DIR="venv"
PYTHON_CMD="python3"

# Print header
echo -e "${CYAN}${BOLD}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     🚀 NIR - Navan Intelligent Recommender                 ║"
echo "║            Setup & Launch Script                           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if Python is installed
print_status "Checking Python installation..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_success "Python ${PYTHON_VERSION} found"

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_DIR/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install requirements
print_status "Installing project requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install requirements"
        exit 1
    fi
    print_success "Requirements installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Check and install Ollama if needed
print_status "Checking Ollama installation..."
# Models used in the application
REQUIRED_MODELS=("qwen3" "llama3.1:8b")

if ! command -v ollama &> /dev/null; then
    print_warning "Ollama not found. Installing Ollama..."
    print_status "Downloading and installing Ollama (this may take a moment)..."
    
    # Check OS type for installation method
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - try Homebrew first, then official installer
        if command -v brew &> /dev/null; then
            print_status "Installing Ollama via Homebrew..."
            if brew install ollama; then
                print_success "Ollama installed via Homebrew"
            else
                print_warning "Homebrew installation failed, trying official installer..."
                if curl -fsSL https://ollama.com/install.sh | sh; then
                    print_success "Ollama installed successfully"
                else
                    print_error "Failed to install Ollama automatically"
                    print_error "Please install Ollama manually from: https://ollama.ai"
                    exit 1
                fi
            fi
        else
            # macOS without Homebrew - use official installer
            if curl -fsSL https://ollama.com/install.sh | sh; then
                print_success "Ollama installed successfully"
            else
                print_error "Failed to install Ollama automatically"
                print_error "Please install Ollama manually from: https://ollama.ai"
                exit 1
            fi
        fi
        # Add common macOS paths
        export PATH="$PATH:/usr/local/bin:/opt/homebrew/bin"
    else
        # Linux - use official installer
        if curl -fsSL https://ollama.com/install.sh | sh; then
            print_success "Ollama installed successfully"
            # Add to PATH for Linux
            export PATH="$PATH:$HOME/.local/bin"
        else
            print_error "Failed to install Ollama automatically"
            print_error "Please install Ollama manually from: https://ollama.ai"
            exit 1
        fi
    fi
    
    # Verify installation
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama was installed but not found in PATH"
        print_error "Please restart your terminal or add Ollama to your PATH"
        print_error "Or run: export PATH=\"\$PATH:\$HOME/.local/bin\""
        exit 1
    fi
else
    print_success "Ollama is already installed"
fi

# Check if Ollama service is running, start if not
print_status "Checking Ollama service..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_success "Ollama service is running"
else
    print_status "Starting Ollama service in the background..."
    # Start Ollama in background
    nohup ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    
    # Wait a bit for Ollama to start
    sleep 3
    
    # Check if it started successfully
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama service started (PID: $OLLAMA_PID)"
    else
        print_warning "Ollama service might not have started. Trying to start manually..."
        # Try to start in background again
        ollama serve > /dev/null 2>&1 &
        sleep 2
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama service is now running"
        else
            print_error "Could not start Ollama service. Please run 'ollama serve' manually in another terminal."
            exit 1
        fi
    fi
fi

# Check and pull required models
print_status "Checking for required models..."
# Wait a moment for Ollama to be ready
sleep 1

for model in "${REQUIRED_MODELS[@]}"; do
    print_status "Checking model: ${model}..."
    # Check if model exists (handle both exact match and version variations)
    if ollama list 2>/dev/null | grep -q "${model}"; then
        print_success "Model ${model} is available"
    else
        print_status "Model ${model} not found. Pulling model (this may take several minutes)..."
        print_warning "This is a one-time download. Models are large (~GB), so please be patient..."
        if ollama pull ${model}; then
            print_success "Model ${model} pulled successfully"
        else
            print_error "Failed to pull model ${model}"
            print_error "Please run 'ollama pull ${model}' manually"
            print_warning "Continuing anyway - the app will show an error if the model is missing"
        fi
    fi
done

# Function to open browser
open_browser() {
    sleep 2
    print_status "Opening browser at ${URL}..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open $URL
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open $URL
        elif command -v gnome-open &> /dev/null; then
            gnome-open $URL
        else
            print_warning "Could not automatically open browser. Please visit: ${URL}"
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        start $URL
    else
        print_warning "Could not automatically open browser. Please visit: ${URL}"
    fi
}

# Start the server in background and open browser
print_status "Starting FastAPI server..."
echo -e "\n${CYAN}${BOLD}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}Server starting on: ${URL}${NC}"
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════${NC}\n"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}\n"

# Open browser in background
open_browser &

# Run the server
python -m app.main.main

