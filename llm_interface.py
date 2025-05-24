import openai
import os
from dotenv import load_dotenv

# Load from .env
load_dotenv()

# Set API key explicitly
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_prompt(question, preferences):
    base = f"Answer the following question: {question}"
    if preferences:
        prefs = ", ".join(preferences)
        base += f"\nPlease ensure the response adheres to the following preferences: {prefs}"
    return base

def get_response_from_llm(question, preferences):
    prompt = build_prompt(question, preferences)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
