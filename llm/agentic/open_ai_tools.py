
import json
from real_world import get_room_temperature, set_room_temperature
from openai import OpenAI

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_room_temperature",
            "description": "Get the current room temperature in Celsius.",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_room_temperature",
            "description": "Set the room temperature to a specified value in Celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_temp": {
                        "type": "number",
                        "description": "The target temperature in Celsius.",
                    }
                },
                "required": ["target_temp"],
            },
        }
    }
]

available_functions = {
    "get_room_temperature": get_room_temperature,
    "set_room_temperature": set_room_temperature,
}

def process_messages(client, messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )

    response_message = response.choices[0].message

    messages.append(response_message)

    if response_message.tool_calls:
       for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            function_response = function_to_call(**function_args)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant that can get and set the room temperature.",
    },
    {
        "role": "user",
        "content": "Can you make it a couple of degrees warmer in here?",
    }
]

client = OpenAI()
process_messages(client, messages)

"""
[
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": "call_t7vNPjRlFJ3nKAhdGAz256cZ",
            "function": {
                "arguments": "{}",
                "name": "get_room_temp"
            },
            "type": "function",
        }],
    },
    {
        "tool_call_id": "call_t7vNPjRlFJ3nKAhdGAz256cZ",
        "role": "tool",
        "name": "get_room_temp",
        "content": "74",
    }
]
"""

"""
[
    {
        "role": "assistant",
        "tool_calls": [{
            "function": {
                "name": "set_room_temp"
                "arguments": "{\"temp\":76}",
            },
            "type": "function"
            "id": "call_X2prAODMHGOmgt523Ob9BIij",
        }],
    },
    {
        "role": "tool",
        "name": "set_room_temp",
        "content": "DONE"
        "tool_call_id": "call_X2prAODMHGOmgt523Ob9BIij",
    }
]
"""

messages_2 = [{
    "content": "The room temperature was 74ºF and has been increased to 76°F.",
    "role": "assistant",
}]