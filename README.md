# 🎙️ Claude Voice Assistant

AI-powered voice interface for real-time conversations with Claude

## 🚀 Features

- **Voice Recognition**: Real-time speech-to-text using advanced AI
- **Natural Conversation**: Seamless interaction with Claude AI
- **Text-to-Speech**: Natural voice synthesis for responses
- **Multi-Language Support**: Works with multiple languages
- **Real-time Processing**: Instant response and interaction

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/zahiliberman/claude-voice-assistant.git
cd claude-voice-assistant

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 🔧 Configuration

Create a `.env` file with your API keys:

```env
CLAUDE_API_KEY=your_claude_api_key
VOICE_API_KEY=your_voice_service_key
```

## 🎯 Usage

### Python Interface

```bash
python voice-interface.py
```

### Web Interface

Visit: [https://claude-voice.vercel.app](https://claude-voice.vercel.app)

## 🏗️ Architecture

```
claude-voice-assistant/
├── voice-interface.py    # Main Python interface
├── index.html            # Web UI
├── app.js               # JavaScript frontend
├── requirements.txt     # Python dependencies
├── package.json        # Node.js dependencies
└── README.md           # Documentation
```

## 🛠️ Technologies

- **Python 3.9+**: Core backend
- **Claude API**: AI conversation engine
- **Speech Recognition**: Voice-to-text processing
- **Text-to-Speech**: Voice synthesis
- **Vercel**: Web deployment
- **GitHub Actions**: CI/CD

## 📱 Features in Development

- [ ] Mobile app support
- [ ] Voice customization
- [ ] Conversation history
- [ ] Multi-user support
- [ ] Custom voice commands
- [ ] Integration with smart home devices

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**Tzachi Liberman**
- GitHub: [@zahiliberman](https://github.com/zahiliberman)

## 🙏 Acknowledgments

- Built with Claude Code
- Powered by Anthropic Claude AI

---

🤖 Generated with [Claude Code](https://claude.ai/code)