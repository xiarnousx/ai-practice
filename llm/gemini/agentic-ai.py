import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configure the Gemini API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_genai_response(instructions, knowledge, memory, goals, tools):
    """
    Generates a response using the Gemini GenAI API based on a structured prompt.
    
    This function takes various pieces of context—instructions, knowledge, memory,
    goals, and available tools—and formats them into a single prompt for the Gemini
    model. It then calls the Gemini API to get a text response.
    """
    
    commands_string = ""
    for key, value in tools.items():
        commands_string += f"{key} -> {value['example']}\n"
        
    prompt = f"""
Here is the specific task that you are required to complete: '''{instructions}'''
Here is some additional knowledge you'll need to complete it: '''{knowledge}'''
Here is some additional memory to give you more background: '''{memory}'''
Your ultimate goal is: '''{goals}'''
You have access to the following tools that will allow you to interact with the outside world:
'''{commands_string}'''
When using commands, be sure to include the command string (for example [SEND_EMAIL] | <to email address> | <subject> | <body>).
"""
    
    # Initialize the Gemini Pro model
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    # Generate content from the model
    response = model.generate_content(prompt)
    
    # Access the generated text from the response
    response_content = response.text
    
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



#result = get_genai_response(
#    "write response to this email: 'Shaun, I am not really happy about talking too much generative ai'",
#    "This is an email from Bob, my boss. We have a pretty good relationship, I have been talking about generative ai lately.",
#    "<bob and shaun's email histroy>", # Load this from gmail API
#    "Convince Bob that GenAI and AI agents are critical to organization survival for the next decade",
#    {
#        "[SEND_EMAIL]": {'f' : send_email, 'example': '[SEND_EMAIL] | <to email address> | <subject> | <body> -> this sends an email to specified email address with subject and body'},
#    } # To what degrees and ways to interact with the outside world
#
#)

result = """
[SEND_EMAIL] | <Bob's email address> | Re: Generative AI | Hi Bob, Thanks for your email. I understand your concern about my enthusiasm for generative AI.  I appreciate you bringing it up directly.  I realize I might have been overly focused on it lately, but I genuinely believe that GenAI and AI agents are not just a passing trend, but critical to our organization's survival and success in the next decade.  We're not just talking about shiny new toys; we're talking about a fundamental shift in how we operate. Consider this:  GenAI can significantly improve efficiency in [mention a specific department or task relevant to your company, e.g.,  "marketing by automating content creation and analysis," or "customer service by providing instant, personalized responses"].  It can also unlock entirely new opportunities for innovation by [mention a specific example relevant to your company, e.g., "analyzing vast datasets to identify emerging market trends," or "developing predictive models to optimize resource allocation"]. I'm not suggesting we abandon our current strategies, but rather integrate these technologies to enhance what we already do well.  Perhaps we could schedule a short meeting next week to discuss specific use cases and address any concerns you might have about implementation and potential risks?  I've also been researching best practices for responsible AI integration, and I'd be happy to share some of that information with you. Let me know what time works best. Best regards, Shaun
"""

parse_command(result)