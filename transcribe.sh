#!/bin/bash
# WhisperTron - Command-line Interface for WhisperTron
# This script provides a simple CLI interface for transcription

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Activate virtual environment
source .venv/bin/activate || {
    echo -e "${RED}Error: Could not activate virtual environment. Run setup.sh first.${NC}"
    exit 1
}

# Display help
show_help() {
    echo -e "${BLUE}WhisperTron CLI${NC} - Command-line interface for transcription"
    echo ""
    echo "Usage: ./transcribe.sh [OPTIONS] <audio-file>"
    echo ""
    echo "Options:"
    echo "  -m, --model MODEL     Specify model to use (default: tiny.en)"
    echo "                        Available: tiny.en, base.en, small.en, medium.en, large-v3"
    echo "  -l, --language LANG   Specify language code (default: auto-detect)"
    echo "  -f, --formats FORMATS Comma-separated output formats (default: txt,srt,vtt)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Example:"
    echo "  ./transcribe.sh -m medium.en -f txt,srt recording.m4a"
    echo ""
}

# Default values
MODEL="tiny.en"
LANGUAGE=""
FORMATS="txt,srt,vtt"
FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -l|--language)
            LANGUAGE="$2"
            shift 2
            ;;
        -f|--formats)
            FORMATS="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [[ -z "$FILE" ]]; then
                FILE="$1"
                shift
            else
                echo -e "${RED}Error: Unknown argument: $1${NC}"
                show_help
                exit 1
            fi
            ;;
    esac
done

# Check if a file was provided
if [[ -z "$FILE" ]]; then
    echo -e "${RED}Error: No audio file specified.${NC}"
    show_help
    exit 1
fi

# Check if file exists
if [[ ! -f "$FILE" ]]; then
    echo -e "${RED}Error: File not found: $FILE${NC}"
    exit 1
fi

# Print summary
echo -e "${BLUE}┌─────────────────────────────────────┐${NC}"
echo -e "${BLUE}│   WhisperTron Transcription         │${NC}"
echo -e "${BLUE}└─────────────────────────────────────┘${NC}"
echo ""
echo -e "${YELLOW}File:${NC}      $FILE"
echo -e "${YELLOW}Model:${NC}     $MODEL"
echo -e "${YELLOW}Formats:${NC}   $FORMATS"
if [[ -n "$LANGUAGE" ]]; then
    echo -e "${YELLOW}Language:${NC}  $LANGUAGE"
else
    echo -e "${YELLOW}Language:${NC}  Auto-detect"
fi
echo ""
echo "Starting transcription..."

# Construct command
CMD="python src/transcribe.py \"$FILE\" --model \"$MODEL\" --formats \"$FORMATS\""
if [[ -n "$LANGUAGE" ]]; then
    CMD="$CMD --language \"$LANGUAGE\""
fi

# Run the transcription
eval $CMD

# If successful, open the exports directory
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Transcription complete!${NC}"
    echo -e "Opening exports folder..."
    open exports
fi 