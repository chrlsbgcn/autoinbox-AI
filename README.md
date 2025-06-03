# AutoInbox AI

An AI-powered email automation assistant that helps manage and respond to emails efficiently using local AI models. This tool leverages the power of Ollama and Gmail API to provide intelligent email management solutions.

## 🌟 Features

- 📥 **Gmail Integration**
  - Secure OAuth 2.0 authentication
  - Real-time email monitoring
  - Automated email processing

- 📊 **Smart Email Categorization**
  - Urgent: Requires immediate attention
  - Important: Needs response within 24 hours
  - Low Priority: Can be handled later
  - Custom categories based on user preferences

- ✍️ **AI-Powered Draft Replies**
  - Context-aware response generation
  - Multiple response options
  - Customizable tone and style
  - Support for multiple languages

- 📝 **Daily Email Digest**
  - Summary of important emails
  - Priority-based organization
  - Action items and follow-ups
  - Customizable digest format

- 📈 **Comprehensive Logging**
  - Detailed activity tracking
  - Error monitoring
  - Performance metrics
  - Debug information

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Gmail account
- Google Cloud Platform account
- Ollama installed locally

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/autoinbox-ai.git
cd autoinbox-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as application type
   - Download credentials and save as `credentials.json` in the project root

### Ollama Setup

1. Install Ollama:
   - Follow instructions at [ollama.ai](https://ollama.ai)
   - Download and install for your operating system

2. Pull the required model:
```bash
ollama pull deepseek-r1:1.5b
```

## 📁 Project Structure

```
autoinbox-ai/
├── src/
│   ├── ai/
│   │   └── (AI model integration and processing)
│   ├── email/
│   │   └── (Gmail integration and email handling)
│   └── scheduler/
│       └── (Task scheduling and automation)
├── config/
│   └── (Configuration files)
├── data/
│   └── (Data storage and processing)
├── tests/
│   └── (Test files)
├── main.py
├── requirements.txt
├── __init__.py
└── README.md
```

## 💻 Usage

1. Start the application:
```bash
python src/main.py
```

2. First-time setup:
   - Follow the OAuth authentication flow
   - Grant necessary permissions
   - Configure your preferences

3. Monitor your inbox:
   - The system will automatically process incoming emails
   - Check the logs for detailed information
   - Review and send AI-generated responses

## 🔧 Configuration

The application can be configured through the `.env` file:

```env
GMAIL_CREDENTIALS_FILE=credentials.json
OLLAMA_MODEL=deepseek-r1:1.5b
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for providing the AI models
- [Google Gmail API](https://developers.google.com/gmail/api) for email integration
- All contributors who have helped shape this project

## 📞 Support

For support, please:
1. Check the [documentation](docs/)
2. Open an issue in the GitHub repository
3. Contact the maintainers

---

Made with ❤️ by [Your Name]