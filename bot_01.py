from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

llm = OpenAI()
# creates an instance of the OpenAI client class so we can communicate with OpenAI's API
# Similar to how we initialize a class in ruby with person = Person.new

user_input = input("Assistant: How can I help you today? \n\nUser: ")

while user_input != "exit":
  response = llm.responses.create(
    model="gpt-4.1-mini",
    temperature=1,
    # input = "What was the biggest news in the world last year?"
    # augmenting the prompt
    input=user_input
  )

  print(f"\nAssistant: {response.output_text}")

  user_input = input("\nUser: ")



# see OpenAI's docs for where we get the llm.responses.create - https://github.com/openai/openai-python
