import os
from dotenv import load_dotenv
import openai
from datetime import datetime, timedelta
from student_profile import StudentProfile
from educational_activities import EducationalActivities
from user_auth import UserAuth

class VirtualClassroom:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.api_key)
        self.conversation_history = []
        self.active_users = {}
        self.system_prompt = """You are a friendly and educational chat moderator for a kids' virtual classroom. Your role is to:
        1. Keep the conversation fun but educational
        2. Adapt your teaching style to each student's learning style
        3. Encourage positive interaction between students
        4. Use humor to make learning fun
        5. Celebrate achievements and progress
        6. Help students learn through their interests
        """
        self.activities = EducationalActivities()
        self.current_quiz_theme = None
        self.auth = UserAuth()
    
    def get_or_create_student(self, username):
        if username not in self.active_users:
            self.active_users[username] = StudentProfile(username, username)
        return self.active_users[username]

    def moderate_message(self, username, message):
        try:
            # Use logged-in username if available
            if self.auth.is_logged_in():
                username = self.auth.current_user
                
            student = self.get_or_create_student(username)

            # Check for special commands
            if message.lower().startswith('!'):
                return self.handle_command(message.lower(), username)
            
            # Analyze message for learning style and interests
            analysis_prompt = f"""Analyze this message for:
            1. Learning style indicators (visual, auditory, kinesthetic)
            2. Interests or topics
            3. Engagement level (high, medium, low)
            
            Message: {message}
            
            Format: STYLE|INTERESTS|ENGAGEMENT"""
            
            # Updated API call format
            analysis_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.7,
                max_tokens=100
            )
            analysis = analysis_response.choices[0].message.content
            
            style, interests, engagement = analysis.split('|')
            
            # Update student profile
            student.update_learning_style(style.lower(), None, 0.7)
            for interest in interests.split(','):
                student.add_interest(interest.strip())
            
            # Updated API call format
            chat_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Student {username} (learning style: {style}) says: {message}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            response = chat_response.choices[0].message.content
            
            # Record interaction
            student.add_interaction(message, response, engagement.lower())
            
            return response

        except Exception as e:
            print(f"Error handling message: \n{str(e)}")  # Added for debugging
            return "I apologize, but I encountered an error processing your message. Please try again."

    def handle_command(self, command, username):
        commands = {
            '!profile': lambda: self.show_profile(username),
            '!help': self.show_help,
            '!theme': lambda: self.change_theme(command),
            '!quiz': lambda: self.start_quiz(username, command),
            '!activity': lambda: self.start_activity(username),
            '!answer': lambda: self.check_answer(username, command),
            '!register': lambda: self.register_user(username, command),
            '!login': lambda: self.login_user(username, command),
            '!logout': lambda: self.logout_user(username),
            '!forgot': lambda: self.forgot_password(username, command),
            '!verify': lambda: self.verify_code(username, command),
            '!reset': lambda: self.reset_password(username, command)
        }
        
        parts = command.split(maxsplit=1)
        command_name = parts[0]
            
        if command_name in commands:
            return commands[command_name]()
        return "Hmm, I don't know that command! Try !help for a list of commands! 🤔"

    def show_profile(self, username):
        student = self.get_or_create_student(username)
        profile = student.get_profile_summary()
        return f"""📚 {username}'s Learning Profile 📚
Learning Style: {profile['learning_style']['primary']}
Interests: {', '.join(profile['interests'])}
Progress Level: {profile['progress']['language']['level']}"""

    def show_help(self):
        return """🌟 Available Commands 🌟
!register [username] [password] [your name] [email] - Create a new account
!login [username] [password] - Log in to your account
!logout - Log out of your account
!forgot [username] - Request password recovery
!verify [username] [code] - Verify recovery code
!reset [username] [new_password] - Reset password
!profile - See your learning profile
!theme - Change the learning theme
!quiz - Take a themed quiz
!activity - Get a fun learning activity
!answer - Answer a quiz question
!help - Show this help message"""

    def start_activity(self, username):
        student = self.get_or_create_student(username)
        interests = student.profile['interests']
        
        if not interests:
            return "Let's learn about something you're interested in! What do you like?"
            
        # Use student's first interest as theme
        theme = interests[0]
        return self.activities.get_activity(theme, student)

    def check_answer(self, username, command):
        parts = command.split()
        if len(parts) < 2:
            return "Please provide an answer! Example: !answer A"
            
        answer = parts[1]
        return self.activities.check_answer(self.current_quiz_theme, answer)

    def register_user(self, username, command):
        if self.auth.is_logged_in():
            return "You're already logged in! Use !logout first."
            
        parts = command.split()
        if len(parts) < 4:
            return "Usage: !register [username] [password] [your name] [email]"
            
        username = parts[1]
        password = parts[2]
        name = " ".join(parts[3:])
        email = parts[4]
        
        success, message = self.auth.register(username, password, name, email)
        return message

    def login_user(self, username, command):
        if self.auth.is_logged_in():
            return "You're already logged in! Use !logout first."
            
        parts = command.split()
        if len(parts) < 3:
            return "Usage: !login [username] [password]"
            
        username = parts[1]
        password = parts[2]
        
        success, message = self.auth.login(username, password)
        if success:
            # Load or create student profile for logged-in user
            self.get_or_create_student(username)
        return message

    def logout_user(self, username):
        return self.auth.logout()

    def forgot_password(self, username, command):
        parts = command.split()
        if len(parts) < 2:
            return "Usage: !forgot [username]"
            
        username = parts[1]
        success, message = self.auth.initiate_password_recovery(username)
        return message

    def verify_code(self, username, command):
        parts = command.split()
        if len(parts) < 3:
            return "Usage: !verify [username] [code]"
            
        username = parts[1]
        code = parts[2]
        success, message = self.auth.verify_recovery_code(username, code)
        return message

    def reset_password(self, username, command):
        parts = command.split()
        if len(parts) < 3:
            return "Usage: !reset [username] [new_password]"
            
        username = parts[1]
        new_password = parts[2]
        success, message = self.auth.reset_password(username, new_password)
        return message

def main():
    classroom = VirtualClassroom()
    
    print("Welcome to the Virtual Classroom!")
    print("Type !help for available commands")
    print("Type 'quit' to exit")
    
    while True:
        if classroom.auth.is_logged_in():
            user = classroom.auth.get_current_user()
            prompt = f"{user['name']}, what would you like to learn about? "
        else:
            prompt = "\nWhat's your name? "
            
        user_input = input(prompt)
        if user_input.lower() == 'quit':
            if classroom.auth.is_logged_in():
                print(classroom.auth.logout())
            print("See you next time! 👋")
            break
            
        if user_input.startswith('!'):
            response = classroom.handle_command(user_input, user_input)
        else:
            response = classroom.moderate_message(user_input, user_input)
            
        print(f"\nTeacher: {response}")

if __name__ == "__main__":
    main() 