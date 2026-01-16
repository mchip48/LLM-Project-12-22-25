import os
import json
from dotenv import load_dotenv
from langfuse.openai import openai  
import yagmail

load_dotenv()
llm = openai

TOOLS = [
    {
        "type": "function",
        "name": "send_email",
        "description": "Send an email containing a specific subject and body to a specific recipient.",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient_email": { "type": "string" },
                "subject": { "type": "string" },
                "body": { "type": "string" },
            },
            "required": ["recipient_email", "subject", "body"],
        },
    }
]

def send_email(recipient_email, subject, body):
    yag = yagmail.SMTP(os.getenv("GMAIL_ACCOUNT"), os.getenv("GMAIL_APP_PASSWORD"))
    yag.send(to=recipient_email, subject=subject, contents=body)
    return "Success"  # tool result

def llm_response(history):
    response = llm.responses.create(
        model="gpt-4.1-mini",
        input=history,
        tools=TOOLS
    )
    return response

def system_prompt():
    return """You are a friendly AI assistant who helps human users. In addition to your ability to converse with the user, you are equipped with the ability to send an email if the user so desires.

    Here's how to send an email. You first need to ensure that you have three pieces of information:

    1) The recipient email address
    2) The email subject
    3) The email body

    Then, when you're ready to send the email, use your send_email tool."""

assistant_message = "How can I help?"
user_input = input(f"\nAssistant: {assistant_message}\n\nUser: ")

history = [
    {"role": "developer", "content": system_prompt()},
    {"role": "assistant", "content": assistant_message},
    {"role": "user", "content": user_input}
]

while user_input != "exit":

    while True:  # the agent loop
        response = llm_response(history)
        history += response.output
        # Check: did the LLM output any tool calls?
        tool_calls = [obj for obj in response.output if getattr(obj, "type", None) == "function_call"]
        # This is a Python list comprehension that filters response.output to only keep items where type == "function_call". The getattr() safely checks if the .type attribute exists (returns None if it doesn't). 
        # In plain English: "Give me all the function calls from this response."

        # if tools_calls = None - true
        if not tool_calls:
            break  # No tool calls = we got TEXT = exit the loop!

        # Execute all tool calls and add results to history
        for tool_call in tool_calls:
            # ... execute and add result ...
            function_name = tool_call.name
            args = json.loads(tool_call.arguments)

            if function_name == "send_email":
                result = {"send_email": send_email(**args)}

                history += [{"type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(result)}]
                 # Loop continues - call LLM again!
            

    print(f"\nAssistant: {response.output_text}")

    user_input = input("\nUser: ")
    history += [
        {"role": "assistant", "content": response.output_text},
        {"role": "user", "content": user_input}
    ]

print("****HISTORY****")
print(history)