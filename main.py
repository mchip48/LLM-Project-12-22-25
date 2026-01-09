from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load environemnt variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
llm = OpenAI()

# Store conversation history (single user for now - we'll fix this in Part 6!)
history = [
  {"role": "developer", "content": "You are a helpful AI assistant."}
]

# Define request body structure (like Rails strong params)
class ChatMessage(BaseModel):
    message: str

# Root endpoint
@app.get("/")
def index():
    return {"message": "Chatbot API is running successfully!"}

# Chat endpoint
@app.post("/chat")
def create(chat_message: ChatMessage):
    # Add user message to history
    history.append({"role": "user", "content": chat_message.message})

    # Get response from OpenAI
    response = llm.response.create(
        model="gpt-4.1-mini",
        temperature=1,
        input=history
    )

    assistant_message = response.output_text

    # Add assistant message to history
    history.append({"role": "assistant", "content": assistant_message})

    return {"message": assistant_message}
