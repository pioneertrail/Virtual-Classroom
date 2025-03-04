import random
from datetime import datetime

class EducationalActivities:
    def __init__(self):
        self.activities = {
            'space': [
                {
                    'type': 'quiz',
                    'question': 'Which planet is known as the Red Planet?',
                    'options': ['A) Venus', 'B) Mars', 'C) Jupiter'],
                    'correct': 'B',
                    'explanation': 'Mars is called the Red Planet because of its reddish appearance!'
                },
                {
                    'type': 'activity',
                    'title': 'Planet Drawing Challenge',
                    'description': 'Draw a picture of your favorite planet and describe three interesting facts about it!'
                }
            ],
            'animals': [
                {
                    'type': 'quiz',
                    'question': 'Which animal is the fastest on land?',
                    'options': ['A) Lion', 'B) Cheetah', 'C) Gazelle'],
                    'correct': 'B',
                    'explanation': 'Cheetahs can run up to 70 miles per hour!'
                },
                {
                    'type': 'activity',
                    'title': 'Animal Research Project',
                    'description': 'Choose an animal and create a fact sheet about its habitat, diet, and special features!'
                }
            ],
            'science': [
                {
                    'type': 'quiz',
                    'question': 'What is the hardest natural substance on Earth?',
                    'options': ['A) Gold', 'B) Diamond', 'C) Iron'],
                    'correct': 'B',
                    'explanation': 'Diamond is the hardest natural substance known to humans!'
                },
                {
                    'type': 'activity',
                    'title': 'Simple Science Experiment',
                    'description': 'Try this fun experiment: Mix baking soda and vinegar to see what happens!'
                }
            ]
        }

    def get_activity(self, theme, student_profile):
        if theme not in self.activities:
            return "Theme not found! Try space, animals, or science!"
            
        # Choose an activity based on student's learning style
        style = student_profile.profile['learning_style']['primary']
        activities = self.activities[theme]
        
        if style == 'visual':
            # Prefer activities with visual elements
            activity = next((a for a in activities if a['type'] == 'activity'), activities[0])
        else:
            # Mix of activities
            activity = random.choice(activities)
            
        return self.format_activity(activity)

    def format_activity(self, activity):
        if activity['type'] == 'quiz':
            return f"""🎯 Quiz Time! 🎯
{activity['question']}

Options:
{chr(10).join(activity['options'])}

Use !answer A, B, or C to respond!"""
        else:
            return f"""🎨 Activity Time! 🎨
{activity['title']}

{activity['description']}

Share your work with !share when you're done!"""

    def check_answer(self, theme, answer):
        if theme not in self.activities:
            return "Theme not found!"
            
        quiz = next((a for a in self.activities[theme] if a['type'] == 'quiz'), None)
        if not quiz:
            return "No active quiz found!"
            
        if answer.upper() == quiz['correct']:
            return f"🎉 Correct! {quiz['explanation']}"
        else:
            return "Not quite! Try again! 🎯" 