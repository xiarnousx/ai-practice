# different pieces of ai
# start off by creating few functions
import os
from openai import OpenAI
from dotenv import load_dotenv

#Load .env file
load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def get_genai_response(instructions, knowledge, memory, goals, tools):
    commands_string = ""
    for key, value in tools.items():
        commands_string += key
        commands_string += " -> "
        commands_string += value['example']
        commands_string += "\n"
    response = client.chat.completions.create(
        model = "gpt-4.1-mini",
        messages = [{
            "role": "user",
            "content": f"""
                Here is the specific task that you are required to complete: '''{instructions}'''
                Here is some additional knowledge you'll need to complete it: '''{knowledge}'''
                Here is some additional memory to give you more background: '''{memory}'''
                Your ultimate goal is: '''{goals}'''
                You have access to the following tools that will allow you to interact with the
                outside world
                '''{commands_string}'''
                When using commands, be sure to include the command string (for example [SEND_EMAIL])
            """
        }]
    )

    response_content = response.choices[0].message.content

    return response_content

def send_email(to, subject, body):
    print(f"Sending email to {to}")
    print(f"subject: {subject}")
    print("--------------------------------------")
    print(f"{body}")


commands = {
       "[SEND_EMAIL]": {'f' : send_email, 'example': '[SEND_EMAIL] | <to email address> | <subject> | <body> -> this sends an email to specified email address with subject and body'},
} # To what degrees and ways to interact with the outside world
def parse_command(response):
    command, *rest = [section.strip() for section in response.split('|')]
    command_details = commands[command]
    function = command_details['f']
    function(*rest)

result = get_genai_response(
    "write response to this email: 'Shaun, I am not really happy about talking too much generative ai'",
    "This is an email from Bob, my boss. We have a pretty good relationship, I have been talking about generative ai lately.",
    "<bob and shaun's email histroy>", # Load this from gmail API
    "Convince Bob that GenAI and AI agents are critical to organization survival for the next decade",
    commands # To what degrees and ways to interact with the outside world

)

# print(result)

parse_command(result)

