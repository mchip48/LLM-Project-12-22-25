from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

# file i/o 
# reading and writing to files 
# open the flamehamster file, and set the contents equal to the variable documentation
with open("flamehamster.md", "r", encoding="utf-8") as file:
  documentation = file.read()

assistant_message = "Hi, how can I help you today?"
user_input = input(f"Assistant: {assistant_message}\n")
# for the roles, the only valid roles (for OpenAI specifically are - 'assistant', 'system', 'developer', and 'user')
history = [
  {"role": "developer", "content": f"You are an AI customer support technichian who is knowledgeable about software products created by the company called GROSS. One such product is a web browser called Flamehamster. You are to answer user queries below solely on the following documentation: {documentation}"},
  {"role": "assistant", "content": assistant_message},
  {"role": "user", "content": user_input}
]

# Long Context - PACKing - Prompt with All Corpus Knowledge

# summarize the conversation

# RAG - Retrieval Augmented Generation

while user_input != "exit":
  response = llm.responses.create(
    model="gpt-4.1-mini",
    temperature=1,
    input=history
  )

  print(f"\nAssistant: {response.output_text}")

  user_input = input("\nUser: ")

  history += [
    {"role": "assistant", "content": response.output_text},
    {"role": "user", "content": user_input}
  ]

  # print("-----------")
  # print(history)
  # print("-----------")