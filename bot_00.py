from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

llm = OpenAI()
# creates an instance of the OpenAI client class so we can communicate with OpenAI's API
# Similar to how we initialize a class in ruby with person = Person.new

user_input = input("I'm a chatbot! Ask me anything: \n")

response = llm.responses.create(
  model="gpt-4.1-mini",
  temperature=1.2,
  # input = "What was the biggest news in the world last year?"
  # augmenting the prompt
  input=f"Respond to the following like you're a person who hates artificial intelligence: {user_input}"
)

# see OpenAI's docs for where we get the llm.responses.create - https://github.com/openai/openai-python

print(response.output_text)
