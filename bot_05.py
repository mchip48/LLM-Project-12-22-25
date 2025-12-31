import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
llm = OpenAI()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("llm-project-1")

assistant_message = "How can I help you today?"
print(f"Assistant: {assistant_message}\n")
user_input = input("User: ")
history = [
  {"role": "developer", "content": "You are an AI customer support technician who is knowledgeale about software products created by the company called GROSS. One such product is a web browser called Flamehamster."},
  {"role": "assistant", "content": assistant_message}
]

while user_input != "exit":
  # RAG Step #1 - retrieve relevant chunks from the pinecone index/db
  results = dense_index.search(
    namespace="flamehamster",
    query={
      "top_k": 1,
      "inputs": {
        'text': user_input
      }
    }
  )

  # RAG Step #2 - convert chunks into one ong string of documentation
  documentation = ""

  for hit in results['result']['hits']:
    fields = hit.get('fields')
    chunk_text = fields.get('chunk_text')
    documentation += chunk_text
  
  # RAG Step #3 - Insert the retrieved documentation into the prompt
  history += [
    {"role": "user",
    "content": f"Here are the excerpts from the official Flamehamster web browser documentation: {documentation}. Use whatever info from the above documentation excerpts (and no other info) to answer the following query: {user_input}"}
  ]

  response = llm.responses.create(
    model="gpt-4.1-mini",
    temperature=0.5,
    input=history
  )

  print(f"\nAssistant: {response.output_text}\n")

  history += [
    {"role": "assistant", "content": response.output_text}
  ]

  user_input = input("User: ")