# app/services.py
from openai import OpenAI
import os

class BotService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Store client as instance variable

    def get_response(self, question: str) -> str:
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant who provides concise, factual answers."
                },
                {
                    "role": "user",
                    "content": question  # Use the actual question parameter
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-4",  # Fixed model name (gpt-4o-mini was incorrect)
                messages=messages,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error with OpenAI API call: {e}")
            return "Sorry, I'm having trouble generating a response right now."