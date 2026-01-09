from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load environemnt variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
# Configure CORS (so your frontend can talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize OpenAI client
llm = OpenAI()

# Store conversation histories - one per user
conversations = {}

# Define request body structure (like Rails strong params)
class ChatMessage(BaseModel):
    message: str
    conversation_id: str = "default"

# Root endpoint
@app.get("/")
def index():
    return {
        "message": "Chatbot API",
        "endpoints": {
            "POST /chat": "Send a message to the chatbot",
            "GET /conversations/{conversation_id}": "Get conversation history",
            "DELETE /conversations/{conversation_id}": "Clear conversation history"
        }
    }

# Chat endpoint
@app.post("/chat")
def create(chat_message: ChatMessage):
    # # Add user message to history
    # history.append({"role": "user", "content": chat_message.message})
    conversation_id = chat_message.conversation_id
    user_message = chat_message.message

    # Initialize conversation history if it doesn't already exist
    if conversation_id not in conversations:
        conversations[conversation_id] = [
            {"role": "developer", "content": "You are a helpful AI assistant."}
        ]
    
    conversations[conversation_id].append({"role": "user", "content": user_message})
    # Get response from OpenAI
    response = llm.responses.create(
        model="gpt-4.1-mini",
        temperature=1,
        # input=history
        input=conversations[conversation_id]
    )

    assistant_message = response.output_text

    # Add assistant message to history
    # history.append({"role": "assistant", "content": assistant_message})
    # return {"message": assistant_message}

    conversations[conversation_id].append({"role": "assistant", "content": assistant_message})

    return {
        "message": assistant_message,
        "conversation_id": conversation_id
    }

# Get conversation history
@app.get("/conversations/{conversation_id}")
def show(conversation_id: str):
    if conversation_id not in conversations:
        return {"error": "Conversation not found"}
    return {
        "conversation_id": conversation_id,
        "history": conversations[conversation_id]
    }
# Clear conversation history
@app.delete("/conversations/{conversation_id}")
def destroy(conversation_id: str):
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation deleted"}
    return {"error": "Conversation not found"}