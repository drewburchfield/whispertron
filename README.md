# WhisperTron 🎙️ [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Made for Apple Silicon](https://img.shields.io/badge/Made%20for-Apple%20Silicon-green.svg)](https://www.apple.com/mac/m-series/)

> A lightning-fast, privacy-first audio transcription system powered by OpenAI's Whisper model via whisper.cpp with Apple Silicon optimizations.

WhisperTron lets you transcribe voice memos, interviews, podcasts and more - all on your local machine with no data ever leaving your computer.

<p align="center">
  <img src="assets/images/whispertron-screenshot.png" alt="WhisperTron Screenshot" width="80%">
</p>

## ✨ Features

- **🔒 Completely Local**: All processing happens on your machine - no data sent to any external service
- **⚡ Apple Silicon Optimized**: Uses Metal and CoreML acceleration for much faster transcription on M1/M2/M3/M4 Macs
- **📝 Multiple Output Formats**: Generates text (.txt), subtitles (.srt), and web subtitles (.vtt)
- **🖱️ User-Friendly Interface**: Simple drag-and-drop interface for audio files
- **🧠 Model Selection**: Choose from various Whisper models (tiny.en through large-v3)
- **📱 Voice Memo Compatible**: Works directly with iOS Voice Memos (.m4a files)
- **⏱️ Timestamped Output**: Creates subtitles with accurate timestamps

## 🚀 Getting Started

### Prerequisites

- macOS (Apple Silicon recommended for best performance)
- Python 3.11+
- FFmpeg (for audio format conversion)
- Git

### Installation

1. Clone this repository:
   ```bash
   git clone --recurse-submodules https://github.com/drewburchfield/whispertron.git
   cd whispertron
   ```

2. Run the setup script to initialize the environment and build whisper.cpp:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   This script will:
   - Create a Python virtual environment
   - Install required packages
   - Clone and build whisper.cpp with Apple Silicon optimizations
   - Download the tiny.en model for initial testing
   - Set up necessary directory structure

3. Launch the application:
   ```bash
   python whispertron.py
   ```

## 📖 Usage

### GUI Interface

1. Launch WhisperTron: `python whispertron.py`
2. Drag and drop audio files onto the application or use the "Browse Files" button
3. Select your desired model and output formats
4. Wait for transcription to complete
5. Transcribed files will be saved in the "exports" directory with timestamp-based folders

### Command Line Interface

For batch processing or automation, use the included CLI:

```bash
./transcribe.sh -m medium.en -f txt,srt,vtt recording.m4a
```

Options:
- `-m, --model MODEL`: Specify model to use (default: tiny.en)
- `-l, --language LANG`: Specify language code (default: auto-detect)
- `-f, --formats FORMATS`: Comma-separated output formats (default: txt,srt,vtt)
- `-h, --help`: Show help message

## 🧠 Models

WhisperTron supports the following models:

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny.en | ~75MB | ⚡⚡⚡⚡⚡ | ⭐☆☆☆☆ | Quick testing, short clips |
| base.en | ~142MB | ⚡⚡⚡⚡ | ⭐⭐☆☆☆ | Short voice memos |
| small.en | ~466MB | ⚡⚡⚡ | ⭐⭐⭐☆☆ | Good balance for most uses |
| medium.en | ~1.5GB | ⚡⚡ | ⭐⭐⭐⭐☆ | High accuracy needs |
| large-v3 | ~3GB | ⚡ | ⭐⭐⭐⭐⭐ | Critical transcriptions |

To download additional models, run:
```bash
cd whisper.cpp && ./models/download-ggml-model.sh MODEL_NAME
```

> **Note**: The first time you use a model with CoreML, it will need to compile (may take up to 1 minute)

## 💡 Performance Tips

1. Start with the tiny.en model to test your setup (fastest but least accurate)
2. For longer recordings, medium.en offers a good balance of speed and accuracy
3. For critical transcriptions where accuracy is essential, use large-v3
4. M1/M2/M3/M4 Macs provide significantly better performance than Intel-based Macs

## 🗂️ Project Structure

- `src/`: Core transcription engine with Python interface to whisper.cpp
- `ui/`: PyQt6-based user interface
- `bin/`: Executable binaries
- `models/`: Whisper model files location
- `exports/`: Output directory for transcribed files
- `whisper.cpp/`: C++ implementation of Whisper with Apple Silicon optimizations

## 🔧 Troubleshooting

- **No audio transcription**: Ensure FFmpeg is installed (`brew install ffmpeg` on macOS)
- **"Model not found" error**: Make sure you've downloaded the model you're trying to use
- **Performance issues**: Try a smaller model if transcription is too slow
- **M4A format issues**: The app should automatically convert these, but if not, manually convert to WAV

## 👥 Contributing

Contributions are welcome! Please check out our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report bugs, and suggest features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - The original Whisper model
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - C++ implementation with Apple Silicon optimization 

## 📬 Contact

Drew Burchfield - [drewburchfield.com](https://drewburchfield.com)

Project Link: [https://github.com/drewburchfield/whispertron](https://github.com/drewburchfield/whispertron)

---

<p align="center">
  Made with ❤️ in 2025
</p> 
