from fastapi import FastAPI
from pydantic import BaseModel
from guideline_bot import GuidelineBot
from guideline_bot_with_ollama import GuidelineOllamaBot
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()
class Query(BaseModel):
    session_id: str
    query: str

json_path = os.path.join(os.path.dirname(__file__), "../data/remo_guideline.json")
openai_api_key = os.getenv("OPENAI_API_KEY")
chatbot = GuidelineBot(json_path, openai_api_key)
ollamaChatbot = GuidelineOllamaBot(json_path)

session_history = {}

@app.post("/chatbot/guideline")
def get_response_with_guideline(query: Query):
    session_id = query.session_id
    if session_id not in session_history:
        session_history[session_id] = [] 
    current_user_input = query.query.strip()
    session_history[session_id].append(f"User: {current_user_input}") 
    response = chatbot.answer_question(current_user_input)
    session_history[session_id].append(f"Chatbot: {response}")
    return {
        "response": response,
        "history": session_history[session_id]
    }

@app.post("/chatbot/guideline/ollama")
def get_response_with_ollama(query: Query):
    session_id = query.session_id
    if session_id not in session_history:
        session_history[session_id] = [] 
    current_user_input = query.query.strip()
    session_history[session_id].append(f"User: {current_user_input}") 
    response = ollamaChatbot.answer_question(current_user_input)
    session_history[session_id].append(f"Chatbot: {response}")
    return {
        "response": response,
        "history": session_history[session_id]
    }