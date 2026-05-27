import google.generativeai as genai
import os

# Configure the API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
