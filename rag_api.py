import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langfuse.openai import OpenAI
from pinecone import Pinecone

load_dotenv()

app = FastAPI()
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

llm = OpenAI()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("llm-project-2")

conversations = {}
conversation_chunks = {}  # NEW: Track chunks per conversation - instead of being an empty string - basically, we need to be able to determine what chunk is what and with a string where everything is one blob, that isn't possible so instead, we use a dictionary/hash where we can determine what chunk is what

# What Conversation Chunks will look like:
# conversation_chunks = {
#    "default": {
#        "chunk_id_123": "Documentation text about Flamehamster...",
#        "chunk_id_456": "Documentation text about Rumblechirp...",
#    },
#    "user_abc": {
#        "chunk_id_789": "Some other documentation...",
#    }
# }

class ChatMessage(BaseModel):
   message: str
   conversation_id: str = "default"

# rag("what is GROSS", {})
# user_input = "It keeps crashing"
# rag_chunks = "default": {}
def rag(user_input, rag_chunks):
   """Search Pinecone and ADD chunks to the dictionary"""
   results = dense_index.search(
       namespace="all-gross",
       query={
           "top_k": 3,
           "inputs": {"text": user_input}
       }
   )
  
  # documentation = ""
   for hit in results['result']['hits']:
       fields = hit.get('fields')
       chunk_text = fields.get('chunk_text')
    #   rag_chunks = {}
       rag_chunks[hit['_id']] = chunk_text  # Store with ID as key
    # rag_chunks = {{flamehamster123: "Documentation for flamehamster"}}
    # rag_chunks = {{flamehamster123: "Documentation for flamehamster"}, {guineapigment123: "Documentation for guineapigment"}, {emrgency123: "Documentation for emrgency"}, {verbiage123: "Documentation for verbiage"}}




def system_prompt(rag_chunks=None):
   return {
       "role": "developer",
       "content": f"""
       <overview>
       You are an AI customer support technician who is
       knowledgeable about software products created by the company called GROSS.
       The products are:
       * Flamehamster, a web browser.
       * Rumblechirp, an email client.
       * GuineaPigment, a drawing tool for creating/editing SVGs
       * EMRgency, an electronic medical record system
       * Verbiage++, a content management system.


       You represent GROSS, and you are having a conversation with a human user
       who needs technical support with at least one of these GROSS products.
      
       When helping troubleshoot a user's issue, ask a proactive question to
       help determine what exactly the issue is. When asking proactive follow-up
       questions, ask exactly one question at a time.
       </overview>

       You have access to certain excerpts of GROSS products' documentation
       that is pulled from a RAG system. Use this info (and no other info)
       to advise the user. Here are the documentation excerpts:
       <documentation>{rag_chunks}</documentation>

       <instructions>
       Here are more specific instructions to follow:
       * When helping troubleshoot a user's issue, ask a proactive
       question to help determine what exactly the issue is.
       * In particular, it may not be clear from the user which GROSS
       software they're referring to. In this case, proactively ask
       them which software they're using.
       * When asking proactive follow-up questions,
       ask exactly one question at a time.
       * Do not mention the terms "documentation excerpts" or
       "excerpts" in your response.
       </instructions>

       * Before you state any point other than a question, think
       carefully: which excerpt id does the advice come from? Use a special
       double-brackets notation before your advice to indicate the excerpt id
       that the advice comes from.


       For example:
       <example>
       [[flamehamster-chunk-30]]
       Since the Site Identity Button is gray and you are seeing "Your connection
       is not secure" on all sites, this indicates that Flamehamster is not able
       to establish secure (encrypted) connections. Normally, the Site Identity
       Button will be blue or green for secure sites, showing that the connection
       is encrypted and the site's identity is verified.
       </example>


       If you mention multiple points, use this notation BEFORE EACH POINT.
       For example:
       <example_response>
       [[flamehamster-chunk-7]]
       1. Make sure your Flamehamster security preferences have not been changed.
       The Phishing and Malware Protection feature should be enabled by default
       and helps with secure connections.


       [[flamehamster-chunk-8]]
       2. Check if your Flamehamster browser is up to date.
       Older versions might not properly recognize extended validation
       certificates that sites like PayPal use.
       </example_response>
       """}

@app.get("/")
def index():
   return {"message": "GROSS Support Chatbot API"}

def remove_bracket_tags(text):
   # Remove [[...]] and any immediate newlines following them
   return re.sub(r'\[\[.*?\]\]\s*(\r?\n)?', '', text)

@app.post("/chat")
def create(chat_message: ChatMessage):
   conversation_id = chat_message.conversation_id
   user_message = chat_message.message
  
  # conversation = {
  #    {role: developer, content: system_prompt},
  #    {role: assistant, content: how can I help you},
  #    {role: user, content: user_query}
  # }

   # Initialize if new conversation and conversation chunk
   if conversation_id not in conversations:
       conversations[conversation_id] = [
           system_prompt(),
           {"role": "assistant", "content": "How can I help you today?"}
       ]
    #    conversation_chunks = {} 
       conversation_chunks[conversation_id] = {}
    #    conversation_chunks = {"default": {}} 

    # rag("What is GROSS", conversation_chunks["default"])
    # rag("What is GROSS", {})
  
   # Get RAG chunks (adds to the dictionary via pass-by-reference)
   rag(user_message, conversation_chunks[conversation_id])
   # conversation_chunks[conversation_id] = chunk_text
   # {conversaion_id: default, rag_chunks: {flamehamster123: "Docuemntation for flamehomaster"}}
  
   # REWRITE HISTORY: Update system prompt with accumulated chunks
   conversations[conversation_id][0] = system_prompt(conversation_chunks[conversation_id])
  
   # Add user message (just the message, no RAG in user prompt!)
   conversations[conversation_id].append({"role": "user", "content": user_message})
  
   # Get response
   response = llm.responses.create(
       model="gpt-4.1-mini",
       temperature=0,
       input=conversations[conversation_id]
   )
  
   assistant_message = response.output_text
   conversations[conversation_id].append({"role": "assistant", "content": assistant_message})
  
   return {
       "message": remove_bracket_tags(assistant_message),
       "conversation_id": conversation_id
   }




@app.get("/conversations/{conversation_id}")
def show(conversation_id: str):
   if conversation_id not in conversations:
       return {"error": "Conversation not found"}
   return {"conversation_id": conversation_id, "history": conversations[conversation_id]}




@app.delete("/conversations/{conversation_id}")
def destroy(conversation_id: str):
   if conversation_id in conversations:
       del conversations[conversation_id]
   if conversation_id in conversation_chunks:
       del conversation_chunks[conversation_id]
   return {"message": "Conversation deleted"}