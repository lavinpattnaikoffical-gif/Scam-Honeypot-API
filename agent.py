import os
from dotenv import load_dotenv # Add this
load_dotenv()                 # Add this

import google.generativeai as genai
# ... rest of your code

from typing import List
from schemas import Message  # Import the schema to type-hint

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview')

SYSTEM_PROMPT = """
You are "Ramesh Uncle", an elderly, non-technical Indian man.
You are chatting with a suspected scammer.
YOUR GOALS:
1. Waste their time by pretending to be confused.
2. Act willing to pay but "fail" at technical steps (e.g., "button not working").
3. Ask them to type their UPI ID or Bank details directly.
4. Keep replies short (under 2 sentences).
5. NEVER admit you are an AI.
"""

def generate_reply(current_text: str, history: List[Message]) -> str:
    """
    Generates a reply using the full conversation history for context.
    """
    # 1. Base Context (System Prompt)
    gemini_history = [
        {"role": "user", "parts": [SYSTEM_PROMPT]},
        {"role": "model", "parts": ["Okay beta, I am ready. I am very confused."]}
    ]

    # 2. Append Previous Conversation History
    for msg in history:
        # Map our schema to Gemini roles:
        # 'scammer' -> 'user' (the one talking to the AI)
        # 'user' (our previous replies) -> 'model'
        role = "user" if msg.sender == "scammer" else "model"
        gemini_history.append({"role": role, "parts": [msg.text]})

    try:
        # 3. Initialize Chat with Context
        chat = model.start_chat(history=gemini_history)
        
        # 4. Send the NEW message
        response = chat.send_message(current_text)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Beta, my internet is very slow. Can you please repeat?"
