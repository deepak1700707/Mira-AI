# Mira-AI 🤖

A voice-activated AI assistant with emotion detection, bilingual support (Hindi/English), and intelligent tool integration.

## ✨ Features

- 🎙️ **Voice Recognition** - OpenAI Whisper for accurate speech-to-text
- 🗣️ **Text-to-Speech** - Edge TTS with emotion-based voice modulation
- 🧠 **AI Brain** - Ollama LLM with LangChain agents for intelligent responses
- 😊 **Emotion Detection** - Detects user emotions and adapts response tone
- 🌐 **Bilingual Support** - Automatic Hindi/English detection and responses
- 🛠️ **Tool Integration** - Weather, time, web search, and custom tools
- 💾 **Conversation Memory** - Persistent memory with automatic cleanup
- 🎯 **Voice Activity Detection** - Automatic recording stop when speech ends
- 📊 **Logging** - Comprehensive logging for debugging and monitoring

## 📋 Requirements

- Python 3.8+
- Ollama installed and running (for LLM)
- Microphone for voice input
- API keys (optional, for weather and search features)

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Mira-AI
```

2. **Create a virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

**Note**: If you get build errors (especially on Windows), `webrtcvad` is optional. The VAD feature will work using amplitude-based detection without it.

**Optional - Wake Word Detection**: For true hands-free operation, install Porcupine:
```bash
pip install pvporcupine
```
Without Porcupine, wake word detection works using keyword matching in transcribed text.

4. **Install Ollama:**
   - Visit [https://ollama.ai](https://ollama.ai) and install Ollama
   - Pull the required model:
```bash
ollama pull qwen2.5:7b
# Or use a smaller model if you have limited RAM:
ollama pull qwen2.5:1.5b
```

5. **Configure environment variables:**
   - Copy `env_example.txt` to `.env`
   - Fill in your API keys:
```bash
cp env_example.txt .env
# Edit .env with your API keys
```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# API Keys
OPENWEATHER_API_KEY=your_openweather_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Ollama Configuration
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434

# Recording Configuration
RECORDING_DURATION=5
VAD_ENABLED=true
VAD_THRESHOLD=0.01

# Memory Configuration
MAX_MEMORY_ENTRIES=1000

# Wake Word Configuration
WAKE_WORD_ENABLED=true
WAKE_WORD=hey-mira
WAKE_WORD_SENSITIVITY=0.5
```

### Getting API Keys

- **OpenWeatherMap**: Sign up at [openweathermap.org](https://openweathermap.org/api)
- **Tavily** (optional): Sign up at [tavily.com](https://tavily.com)

## 🎯 Usage

1. **Start Ollama server:**
```bash
ollama serve
```

2. **Run Mira-AI:**
```bash
python main.py
```

3. **With Wake Word (Recommended):**
   - Say **"Hey Mira"** to activate the assistant
   - Then speak your command
   - The assistant will process your request automatically

4. **Without Wake Word:**
   - The assistant will continuously listen
   - Speak your command directly
   - Disable wake word: Set `WAKE_WORD_ENABLED=false` in `.env`

5. **Press Ctrl+C** to exit gracefully

## 📁 Project Structure

```
Mira-AI/
├── main.py                 # Main entry point
├── modules/
│   ├── brain.py            # AI logic with emotion detection
│   ├── speech_to_text.py   # Whisper transcription (with caching)
│   ├── text_to_speech.py   # Edge TTS with emotion support
│   ├── memory_manager.py   # Conversation memory management
│   └── tools.py            # Custom tools (weather, time, etc.)
├── utils/
│   ├── mic_record.py       # Audio recording with VAD
│   └── config.py           # Configuration management
├── data/
│   ├── config.json         # Legacy config (backwards compatible)
│   └── memory.json         # Conversation history
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠️ Tools

Mira-AI comes with several built-in tools:

- **Weather** - Get current weather for any city
- **Time** - Get current time
- **Web Search** - DuckDuckGo search integration
- **Custom Tools** - Easy to add your own in `modules/tools.py`

## 🎙️ Wake Word Detection

Mira-AI supports hands-free activation using wake word detection:

### Two Modes:

1. **Porcupine Mode (Recommended)** - Real-time audio wake word detection
   - Install: `pip install pvporcupine`
   - Works completely offline
   - Low latency (< 50ms detection)
   - Continuously listens in background

2. **Keyword Mode (Fallback)** - Text-based wake word detection
   - No additional installation needed
   - Transcribes audio first, then checks for wake word
   - Slightly slower but works everywhere

### Configuration:

- **Enable/Disable**: `WAKE_WORD_ENABLED=true/false` in `.env`
- **Wake Word**: `WAKE_WORD=hey-mira` (Porcupine) or custom keyword
- **Sensitivity**: `WAKE_WORD_SENSITIVITY=0.5` (0.0-1.0, higher = more sensitive)

### Usage:

- **With Porcupine**: Say "Hey Mira" → Assistant activates → Speak your command
- **Without Porcupine**: Say "Hey Mira, what's the weather?" → Assistant processes after transcription

## 🔧 Advanced Features

### Voice Activity Detection (VAD)

VAD automatically stops recording when it detects silence, making conversations more natural. Disable it by setting `VAD_ENABLED=false` in `.env` or passing `use_vad=False` to `record_audio()`.

### Model Caching

Whisper model is cached after first load to improve performance. The model stays in memory for faster subsequent transcriptions.

### Memory Management

- Conversations are automatically saved to `data/memory.json`
- Memory file is automatically cleaned up when it gets too large
- Keeps the most recent 500 entries by default

### Emotion Detection

The assistant detects emotions (joy, sadness, anger, fear, surprise) and adapts:
- **Response tone** - Adjusts language model prompts
- **Voice modulation** - Changes TTS voice and speed based on emotion

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check that the model is pulled: `ollama list`

### "Model requires too much memory"
- Use a smaller model: `qwen2.5:1.5b` or `qwen2.5:3b`
- Update `OLLAMA_MODEL` in `.env`

### Installation/Build issues
- **"Failed to build webrtcvad"**: This is optional! VAD works without it using amplitude detection. The package is commented out in requirements.txt.

- **"Failed to build torch"**: Install PyTorch separately:
  ```bash
  # For CPU only
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
  
  # For CUDA (if you have NVIDIA GPU)
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

- **"Microsoft Visual C++ required"**: 
  - Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  - Or skip packages that require it (webrtcvad is optional)

- **Install individual packages**: If specific packages fail, install them one by one:
  ```bash
  pip install torch openai-whisper
  pip install transformers langchain langchain-community langchain-ollama
  pip install sounddevice soundfile scipy numpy pygame
  pip install edge-tts python-dotenv requests ddgs ollama
  ```

### Audio issues
- Check microphone permissions
- Try adjusting `VAD_THRESHOLD` in `.env`
- Disable VAD if having issues: `use_vad=False`

### Transcription errors
- Speak clearly and close to the microphone
- Check that Whisper model downloaded correctly
- Verify audio file is being created

## 📝 Logging

Logs are saved to `mira_ai.log` and also printed to console. Check the log file for detailed error information.

## 🔒 Security

- API keys are stored in `.env` file (not committed to git)
- Never commit `.env` file to version control
- Memory file may contain sensitive conversation data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- Edge TTS for high-quality text-to-speech
- Ollama for local LLM inference
- LangChain for agent framework
- Hugging Face for emotion detection model

## 🚧 Future Improvements

See [ROADMAP.md](ROADMAP.md) for detailed upgrade suggestions and implementation roadmap.

**Quick highlights:**
- [ ] Wake word detection ("Hey Mira")
- [ ] GUI/web interface
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Vector memory for semantic search
- [ ] Conversation export & management
- [ ] Plugin system for custom tools
- [ ] Voice cloning & personality customization

