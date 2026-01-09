import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langfuse.openai import OpenAI  # Using Langfuse for tracing!
from pinecone import Pinecone

load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Configure CORS (so your frontend can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
llm = OpenAI()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("llm-project-2")  # Use YOUR Pinecone index name

# Store conversations - one per user
conversations = {}


# Request body structure (like Rails strong params)
class ChatMessage(BaseModel):
    message: str
    conversation_id: str = "default"


# Root endpoint
@app.get("/")
def index():
    return {
        "message": "GROSS Support Chatbot API (with RAG)",
        "endpoints": {
            "POST /chat": "Send a message (uses RAG)",
            "GET /conversations/{id}": "Get conversation history",
            "DELETE /conversations/{id}": "Clear conversation"
        }
    }


# RAG Chat endpoint
@app.post("/chat")
def create(chat_message: ChatMessage):
    conversation_id = chat_message.conversation_id
    user_message = chat_message.message
    
    # Initialize conversation if new
    if conversation_id not in conversations:
        conversations[conversation_id] = [
            {"role": "developer", "content": """You are an AI customer support 
            technician who is knowledgeable about software products created by 
            the company called GROSS. The products are:
            * Flamehamster, a web browser.
            * Rumblechirp, an email client.
            * GuineaPigment, a drawing tool for creating/editing SVGs
            * EMRgency, an electronic medical record system
            * Verbiage++, a content management system."""}
        ]
    
    # RAG Step #1 - Retrieve relevant chunks from Pinecone
    results = dense_index.search(
        namespace="all-gross",
        query={
            "top_k": 3,
            "inputs": {"text": user_message}
        }
    )
    
    # RAG Step #2 - Convert chunks into one long string of documentation
    documentation = ""
    for hit in results['result']['hits']:
        fields = hit.get('fields')
        chunk_text = fields.get('chunk_text')
        documentation += chunk_text
    
    # RAG Step #3 - Insert the retrieved documentation into the prompt
    conversations[conversation_id].append({
        "role": "user",
        "content": f"""Here are excerpts from the official GROSS documentation: 
        {documentation}. Use whatever info from the above documentation excerpts 
        (and no other info) to answer the following query: {user_message}. 
        If the user asks something that you are unsure of, make sure to always 
        ask follow-up questions to make sure you're clear on what the user needs. 
        Also, if the user asks something that is vague and you're not sure what 
        service they're asking about, ask follow up questions."""
    })
    
    # Get response from LLM
    response = llm.responses.create(
        model="gpt-4.1-mini",
        temperature=0.5,
        input=conversations[conversation_id]
    )
    
    assistant_message = response.output_text
    
    # Add response to history
    conversations[conversation_id].append({
        "role": "assistant",
        "content": assistant_message
    })
    
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


# Clear conversation
@app.delete("/conversations/{conversation_id}")
def destroy(conversation_id: str):
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation deleted"}
    
    return {"error": "Conversation not found"}