# Multimodal AI System

A fully local, censorship-free multimodal AI system with vocal responses and read aloud features. This system provides text, audio, and image processing capabilities entirely offline, ensuring complete privacy and freedom from external censorship.

## 🌟 Features

### Core Capabilities
- **Text Processing**: Advanced language understanding and generation
- **Speech-to-Text**: Convert voice input to text using Vosk
- **Text-to-Speech**: Convert responses to natural speech with multiple voice options
- **Image Analysis**: OCR text extraction and image description
- **Multimodal Processing**: Combined text, audio, and image understanding

### Privacy & Freedom
- **100% Local**: No data sent to external servers
- **Censorship-Free**: No content filtering or restrictions
- **Offline Operation**: Works without internet connection
- **Open Source**: Fully transparent and customizable

### User Interface
- **Modern Web Interface**: Clean, responsive design with dark/light themes
- **Real-time Communication**: WebSocket-based instant responses
- **Voice Controls**: Click-to-talk voice input
- **Image Upload**: Drag-and-drop image processing
- **Conversation Memory**: Context-aware conversations

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running (for language model)
3. **FFmpeg** installed (for audio processing)

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd multimodal-ai-system
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install Ollama**:
```bash
# Install Ollama from https://ollama.ai/
# Then pull the language model:
ollama pull llama3.1:8b
```

3. **Run setup**:
```bash
python main.py --setup
```

4. **Start the system**:
```bash
python main.py
```

5. **Open your browser** and go to `http://localhost:8000`

## 🎯 Usage

### Web Interface

1. **Text Chat**: Type messages in the input field and press Enter
2. **Voice Input**: Click the microphone button to record voice input
3. **Image Upload**: Click the image button to upload and analyze images
4. **Settings**: Click the gear icon to customize voice, theme, and behavior

### CLI Mode

For testing and development:
```bash
python main.py --mode cli
```

Commands:
- Type a message and press Enter to chat
- Type `voice` to start voice input
- Type `image <path>` to process an image
- Type `quit` to exit

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Audio settings
TTS_VOICE_ID=your_preferred_voice_id
TTS_RATE=200

# Model settings
LLM_MODEL=llama3.1:8b
DEVICE=auto

# UI settings
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### Voice Configuration

The system automatically detects available TTS voices. You can:
- Select different voices in the settings
- Adjust speech rate and volume
- Enable/disable auto-speak responses

### Model Configuration

Edit `config.py` to customize:
- Language model (Ollama model name)
- Embedding model for semantic search
- Image processing models
- Audio processing parameters

## 🏗️ Architecture

### Components

1. **AI Models** (`ai_models.py`):
   - Local LLM interface via Ollama
   - Image processing (BLIP for captioning, EasyOCR for text extraction)
   - Embedding model for semantic search
   - Multimodal coordination

2. **Audio Processing** (`audio_processor.py`):
   - Text-to-Speech (pyttsx3)
   - Speech-to-Text (Vosk)
   - Audio playback and file handling

3. **Web Interface** (`web_interface.py`):
   - FastAPI backend
   - WebSocket real-time communication
   - File upload handling
   - REST API endpoints

4. **Configuration** (`config.py`):
   - Centralized settings management
   - Environment variable support
   - Model and system configuration

### Data Flow

```
User Input → Web Interface → AI Models → Audio Processor → Response
     ↓              ↓            ↓            ↓
Voice/Text → WebSocket → LLM/Image → TTS → Audio Output
```

## 🔧 Advanced Usage

### Custom Models

To use different models, modify `config.py`:

```python
class ModelConfig(BaseModel):
    llm_model: str = "your-custom-model"  # Ollama model name
    embedding_model: str = "your-embedding-model"
    image_model: str = "your-image-model"
```

### API Endpoints

The system provides REST API endpoints:

- `POST /api/chat` - Send text/image message
- `POST /api/transcribe` - Transcribe audio
- `POST /api/speak` - Convert text to speech
- `GET /api/voices` - Get available voices
- `GET /api/conversation` - Get chat history
- `DELETE /api/conversation` - Clear history

### WebSocket Events

Real-time communication via WebSocket:

- `chat` - Send text message
- `voice_input` - Start voice recording
- `response` - Receive AI response
- `voice_response` - Receive transcribed + response

## 🛠️ Development

### Project Structure

```
multimodal-ai-system/
├── main.py                 # Main entry point
├── config.py              # Configuration management
├── ai_models.py           # AI model interfaces
├── audio_processor.py     # Audio processing
├── web_interface.py       # Web interface
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   └── index.html
├── static/                # Static assets
│   ├── css/style.css
│   └── js/app.js
├── models/                # Downloaded models
└── data/                  # Application data
```

### Adding New Features

1. **New AI Models**: Extend `ai_models.py`
2. **Audio Features**: Extend `audio_processor.py`
3. **UI Components**: Modify templates and static files
4. **API Endpoints**: Add to `web_interface.py`

### Testing

```bash
# Run in debug mode
python main.py --debug

# Test CLI mode
python main.py --mode cli

# Test specific components
python -c "from ai_models import MultimodalAI; ai = MultimodalAI()"
```

## 🔒 Privacy & Security

### Data Handling
- All processing happens locally
- No data is sent to external services
- Temporary files are cleaned up automatically
- Conversation history is stored in memory only

### Security Considerations
- Web interface runs on localhost by default
- No authentication (suitable for local use)
- File uploads are validated and limited in size
- Temporary files are automatically cleaned

## 🐛 Troubleshooting

### Common Issues

1. **Ollama not responding**:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama
   ollama serve
   ```

2. **Audio not working**:
   - Check if microphone permissions are granted
   - Verify audio drivers are working
   - Try different TTS voices

3. **Model download fails**:
   - Check internet connection
   - Verify disk space
   - Try manual download

4. **Web interface not loading**:
   - Check if port 8000 is available
   - Try different port: `python main.py --port 8001`
   - Check firewall settings

### Debug Mode

Run with debug logging:
```bash
python main.py --debug
```

### Logs

Logs are displayed in the console. For production, configure loguru to write to files.

## 📝 License

This project is open source. See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

## 🔄 Updates

To update the system:
1. Pull latest changes
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Update models if needed
4. Restart the system

---

**Enjoy your fully local, censorship-free multimodal AI system!** 🎉