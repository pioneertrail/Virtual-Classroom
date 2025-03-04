from openai import OpenAI

class VirtualClassroom:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = """You are a helpful virtual classroom assistant. You help students learn 
        by answering questions, providing explanations, and guiding them through topics. You are 
        knowledgeable, patient, and encouraging."""
        self.messages = []
        
    def get_ai_response(self, user_message):
        try:
            if not self.messages:
                self.messages.append({"role": "system", "content": self.system_prompt})
            
            self.messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages
            )
            
            ai_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            print(f"Error handling message: \n{str(e)}")
            return "I apologize, but I encountered an error processing your message. Please try again." 