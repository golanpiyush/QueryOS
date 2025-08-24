<p align="center">
  <img src="assets/queryos.ico" alt="QueryOS Logo" width="128" height="128">
</p>

# QueryOS - AI Desktop Search Assistant 

[![GitHub Stars](https://img.shields.io/github/stars/golanpiyush/QueryOS?style=for-the-badge&logo=github)](https://github.com/golanpiyush/QueryOS/stargazers)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/GPL-3.0)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078d4?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows/)
[![Release](https://img.shields.io/badge/Release-v1.0.0-green?style=for-the-badge)](https://github.com/golanpiyush/QueryOS/releases)

> 🔍 **An intelligent AI-powered desktop search assistant that understands natural language queries and searches across all your Windows drives with voice support.**

## ✨ Features

### 🧠 AI-Powered Search
- **Natural Language Processing**: Use OpenRouter AI to parse complex search queries
- **Smart Query Understanding**: "Find me that Python file with 'main' in the name from last week"
- **Context-Aware Results**: Prioritizes recent files and common locations

### 🎤 Voice Integration
- **Voice Commands**: Search using your voice with speech recognition
- **Text-to-Speech**: Hear search results and confirmations
- **Hands-Free Operation**: Perfect for accessibility and multitasking

### 💾 Cross-Drive Search
- **All Windows Drives**: Automatically detects and searches C:, D:, E:, etc.
- **Smart Filtering**: Skips system directories for faster results
- **File Type Recognition**: Supports code, documents, media, archives, and more

### 🎯 Intelligent Results
- **Relevance Scoring**: Best matches appear first
- **File Preview**: View content with syntax highlighting
- **Quick Actions**: Open files or show in Windows Explorer
- **Priority Locations**: Desktop, Documents, Downloads get preference

### 🔧 Flexible Interface
- **Debug Mode**: Full detailed information and search progress
- **Minimal Mode**: Clean interface with essential options only
- **Voice/Text Toggle**: Switch between input methods seamlessly

## 📋 Requirements

- **Operating System**: Windows 7/8/10/11
- **Python**: 3.7 or higher
- **Dependencies**: See [requirements.txt](requirements.txt)

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/golanpiyush/QueryOS.git
   cd QueryOS
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   - Edit `config/settings.py`
   - Add your OpenRouter API key (free tier available)

4. **Run QueryOS**:
   ```bash
   python bin/queryos.py
   ```

### First Run

1. QueryOS will initialize and detect available drives
2. Try a search: `"find me config.json"`
3. Use voice mode: type `voice` and speak your query
4. Toggle debug mode in `config/settings.py`

## 🎮 Usage Examples

### Text Commands
```
🔍 find me apimain.py
🔍 search for Excel files with budget
🔍 in D drive find config.json and open it
🔍 look for Python files from this week
🔍 find documents about project planning
```

### Voice Commands
1. Type `voice` to activate voice mode
2. Speak naturally: *"Find me that JavaScript file I was working on yesterday"*
3. QueryOS will process and search automatically

### Special Commands
- `drives` - Show available drives
- `voice` - Switch to voice input
- `text` - Switch to text input
- `help` - Show command guide
- `quit` - Exit application

## ⚙️ Configuration

### Debug Mode Control
Edit `config/settings.py`:

```python
# Full detailed interface
DEBUG_MODE = True

# Minimal clean interface  
DEBUG_MODE = False
```

### API Configuration
```python
OPENROUTER_API_KEY = "your-api-key-here"
AI_MODEL = "nousresearch/deephermes-3-llama-3-8b-preview:free"
```

### Search Customization
```python
PRIORITY_PATHS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    # Add your preferred locations
]
```

## 📁 Project Structure

```
QueryOS/
├── bin/
│   └── queryos.py              # Main executable
├── classes/
│   └── ai_desktop_search.py    # Core application logic
├── utils/
│   ├── voice_handler.py        # Voice recognition & TTS
│   ├── file_searcher.py        # File searching algorithms
│   └── query_parser.py         # AI query parsing
├── user/
│   └── user_interface.py       # UI display logic
├── inputs/
│   └── input_handler.py        # Input processing
├── errors/
│   └── error_handler.py        # Error management
├── config/
│   └── settings.py             # Configuration settings
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Advanced Features

### File Type Support
- **Code**: `.py`, `.js`, `.html`, `.css`, `.java`, `.cpp`, `.go`, `.rs`
- **Documents**: `.txt`, `.pdf`, `.docx`, `.doc`, `.rtf`
- **Data**: `.xlsx`, `.csv`, `.json`, `.xml`, `.sql`
- **Media**: `.mp4`, `.mp3`, `.jpg`, `.png`, `.gif`
- **Archives**: `.zip`, `.rar`, `.7z`, `.tar`

### Smart Search Features
- **Partial Matching**: Find files with incomplete names
- **Date Filtering**: Search by modification date
- **Size Optimization**: Prioritize appropriately-sized files
- **Location Scoring**: Boost results from important folders

### Voice Features
- **Ambient Noise Adjustment**: Automatic microphone calibration
- **Timeout Handling**: Smart listening duration
- **Error Recovery**: Graceful fallback to text mode
- **TTS Customization**: Adjustable speech rate and voice

## 🛠️ Development

### Building Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=queryos.ico bin/queryos.py
```

### Running Tests
```bash
python -m pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 API Keys

QueryOS uses OpenRouter for AI query parsing:

1. **Get Free API Key**: Visit [OpenRouter.ai](https://openrouter.ai)
2. **Free Tier**: 200+ requests per day at no cost
3. **Privacy**: No data stored, requests are processed and discarded

## 🐛 Troubleshooting

### Voice Recognition Issues
- **Install audio dependencies**: `pip install pyaudio`
- **Check microphone**: Ensure default recording device works
- **Try different voice models**: Modify `config/settings.py`

### Permission Errors
- **Run as Administrator**: For accessing protected directories
- **Antivirus Software**: May block file system scanning
- **Network Drives**: May require additional permissions

### Search Performance
- **Exclude Large Directories**: Modify search paths in config
- **SSD vs HDD**: Search speed varies by storage type
- **Background Activity**: Other programs may slow searches

## 📜 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **OpenRouter**: AI query parsing service
- **SpeechRecognition**: Python speech recognition library
- **pyttsx3**: Text-to-speech conversion
- **OpenAI**: AI model architecture inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/golanpiyush/QueryOS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/golanpiyush/QueryOS/discussions)
- **Email**: golanpiyush32@gmail.com

---

**Made with ❤️ for Windows power users who love intelligent search**

⭐ **Star this repo if QueryOS helps you find files faster!**