import os
from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_SECRET_KEY")

llm = OpenAI(openai_api_key=openai_api_key)

result =""