import google.generativeai as genai
import config

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Generate content
response = model.generate_content("How to use ChatML with gemini-1.5-flash")

print(response.text)