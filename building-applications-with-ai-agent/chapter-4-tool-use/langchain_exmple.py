"""
These building blocks—chat models, messages, tools, and tool invocation—form the foundation of LangChain-based systems
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

# 1) Define the LLM model
llm = ChatOpenAI(model_name="gpt-4o")

# 2) Build the messages
messages = [HumanMessage("What is the weather today?")]

# 3) Define the tool that LLM will call
@tool
def add_numbers(x: int, y: int) -> int:
    return x + y


# Tying everything together

llm_with_tools = llm.bind_tools([add_numbers])
ai_messages = llm_with_tools.invoke(messages)
for tool_call in ai_messages.tool_calls:
    tool_response = add_numbers.invoke(tool_call)