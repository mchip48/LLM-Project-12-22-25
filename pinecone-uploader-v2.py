import os
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone
import re

load_dotenv()

# create the function to split up the documentation into proper chunks (by h1)
def split_markdown_by_h1(md_text):
  pattern = r"(?m)^# .+?(?=^# |\Z)"
  chunks = re.findall(pattern, md_text, re.DOTALL)
  return [chunk.strip() for chunk in chunks if chunk.strip()]

# setup pinecone, the directory with our data, and the batch size
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("llm-project-2")
data_dir = Path("data")
BATCH_SIZE = 96

# grab all the documentation from the data directroy
# loop through each file and chunk it, format it, and upsert it before moving onto the next file
for file_path in data_dir.glob("*.md"):
  records = []

  with open(file_path, "r", encoding="utf-8") as f:
    md_content = f.read()

  # chunk up the data
  chunks = split_markdown_by_h1(md_content)
  manual_name = file_path.stem # grabs the filename without the extension

  # format the data for pinecone
  for i, chunk in enumerate(chunks):
    records.append({
      "id": f"{manual_name}-chunk-{i}",
      "chunk_text": chunk,
      "manual": manual_name
    })

  # upsert/upload the data to pinecone
  for i in range(0, len(records), BATCH_SIZE):
    batch = records[i:i + BATCH_SIZE]
    dense_index.upsert_records("all-gross", batch)

print("Complete...")