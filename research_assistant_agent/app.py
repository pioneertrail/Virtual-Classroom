import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
import openai
from flask_oauthlib.client import OAuth
from datetime import timedelta

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Allow HTTP for local development only!
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Get the directory containing app.py
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'

# Load environment variables
load_dotenv(ENV_FILE, override=True)

# OAuth 2.0 configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Debug logging
logger.debug(f"Current working directory: {os.getcwd()}")
logger.debug(f"Environment variables loaded: {os.environ.get('GOOGLE_CLIENT_ID')}")
logger.debug(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
logger.debug(f"GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET}")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///virtual_classroom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    profile_picture = db.Column(db.String(200))

# After loading environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
logger.debug(f"OpenAI API key loaded: {'OPENAI_API_KEY' in os.environ}")

class VirtualClassroom:
    def __init__(self):
        self.client = openai.OpenAI()  # Create client instance
        self.system_prompt = """You are a helpful virtual classroom assistant. You help students learn 
        about various topics and can provide quizzes and educational activities. When using commands:
        !help - List available commands and features
        !topics - Show available learning topics
        !quiz - Start a quiz on the current or selected topic"""
        
    def handle_message(self, message, history):
        try:
            if message.startswith('!'):
                return self.handle_command(message)
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add message history
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Updated API call format
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error handling message: {str(e)}")
            return "I apologize, but I encountered an error processing your message. Please try again."
    
    def handle_command(self, command):
        if command == '!help':
            return """Available commands:
            !help - Show this help message
            !topics - Show available learning topics
            !quiz - Start a quiz on the current topic"""
            
        elif command == '!topics':
            return """Available topics:
            1. Mathematics
            2. Science
            3. History
            4. Literature
            5. Computer Science
            Choose a topic by saying "Let's learn about [topic]" """
            
        elif command == '!quiz':
            return """Let's start a quiz! First, which topic would you like to be quizzed on?
            - Mathematics
            - Science
            - History
            - Literature
            - Computer Science"""
            
        return f"Unknown command: {command}"

# Create an instance of VirtualClassroom
virtual_classroom = VirtualClassroom()

# Initialize OAuth client
oauth = OAuth(app)

# Near the top of your file
def get_host_url():
    # Get the host from the request
    host = request.headers.get('Host', '10.1.10.90:5000')
    return f'http://{host}'

# Use localhost for OAuth
NGROK_URL = 'https://6b8d-67-166-113-95.ngrok-free.app'

# Make sure session cookie settings are permissive
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SERVER_NAME'] = None

# First define the remote app
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_CLIENT_ID'),
    consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'email profile',
        'access_type': 'offline'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth'
)

# Then define the tokengetter
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/')
def index():
    if 'google_token' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    callback_url = f'{NGROK_URL}/callback'
    print(f"Attempting login with callback URL: {callback_url}")  # Debug line
    return google.authorize(callback=callback_url)

@app.route('/callback')
def callback():
    try:
        resp = google.authorized_response()
        if resp is None or resp.get('access_token') is None:
            return 'Access denied: reason={} error={}'.format(
                request.args.get('error_reason', 'unknown'),
                request.args.get('error_description', 'unknown')
            )
        
        session['google_token'] = (resp['access_token'], '')
        
        # Get user info
        me = google.get('userinfo')
        if me.status != 200:
            return 'Failed to get user info'
            
        user_data = me.data
        session['user_email'] = user_data.get('email')
        session['user_name'] = user_data.get('name')
        session['picture'] = user_data.get('picture')
        
        print(f"Login successful for: {session.get('user_email')}")
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f"OAuth error: {str(e)}")
        return f"Authentication error: {str(e)}", 400

@app.route('/dashboard')
def dashboard():
    if 'google_token' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html',
        user_name=session.get('user_name'),
        user_email=session.get('user_email'),
        picture=session.get('picture')
    )

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('picture', None)
    return redirect(url_for('index'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    try:
        data = request.get_json()
        user_message = data.get('message')
        
        logger.debug(f"Received message: {user_message}")
        logger.debug(f"User info: {session['user']}")
        
        # Use the existing virtual classroom logic
        response = virtual_classroom.process_message(
            user_message,
            user_name=session['user']['name'],
            user_email=session['user']['email']
        )
        
        return jsonify({'response': response})
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    if 'google_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        message = data.get('message', '')
        history = data.get('history', [])
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
            
        response = virtual_classroom.handle_message(message, history)
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/test-urls')
def test_urls():
    return {
        'ngrok_url': NGROK_URL,
        'callback_url': f'{NGROK_URL}/callback',
        'current_host': request.host
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Try port 5000 instead
    app.run(host='0.0.0.0', port=5000, debug=True)