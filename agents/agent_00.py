from dotenv import load_dotenv
from openai import OpenAI
import yagmail
import os

load_dotenv('.env')
llm = OpenAI()

# configuration to setup yagmail to send an email
def send_email(body):
    yag = yagmail.SMTP(os.getenv("GMAIL_ACCOUNT"), os.getenv("GMAIL_APP_PASSWORD"))
    yag.send(to="fiamocar15@gmail.com", subject="Test Email", contents=body)

send_email("Testing 1, 2, 3, Testing 1, 2, 3, Testing 1, 2, 3")

# assistant_message = "How can I help?"
# user_input = input(f"\nAssistant: {assistant_message}\n\nUser: ")

# history = [
#     {"role": "developer", "content": "You are a helpful chatbot."},
#     {"role": "assistant", "content": assistant_message},
#     {"role": "user", "content": user_input}
# ]

# while user_input != "exit":
#     response = llm.responses.create(
#         model="gpt-4.1-mini",
#         input=history,
#     )

#     llm_response_text = f"\nAssistant: {response.output_text}"
#     print(llm_response_text)

#     user_input = input("\nUser: ")
#     history += [
#         {"role": "assistant", "content": response.output_text},
#         {"role": "user", "content": user_input}
#     ]