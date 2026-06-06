from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import requests


@tool
def get_stock_price(ticker: str) -> float:
    """
        Get the current stock price for a given ticker symbol.
    """
    response = requests.get(f"https://api.example.com/stock/{ticker}")
    
    if response.status_code != 200:
        raise ValueError(f"API request failed with status code {response.status_code}")
    
    data = response.json()
    return data["price"]


# Initialize the LLM with GPT-4o and bind the tool
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools([get_stock_price])

messages = [HumanMessage("What is the current stock price of Apple?")]

ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

for tool_call in ai_msg.tool_calls:
    tool_msg = get_stock_price.invoke(tool_call)

    print(f"{tool_msg.name} {tool_call['args']} {tool_msg.content}")
    messages.append(tool_msg)

    print()
    
    final_response = llm_with_tools.invoke(messages)
    print(final_response.content)