#!/bin/bash
set -e

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}┌─────────────────────────────────────┐${NC}"
echo -e "${BLUE}│   WhisperTron Setup                 │${NC}"
echo -e "${BLUE}└─────────────────────────────────────┘${NC}"
echo ""

# Function to check dependencies
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is required but not found.${NC}"
        if [ "$2" ]; then
            echo -e "${YELLOW}Recommendation: $2${NC}"
        fi
        return 1
    else
        echo -e "${GREEN}✓ Found $1${NC}"
        return 0
    fi
}

# Check required dependencies
echo "Checking dependencies..."
check_dependency python3 "Install Python 3 from https://www.python.org/downloads/"
check_dependency git "Install Git from https://git-scm.com/downloads"
check_dependency ffmpeg "Install FFmpeg (for m4a conversion) with 'brew install ffmpeg' (macOS) or from https://ffmpeg.org/download.html"

# Check if running on Apple Silicon Mac
if [[ "$(uname)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
    echo -e "${GREEN}✓ Running on Apple Silicon Mac - Metal and CoreML optimizations will be enabled${NC}"
    ENABLE_METAL=1
    ENABLE_COREML=1
else
    echo -e "${YELLOW}⚠️ Not running on Apple Silicon Mac - Metal and CoreML optimizations will be disabled${NC}"
    ENABLE_METAL=0
    ENABLE_COREML=0
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    
    if [ ! -d ".venv" ]; then
        echo -e "${RED}Failed to create virtual environment. Please check your Python installation.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Using existing virtual environment${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install required packages
echo "Installing required Python packages..."
pip install --upgrade pip
pip install PyQt6 pandas pydub tqdm

# Create necessary directories
mkdir -p bin src ui exports models

# Check if whisper.cpp already exists
if [ ! -d "whisper.cpp" ]; then
    echo "Cloning whisper.cpp repository..."
    git clone https://github.com/ggerganov/whisper.cpp.git
    
    if [ ! -d "whisper.cpp" ]; then
        echo -e "${RED}Failed to clone whisper.cpp repository. Please check your internet connection.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Cloned whisper.cpp repository${NC}"
else
    echo -e "${GREEN}✓ Using existing whisper.cpp repository${NC}"
    # Pull latest changes
    echo "Updating whisper.cpp repository..."
    (
        cd whisper.cpp 
        # Check if we're in a detached HEAD state and handle it
        if git symbolic-ref -q HEAD >/dev/null; then
            # On a branch, just pull
            git pull
        else
            echo "Whisper.cpp is in detached HEAD state. Checking out main branch first..."
            git checkout main && git pull
        fi
    )
fi

# Build whisper.cpp
echo "Building whisper.cpp..."
cd whisper.cpp

# Set build flags based on platform
BUILD_COMMAND="make -j"
if [ "$ENABLE_METAL" == "1" ]; then
    BUILD_COMMAND="WHISPER_METAL=1 $BUILD_COMMAND"
fi
if [ "$ENABLE_COREML" == "1" ]; then
    BUILD_COMMAND="WHISPER_COREML=1 $BUILD_COMMAND"
fi

# Execute build
echo "Running: $BUILD_COMMAND"
eval $BUILD_COMMAND

if [ ! -f "build/bin/whisper-cli" ]; then
    echo -e "${RED}Failed to build whisper.cpp. Check build errors above.${NC}"
    cd ..
    exit 1
fi

echo -e "${GREEN}✓ Built whisper.cpp successfully${NC}"

# Download tiny.en model if no models exist
if [ ! -f "models/ggml-tiny.en.bin" ]; then
    echo "Downloading tiny.en model (smallest) for testing..."
    ./models/download-ggml-model.sh tiny.en
    
    if [ ! -f "models/ggml-tiny.en.bin" ]; then
        echo -e "${RED}Failed to download model. Check your internet connection.${NC}"
        cd ..
        exit 1
    fi
    
    echo -e "${GREEN}✓ Downloaded tiny.en model${NC}"
else
    echo -e "${GREEN}✓ Model already exists${NC}"
fi

cd ..

# Create symbolic links
echo "Setting up symbolic links..."
rm -f bin/whisper
ln -sf "$(pwd)/whisper.cpp/build/bin/whisper-cli" bin/whisper

# Remove duplicate symlink (we only need one in bin/)
rm -f src/whisper

# Set up models symlink
rm -f models/whisper_models
ln -sf "$(pwd)/whisper.cpp/models" models/whisper_models

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}┌─────────────────────────────────────┐${NC}"
echo -e "${BLUE}│   WhisperTron is ready!             │${NC}"
echo -e "${BLUE}└─────────────────────────────────────┘${NC}"
echo ""
echo -e "To start the application, run: ${YELLOW}python whispertron.py${NC}"
echo ""
echo -e "${YELLOW}Available models:${NC}"
echo "• tiny.en   - Fastest, least accurate"
echo "• base.en   - Fast with reasonable accuracy"
echo "• small.en  - Good balance between speed and accuracy"
echo "• medium.en - High accuracy, moderate speed"
echo "• large-v3  - Highest accuracy, slowest speed"
echo ""
echo -e "To download more models, run: ${YELLOW}cd whisper.cpp && ./models/download-ggml-model.sh MODEL_NAME${NC}"
echo "Example: cd whisper.cpp && ./models/download-ggml-model.sh base.en"
echo "" 