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

# Check if Ollama is running (optional check)
print_status "Checking Ollama service..."
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama service is running"
    else
        print_warning "Ollama is installed but service might not be running"
        print_warning "Make sure Ollama is running: ollama serve"
    fi
else
    print_warning "Ollama not found. The app requires Ollama to be installed and running."
    print_warning "Install from: https://ollama.ai"
fi

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

