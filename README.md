# Virtual Classroom Assistant

An intelligent virtual classroom assistant powered by OpenAI's GPT, featuring Google OAuth authentication and an intuitive chat interface.

## 🌟 Features

- **Secure Authentication**
  - Google OAuth 2.0 integration
  - Session management
  - Secure user data handling

- **Interactive Learning Interface**
  - Real-time chat with AI assistant
  - Dark/Light mode toggle
  - Responsive design for all devices

- **Educational Tools**
  - Multiple subject areas:
    - Mathematics
    - Science
    - History
    - Literature
    - Computer Science
  - Interactive quizzes
  - Topic-based learning paths

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Flask
- OpenAI API key
- Google OAuth credentials

### Installation

1. Clone the repository
```bash
git clone https://github.com/pioneertrail/Virtual-Classroom.git
cd Virtual-Classroom
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env` file
```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FLASK_SECRET_KEY=your_flask_secret_key
```

5. Run the application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Authentication**: Google OAuth 2.0
- **AI Integration**: OpenAI GPT-3.5
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Session Management**: Flask-Session

## 📚 Usage

1. Log in using your Google account
2. Access the chat interface
3. Use commands:
   - `!help` - Show available commands
   - `!topics` - List learning topics
   - `!quiz` - Start an interactive quiz

## 🔒 Security

- OAuth 2.0 authentication
- Secure session management
- Environment variable protection
- Input validation and sanitization

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT integration
- Google for OAuth services
- Flask and its community for the excellent web framework