from langchain.tools import tool
from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from lanchain_core.messages.tool import ToolMessage
from langgraph.graph import StateGraph


# -- 1) Define our single business tool
@tool
def cancel_order( order_id: str) -> str:
    # Cancel an order that hasn't shipped
    #(Here your' call your real backend API)
    return f"Order {order_id} has been cancelled"

# -- 2) The agent "brain" invoke LLM, run tool, then invoke llm again
def call_model(state):
    msgs = state["messages"]
    order = state.get("order", {"order_id": "UNKNOWN"})

    # System prompt tells the model exactly what to do

    prompt = (
        f"""
            You are an ecommerece support agent.
            ORDER ID: {order['order_id']}
            If the customer asks to cancel, call cancel_order(order_id)
            and then send a simple confirmation.
            Otherwise, just respond normally.
        """
    )

    full = [SystemMessage(prompt)] + msgs

    # 1st LLM pass: decides whether to call our tool
    first = ChatOpenAI(model="gpt-5", temperature=0)(full)
    out = [first]

    if getattr(first, "tool_calls", None):
        # Run cancel order tool
        tc = first.tool_calls[0]
        result = cancel_order(**tc["args"])
        out.append(ToolMessage(content= result, tool_call_id = tc["id"]))

        # 2nd LLM pass: generate the final confirmation text
        second = ChatOpenAI(model = "gpt-5", temperature= 0)(full + out)
        out.append(second)
    
    return {"messages": out}

# -- 3) Wire it all up in a StateGraph
def construct_graph():
    g = StateGraph({"order": None, "messages": []})
    g.add_node("assistant", call_model)
    g.set_entry_point("assistant")
    return g.compile()



graph = construct_graph()


def main():
    example_order = {"order_id": "A123456"}
    convo = [HumanMessage(content = "Please cancel my order A12345")]
    result = graph.invoke({"order": example_order, "messages": convo})
    for msg in result['messages']:
        print (f"{msg.type}: {msg.content}")


if __name__ == "__main__":
    main()
