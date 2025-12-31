import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("llm-project-1")

user_query = "How can I add a bookmark?"

results = dense_index.search(
  namespace="flamehamster",
  query={
    "top_k": 3,
    "inputs": {
      'text': user_query
    }
  }
)

# print(results)

# convert chunks into one long string of documentation
documentation = ""

for hit in results['result']['hits']:
  fields = hit.get('fields')
  chunk_text = fields.get('chunk_text')
  documentation += chunk_text

print(documentation)