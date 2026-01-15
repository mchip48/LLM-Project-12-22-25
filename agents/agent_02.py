import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import yagmail  # email-sending library

load_dotenv()
llm = OpenAI()

def send_email(recipient_email, subject, body): # updated to customize recipient and subject
    yag = yagmail.SMTP(os.getenv("GMAIL_ACCOUNT"), os.getenv("GMAIL_APP_PASSWORD"))
    yag.send(to=recipient_email, subject=subject, contents=body)

def extract_double_brace(text):  # updated function to pull out 3 pieces of info
    """
    Extracts three pieces of text inside [[...]] separated by '|'.
    Returns a tuple (part1, part2, part3) or None if no match.
    """
    match = re.search(r"\[\[(.*?)\]\]", text)
    if not match:
        return None

    parts = match.group(1).split("|")
    return tuple(parts)

EMAILS = {
    "Leon": "leon@anyonecanlearntocode.com",
    "CSG": "codeschoolofguam@gmail.com",
    "Fi": "fiamocar15@gmail.com"
}

def system_prompt():
    return f"""You are a friendly AI assistant who helps human users. In addition to your ability to converse with the user, you are equipped with the ability to send an email if the user so desires.

    You have access to some pre-set emails from the company here: {EMAILS}. Use these emails first, unless the user provides a different email to use.

    Here's how to send an email. You first need to ensure that you have three pieces of information:

    1) The recipient email address
    2) The email subject
    3) The email body

    Then, when you're ready to send the email, output the following precise syntax of double braces and single pipes:

    [[recipient email address|email subject|email body]]

    For example, if the user wants to email the message "Hey, what's up?" to bob@example.net with the subject "Hi", output:

    [[bob@example.net|Hi|Hey what's up?]]"""
    # tuple1 = (box@example.com, hi, hey what's up) - tuple
    # list1 = [box@example.com, hi, hey what's up] - list (array)
    # tuple1[0] = somethingelse
    # list1[0] = somethingelse

assistant_message = "How can I help?"
user_input = input(f"\nAssistant: {assistant_message}\n\nUser: ")

history = [
    {"role": "developer", "content": system_prompt()},
    {"role": "assistant", "content": assistant_message},
    {"role": "user", "content": user_input}
]

while user_input != "exit":
    response = llm.responses.create(
        model="gpt-4.1-mini",
        input=history
    )

    email_data = extract_double_brace(response.output_text) # check for tool use
    if email_data:   # if tool is called
        send_email(email_data[0], email_data[1], email_data[2]) 
        llm_response_text = "\nAssistant: I've sent your email! What else can I do to help?"
    else:
        llm_response_text = f"\nAssistant: {response.output_text}"

    print(llm_response_text)

    user_input = input("\nUser: ")
    history += [
        {"role": "assistant", "content": response.output_text},
        {"role": "user", "content": user_input}
    ]