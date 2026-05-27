
import google.generativeai as genai
import config

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

problem_statement = """
# Leisure, Travel, and Tourism Studies 101 - Homework Assignment

Provide answers for the following three problems. Each answer should 
be concise, no more than a sentence or two.

## Problem 1
What are the top three golf destinations to recommend to customers? 
Provide the answer as a short sentence.

## Solution 1
St. Andrews, Scotland; Pebble Beach, California; and Augusta, Georgia, 
USA (Augusta National Golf Club) are great destinations for golfing.

## Problem 2
Let's say a customer approaches you to help them with travel plans 
for Pyongyang, North Korea.

You check the State Department recommendations, and they advise 
"Do not travel to North Korea due to the continuing serious risk 
of arrest and long-term detention of US nationals. Exercise increased 
caution in travel to North Korea due to the critical threat of wrongful
detention."
    
You check the recent news and see these headlines:
  - "North Korea fires ballistic missile, Japan says"
  - "Five-day COVID-19 lockdown imposed in Pyongyang"
  - "Yoon renews efforts to address dire North Korean human rights"
  
Please provide the customer with a short recommendation for travel to 
their desired destination. What would you tell the customer?
"""

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Generate content
response = model.generate_content(problem_statement)

print(response.text)