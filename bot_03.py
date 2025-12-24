import pprint
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

llm = OpenAI()
# creates an instance of the OpenAI client class so we can communicate with OpenAI's API
# Similar to how we initialize a class in ruby with person = Person.new

# Memory System

assistant_message = input("Assistant: How can I help you today? \n\nUser: ")
user_input = input(f"Assistant: {assistant_message}\n")
history = [
  {"role": "developer", "content": "You are a helpful AI assistant who always talks like Albert Pennington IV of Poughkeepsie"},
  {"role": "assistant", "content": assistant_message},
  {"role": "user", "content": user_input}
]

while user_input != "exit":
  response = llm.responses.create(
    model="gpt-4.1-mini",
    temperature=1,
    # input = "What was the biggest news in the world last year?"
    # augmenting the prompt
    input=history
  )
  
  print(f"\nAssistant: {response.output_text}")

  user_input = input("\nUser: ")

  history += [
    {"role": "assistant", "content": response.output_text},
    {"role": "user", "content": user_input}    
  ]

print("-------------------")
print(history)
print("-------------------")

# see OpenAI's docs for where we get the llm.responses.create - https://github.com/openai/openai-python