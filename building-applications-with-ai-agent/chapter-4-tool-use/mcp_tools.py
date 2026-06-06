
from typing import Any, Sequence, TypedDict
from mcp import MultiServerMCPClient, Tool

class AgentState(TypedDict):
    message: Sequence[Any]



mcp_client = MultiServerMCPClient({
    "math": {
        "command": "python3",
        "args": ["src/common/mcp/MCP_math_server.py"],
        "transport": "stdio", # Subprocess -> STDIO JSON-RPC
    },
    "weather": {
        "url": "http://localhost:8000/weather", # HTTP JSON API
        "transport": "streamable_http", # Streamable HTTP responses
    },
})

async def get_mcp_tools() -> list[Tool]:
    return await mcp_client.get_tools()

async def calls_mcp_tools(state: AgentState) -> dict[str, Any]:
    messages = state["messages"]
    last_msg = messages[-1].content.lower()

    # Fetch and cache MCP tools on first call
    global MCP_TOOLS
    if "MCP_TOOLS" not in globals():
        MCP_TOOLS = await get_mcp_tools()
    
    # Simple heuristic: if any digit-operator token appeares, choose "math"

    if any(token in last_msg for token in ["+", "-", "*", "/", "(", ")"]):
        tool_name = "math"
    elif "weather" in last_msg:
        tool_name = "weather"
    else:
        # Not Match - respond directly
        return {"response": "Sorry, I can only answer math and weather questions."}
    
    tool_obj = next(t for t in MCP_TOOLS if t.name == tool_name)

    user_input = messages[-1].content
    mcp_result: str = await tool_obj.arun(user_input)
    
    return { "messages": [{"role": "assistant", "content": mcp_result}] }