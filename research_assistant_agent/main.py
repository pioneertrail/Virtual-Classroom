import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta

class ChatModerator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []
        self.active_users = {}  # Track user status and timeout info
        self.warning_counts = {}  # Track warnings per user
        self.system_prompt = """You are a sassy but responsible chat moderator for a kids' chatroom. Your role is to:
        1. Keep the conversation fun but appropriate
        2. Use playful language and occasional sass, but always stay kid-friendly
        3. Gently redirect inappropriate topics
        4. Encourage positive interaction between kids
        5. Use humor to defuse tensions
        6. Jump in with fun topics if conversation gets slow
        7. Celebrate kind behavior
        
        Moderation levels:
        - APPROVED: Message is fine
        - WARNING: Minor issue, needs gentle correction
        - TIMEOUT: Serious issue, user needs a break
        """
        self.user_points = {}  # Track user points
        self.achievements = {
            'friendly': '🤝 Friend Maker',
            'helpful': '🌟 Super Helper',
            'creative': '🎨 Creative Mind',
            'wordmaster': '📚 Word Master',
            'peacemaker': '🕊️ Peace Maker'
        }
        self.user_achievements = {}  # Track user achievements
        self.current_theme = None
        self.themes = {
            'space': '🚀 Space Explorers',
            'animals': '🦁 Animal Kingdom',
            'science': '🔬 Mad Scientists',
            'books': '📚 Book Club',
            'art': '🎨 Creative Corner'
        }
        self.current_quiz = None
        self.quiz_scores = {}
        self.story_active = False
        self.story_parts = []
        self.story_theme = None
        self.story_contributors = set()
        self.max_story_parts = 10
    
    def check_timeout(self, username):
        if username in self.active_users:
            timeout_until = self.active_users[username].get('timeout_until')
            if timeout_until and datetime.now() < timeout_until:
                remaining = (timeout_until - datetime.now()).seconds
                return f"Whoopsie! You're in a timeout for {remaining} more seconds. Take a breather! 😌"
        return None

    def add_warning(self, username):
        if username not in self.warning_counts:
            self.warning_counts[username] = 0
        self.warning_counts[username] += 1
        
        if self.warning_counts[username] >= 3:
            self.timeout_user(username)
            return "Three strikes! Time for a 30-second timeout to cool off! 🧊"
        return f"Warning {self.warning_counts[username]}/3! Keep it friendly! 🌟"

    def timeout_user(self, username):
        self.active_users[username] = {
            'timeout_until': datetime.now() + timedelta(seconds=30)
        }
        self.warning_counts[username] = 0

    def add_points(self, username, points, reason=""):
        if username not in self.user_points:
            self.user_points[username] = 0
        self.user_points[username] += points
        
        message = f"+{points} points"
        if reason:
            message += f" ({reason})"
        
        # Check for achievements
        self.check_achievements(username)
        
        return message

    def check_achievements(self, username):
        if username not in self.user_achievements:
            self.user_achievements[username] = set()
        
        points = self.user_points.get(username, 0)
        new_achievements = []
        
        # Point-based achievements
        if points >= 50 and 'friendly' not in self.user_achievements[username]:
            self.user_achievements[username].add('friendly')
            new_achievements.append(self.achievements['friendly'])
        
        if points >= 100 and 'helpful' not in self.user_achievements[username]:
            self.user_achievements[username].add('helpful')
            new_achievements.append(self.achievements['helpful'])
        
        return new_achievements

    def moderate_message(self, username, message):
        try:
            # Check if user is in timeout
            timeout_message = self.check_timeout(username)
            if timeout_message:
                return timeout_message

            # Handle special commands
            if message.lower().startswith('!'):
                return self.handle_command(message.lower(), username)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Moderate this message from {username}: {message}\n\nRespond with exactly one of: APPROVED, WARNING, or TIMEOUT, followed by your response after a | character."}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the moderation response
            full_response = response.choices[0].message.content
            moderation_type, moderator_message = full_response.split('|', 1)
            moderation_type = moderation_type.strip()
            
            # Handle different moderation types
            if moderation_type == "WARNING":
                warning_message = self.add_warning(username)
                return f"{moderator_message.strip()} {warning_message}"
            elif moderation_type == "TIMEOUT":
                self.timeout_user(username)
                return f"{moderator_message.strip()} (30-second timeout)"
            
            # Store approved messages in history
            self.conversation_history.append({"role": "user", "content": f"{username}: {message}"})
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            if moderation_type == "APPROVED":
                # Add theme-based responses
                if self.current_theme and not message.startswith('!'):
                    theme_response = self.get_theme_response(message)
                    if theme_response:
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": f"Theme Helper: {theme_response}"
                        })
                
                # Award points for positive behaviors
                points_earned = 0
                reason = []
                
                # Point awards for different behaviors
                if len(message) > 20:  # Thoughtful messages
                    points_earned += 2
                    reason.append("thoughtful message")
                
                if any(word in message.lower() for word in ['thank', 'thanks', 'please']):
                    points_earned += 1
                    reason.append("being polite")
                
                if points_earned > 0:
                    points_message = self.add_points(username, points_earned, ", ".join(reason))
                    
                    # Check for new achievements
                    new_achievements = self.check_achievements(username)
                    if new_achievements:
                        points_message += f"\n🎉 New achievement(s): {' '.join(new_achievements)}"
                    
                    self.conversation_history.append({
                        "role": "system",
                        "content": points_message
                    })

                # Add theme-based bonus points
                if self.current_theme:
                    theme_words = {
                        'space': ['planet', 'star', 'galaxy', 'astronaut', 'rocket'],
                        'animals': ['habitat', 'species', 'wildlife', 'nature', 'pet'],
                        'science': ['experiment', 'discover', 'research', 'learn', 'study'],
                        'books': ['story', 'character', 'author', 'read', 'chapter'],
                        'art': ['create', 'draw', 'color', 'design', 'paint']
                    }
                    
                    if any(word in message.lower() for word in theme_words.get(self.current_theme, [])):
                        points_message = self.add_points(username, 2, f"using {self.current_theme} theme words")
                        self.conversation_history.append({
                            "role": "system",
                            "content": points_message
                        })

            return "APPROVED"

        except Exception as e:
            return f"Oopsie! Something went wrong: {str(e)}"

    def handle_command(self, command, username):
        commands = {
            '!topic': self.suggest_topic,
            '!game': self.suggest_game,
            '!rules': self.show_rules,
            '!help': self.show_help,
            '!chat': lambda: self.chat_with_mod(username, command),
            '!points': lambda: self.show_points(username),
            '!achievements': lambda: self.show_achievements(username),
            '!leaderboard': self.show_leaderboard,
            '!theme': lambda: self.change_theme(command),
            '!quiz': lambda: self.start_quiz(username, command),
            '!answer': lambda: self.check_answer(username, command),
            '!story': lambda: self.start_story(username, command),
            '!add': lambda: self.add_to_story(username, command),
            '!endstory': lambda: self.end_story(username)
        }
        
        command_parts = command.split(maxsplit=1)
        command_name = command_parts[0]
        
        if command_name == '!chat':
            message = command_parts[1] if len(command_parts) > 1 else ""
            return self.chat_with_mod(username, message)
            
        if command_name in commands:
            return commands[command_name]()
        return "Hmm, I don't know that command! Try !help for a list of commands! 🤔"

    def suggest_topic(self):
        topics_prompt = "Suggest a fun, kid-friendly conversation topic with a playful introduction."
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": topics_prompt}],
                temperature=0.9,
                max_tokens=100
            )
            return f"🎯 {response.choices[0].message.content}"
        except Exception:
            return "Hmm, my topic generator is taking a nap! Try again in a minute! 😴"

    def suggest_game(self):
        games_prompt = "Suggest a fun, text-based word game that kids can play in a chat room. Include brief rules."
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": games_prompt}],
                temperature=0.9,
                max_tokens=150
            )
            return f"🎮 {response.choices[0].message.content}"
        except Exception:
            return "Oops, my game ideas are playing hide and seek! Try again soon! 🙈"

    def show_rules(self):
        return """📜 Chat Rules 📜
1. Be kind to everyone
2. No mean words or bullying
3. Keep it fun and friendly
4. Listen to the moderator
5. Three warnings = timeout!"""

    def show_help(self):
        return """🌟 Available Commands 🌟
!topic - Get a fun topic to discuss
!game - Suggest a word game to play
!rules - Show the chat rules
!chat [message] - Have a direct chat with me!
!react [number] [emoji] - React to a recent message
!wordchain - Start a word chain game
!points - See your points and achievements
!achievements - See available achievements
!leaderboard - See top chatters
!theme - See/change chat themes
!quiz - Take a themed quiz
!answer [A/B/C] - Answer quiz question
!story [theme] - Start a group story
!add [text] - Add to the current story
!endstory - Finish the current story
!help - Show this help message"""

    def chat_with_mod(self, username, message):
        if not message:
            return "What's on your mind? Try '!chat hello' to start a conversation! 💭"
        
        try:
            chat_prompt = f"""You are a sassy but friendly chat moderator talking directly to {username}.
            Previous context: {self.conversation_history[-3:] if self.conversation_history else 'No previous context'}
            
            Respond in your sassy moderator personality, but be extra engaging since the user is talking to you directly.
            Keep responses kid-friendly and fun!"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": chat_prompt},
                    {"role": "user", "content": f"{username} says: {message}"}
                ],
                temperature=0.8,
                max_tokens=150
            )
            
            mod_response = response.choices[0].message.content
            self.conversation_history.append({
                "role": "user", 
                "content": f"{username} chatted with mod: {message}"
            })
            self.conversation_history.append({
                "role": "assistant", 
                "content": f"Mod response to {username}: {mod_response}"
            })
            
            return mod_response
            
        except Exception as e:
            return "Oops! My sass processor is glitching! Try again in a sec! 🤪"

    def check_name(self, username):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are checking if a username is appropriate for a kids' chat room. Respond with exactly 'APPROVED' or 'REJECTED' followed by a | and then a kid-friendly explanation if rejected."},
                    {"role": "user", "content": f"Is this username appropriate: {username}"}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            result = response.choices[0].message.content
            status, *message = result.split('|')
            
            if status.strip() == 'APPROVED':
                return True, None
            else:
                return False, message[0].strip()
        except Exception as e:
            return False, "Oops! Having trouble with that name. Try another one! 🎯"

    def show_points(self, username):
        points = self.user_points.get(username, 0)
        achievements = self.user_achievements.get(username, set())
        return f"""🏆 {username}'s Profile:
Points: {points}
Achievements: {' '.join(self.achievements[a] for a in achievements)}"""

    def show_leaderboard(self):
        if not self.user_points:
            return "No points earned yet! Start chatting to earn some! 🎯"
        
        sorted_users = sorted(self.user_points.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_users[:5]
        
        leaderboard = "🏆 Top Chatters 🏆\n"
        for i, (user, points) in enumerate(top_5, 1):
            leaderboard += f"{i}. {user}: {points} points\n"
        return leaderboard

    def show_achievements(self, username):
        achievements = self.user_achievements.get(username, set())
        return f"🏆 {username}'s Achievements: {' '.join(self.achievements[a] for a in achievements)}"

    def change_theme(self, command):
        parts = command.split()
        if len(parts) < 2:
            themes_list = "\n".join([f"- {v} (use: !theme {k})" for k, v in self.themes.items()])
            return f"Available themes:\n{themes_list}\n\nExample: !theme space"
        
        theme = parts[1].lower()
        if theme in self.themes:
            self.current_theme = theme
            return f"🎉 Welcome to {self.themes[theme]}! Try !quiz to test your knowledge!"
        return "Theme not found! Use !theme to see available themes!"

    def start_quiz(self, username, command):
        if not self.current_theme:
            return "Please select a theme first using !theme!"
        
        try:
            # Pre-defined quizzes for each theme
            theme_quizzes = {
                'space': {
                    'question': 'What is the closest planet to the Sun?',
                    'options': ['A) Mercury', 'B) Venus', 'C) Earth'],
                    'correct': 'A'
                },
                'animals': {
                    'question': 'Which animal is known as the King of the Jungle?',
                    'options': ['A) Elephant', 'B) Lion', 'C) Tiger'],
                    'correct': 'B'
                },
                'science': {
                    'question': 'What is H2O more commonly known as?',
                    'options': ['A) Air', 'B) Fire', 'C) Water'],
                    'correct': 'C'
                },
                'books': {
                    'question': 'Who wrote "Harry Potter"?',
                    'options': ['A) J.K. Rowling', 'B) Roald Dahl', 'C) Dr. Seuss'],
                    'correct': 'A'
                },
                'art': {
                    'question': 'Which of these is a primary color?',
                    'options': ['A) Green', 'B) Blue', 'C) Orange'],
                    'correct': 'B'
                }
            }
            
            self.current_quiz = theme_quizzes[self.current_theme]
            
            quiz_text = f"🎯 Quiz Time!\n{self.current_quiz['question']}\n"
            for option in self.current_quiz['options']:
                quiz_text += f"\n{option}"
            quiz_text += "\n\nUse !answer A, B, or C to respond!"
            
            return quiz_text
            
        except Exception as e:
            return f"Quiz error: {str(e)}"

    def check_answer(self, username, command):
        if not self.current_quiz:
            return "No active quiz! Use !quiz to start one!"
            
        parts = command.split()
        if len(parts) < 2:
            return "Please provide an answer! Example: !answer A"
            
        answer = parts[1].upper()
        if answer == self.current_quiz['correct']:
            points = self.add_points(username, 5, "correct quiz answer")
            self.current_quiz = None
            return f"🎉 Correct! {points}"
        else:
            return "Not quite! Try again! 🎯"

    def get_theme_response(self, message):
        try:
            if not self.current_theme:
                return None
                
            prompt = f"""As a {self.themes[self.current_theme]} expert, if this message needs any fun facts or gentle corrections about {self.current_theme}, provide them. If not, respond with 'NONE'.
            Message: {message}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            
            fact = response.choices[0].message.content
            return None if fact == 'NONE' else fact
            
        except Exception:
            return None

    def start_story(self, username, command):
        if self.story_active:
            return "There's already a story in progress! Use !add to contribute or !endstory to finish it!"
        
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            return """Start a story with a theme! Try:
🐉 !story fantasy
🚀 !story space
🏰 !story fairytale
🌈 !story adventure
🎵 !story musical"""
        
        self.story_active = True
        self.story_theme = parts[1].lower()
        self.story_parts = []
        self.story_contributors = set()
        
        starter_prompt = f"Create a kid-friendly story starter for a {self.story_theme} theme story. Keep it short and exciting!"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": starter_prompt}],
                temperature=0.8,
                max_tokens=100
            )
            
            story_start = response.choices[0].message.content
            self.story_parts.append({"part": story_start, "author": "Moderator"})
            
            return f"""📖 New {self.story_theme.title()} Story Started! 📖

{story_start}

Add to the story using !add [your part]
Keep it kid-friendly and fun! 🌟"""

        except Exception:
            self.story_active = False
            return "Oops! Couldn't start the story. Try again! 📚"

    def add_to_story(self, username, command):
        if not self.story_active:
            return "No story in progress! Start one with !story [theme]"
            
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            return "What happens next? Use !add [your part of the story]"
            
        story_addition = parts[1]
        
        try:
            # Check if addition is appropriate and fits the story
            check_prompt = f"""Check if this story addition is:
            1. Kid-friendly
            2. Fits the {self.story_theme} theme
            3. Continues the story naturally
            
            Story so far: {self.story_parts[-1]['part']}
            Addition: {story_addition}
            
            Respond with APPROVED or REJECTED with reason."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": check_prompt}],
                temperature=0.7,
                max_tokens=100
            )
            
            if "REJECTED" in response.choices[0].message.content:
                return "Hmm, that doesn't quite fit our story. Try something else! 🎨"
            
            self.story_parts.append({"part": story_addition, "author": username})
            self.story_contributors.add(username)
            
            # Award points for contributing
            self.add_points(username, 3, "contributing to the story")
            
            # Check if story should end
            if len(self.story_parts) >= self.max_story_parts:
                return self.end_story(username)
            
            return f"""Added to the story! ✨
{len(self.story_parts)}/{self.max_story_parts} parts written.
Use !add to continue or !endstory to finish!"""
            
        except Exception:
            return "Oops! Couldn't add to the story. Try again! 📚"

    def end_story(self, username):
        if not self.story_active:
            return "No story in progress!"
            
        full_story = "\n\n".join([f"{part['author']}: {part['part']}" for part in self.story_parts])
        
        # Bonus points for all contributors
        for contributor in self.story_contributors:
            self.add_points(contributor, 5, "completing a story")
            
        self.story_active = False
        self.story_parts = []
        self.story_contributors = set()
        
        return f"""📖 Story Complete! 📖

{full_story}

Everyone gets +5 points for finishing! Start a new story with !story [theme]"""

def main():
    moderator = ChatModerator()
    
    print("Welcome to the Kid's Chatroom!")
    print("Type !help for available commands")
    print("Type 'quit' to exit")
    
    while True:
        username = input("\nWhat's your name? ")
        if username.lower() == 'quit':
            print("Catch you later, kiddos! 👋")
            break
            
        if username.lower() == 'history':
            for message in moderator.conversation_history:
                print(f"\n{message['role'].capitalize()}: {message['content']}")
            continue
        
        # Add name check here
        name_ok, message = moderator.check_name(username)
        if not name_ok:
            print(f"\nModerator: {message}")
            continue
            
        message = input(f"{username}, what do you want to say? ")
        response = moderator.moderate_message(username, message)
        
        if response == "APPROVED":
            print(f"\n{username}: {message}")
        else:
            print(f"\nModerator: {response}")

if __name__ == "__main__":
    main() 