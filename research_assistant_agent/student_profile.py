import json
import os
from datetime import datetime

class StudentProfile:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        # Create profiles directory if it doesn't exist
        os.makedirs("profiles", exist_ok=True)
        self.profile = self.load_or_create_profile()

    def load_or_create_profile(self):
        profile_path = f"profiles/{self.student_id}.json"
        try:
            with open(profile_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "student_id": self.student_id,
                "name": self.name,
                "learning_style": {
                    "primary": None,
                    "secondary": None,
                    "confidence": 0.0
                },
                "interests": [],
                "progress": {
                    "math": {"level": 1, "milestones": []},
                    "language": {"level": 1, "milestones": []}
                },
                "interaction_history": [],
                "chat_settings": {
                    "language": "en",
                    "grammar_corrections": True,
                    "suggestions": True
                }
            }

    def save_profile(self):
        profile_path = f"profiles/{self.student_id}.json"
        with open(profile_path, "w") as f:
            json.dump(self.profile, f, indent=2)

    def add_interaction(self, message, response, engagement="medium"):
        interaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input": message,
            "response": response,
            "engagement": engagement
        }
        self.profile["interaction_history"].append(interaction)
        self.save_profile()

    def update_learning_style(self, primary, secondary, confidence):
        self.profile["learning_style"] = {
            "primary": primary,
            "secondary": secondary,
            "confidence": confidence
        }
        self.save_profile()

    def add_interest(self, interest):
        if interest not in self.profile["interests"]:
            self.profile["interests"].append(interest)
            self.save_profile()

    def get_profile_summary(self):
        return {
            "name": self.profile["name"],
            "learning_style": self.profile["learning_style"],
            "interests": self.profile["interests"],
            "progress": self.profile["progress"]
        } 