#!/bin/bash

# Multimodal AI System Setup Script
# This script automates the setup process for the multimodal AI system

set -e  # Exit on any error

echo "🤖 Multimodal AI System Setup"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is not installed. Please install pip."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_status "Activating virtual environment and installing dependencies..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Check if Ollama is installed
check_ollama() {
    print_status "Checking Ollama installation..."
    if command -v ollama &> /dev/null; then
        print_success "Ollama found"
        
        # Check if Ollama is running
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            print_success "Ollama is running"
        else
            print_warning "Ollama is installed but not running"
            print_status "Starting Ollama service..."
            ollama serve &
            sleep 5
        fi
        
        # Check if required model is available
        if ollama list | grep -q "llama3.1:8b"; then
            print_success "Required model (llama3.1:8b) is available"
        else
            print_warning "Required model not found. Downloading..."
            ollama pull llama3.1:8b
            print_success "Model downloaded"
        fi
    else
        print_error "Ollama is not installed. Please install Ollama from https://ollama.ai/"
        print_status "After installing Ollama, run: ollama pull llama3.1:8b"
        exit 1
    fi
}

# Check if FFmpeg is installed
check_ffmpeg() {
    print_status "Checking FFmpeg installation..."
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg found"
    else
        print_warning "FFmpeg is not installed. Audio processing may not work properly."
        print_status "Please install FFmpeg:"
        print_status "  Ubuntu/Debian: sudo apt install ffmpeg"
        print_status "  macOS: brew install ffmpeg"
        print_status "  Windows: Download from https://ffmpeg.org/"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p models data temp static/css static/js templates
    print_success "Directories created"
}

# Download Vosk model
download_vosk_model() {
    print_status "Checking Vosk model..."
    if [ ! -d "models/vosk-model-small-en-us-0.15" ]; then
        print_status "Downloading Vosk model (this may take a while)..."
        mkdir -p models
        cd models
        wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
        unzip -q vosk-model-small-en-us-0.15.zip
        rm vosk-model-small-en-us-0.15.zip
        cd ..
        print_success "Vosk model downloaded"
    else
        print_success "Vosk model already present"
    fi
}

# Test the installation
test_installation() {
    print_status "Testing installation..."
    source .venv/bin/activate
    python -c "
import sys
try:
    import torch, transformers, pyttsx3, vosk, fastapi, uvicorn
    print('✓ All Python dependencies imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    print_success "Installation test passed"
}

# Main setup function
main() {
    echo
    print_status "Starting setup process..."
    echo
    
    check_python
    check_pip
    create_venv
    install_dependencies
    check_ollama
    check_ffmpeg
    create_directories
    download_vosk_model
    test_installation
    
    echo
    print_success "Setup completed successfully! 🎉"
    echo
    print_status "To start the system:"
    print_status "  source .venv/bin/activate"
    print_status "  python main.py"
    echo
    print_status "Then open your browser and go to: http://localhost:8000"
    echo
}

# Run main function
main