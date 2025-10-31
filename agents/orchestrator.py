# agents/orchestrator.py
import json
from typing import Any, List, Optional
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from agents.tools import all_tools

from config import MENU

from db.manager import db_manager

from typing import Annotated, TypedDict
import logging
logger = logging.getLogger("food_agent")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    llm_with_tools_instance: Any
    user_id: Optional[str]

def chatbot_node(state: State):
    logger.info("🤖 Chatbot node executing with LLM+tools")
    llm_tools = state["llm_with_tools_instance"]
    response = llm_tools.invoke(state["messages"])
    return {"messages": [response]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot_node)
tool_node = ToolNode(tools=all_tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

def food_agent(query: str, user_id: str = "anon", chat_history: list = None, api_key: str = None) -> str:
    chat_history = chat_history or []
    if chat_history:
        chat_history = chat_history[-6:]
    llm_api_key = api_key
    model_name = "gemini-2.5-flash"  # or from env/config
    model_provider = "google_genai"
    llm_instance = init_chat_model(
        model_name,
        model_provider=model_provider,
        api_key=llm_api_key
    )
    llm_with_tools_instance = llm_instance.bind_tools(tools=all_tools)
    system_prompt = f"""
You are the Friendly Food Ordering Assistant. You can:
- Show the menu, calculate costs, create orders, show user orders, show order details, cancel orders, and update statuses.
- Use the provided tools whenever appropriate. Tools return both structured data and a short 'text' summary. Prefer calling tools for CRUD operations.
- Always confirm with the user before creating or cancelling orders if the user's intent is ambiguous.
- Keep responses short, helpful, and conversational.
- If a user mentions only a title (e.g., an order number) but not the ID, ask a clarifying question.
- Use the 'user_id' present in the conversation context to scope orders.
- If a user ask about previous orders then return all data related to those order in table form like order id, items, total_cost, order date and time , status etc.

Chat history:
{json.dumps(chat_history, default=str)}
"""
    user_prompt = f"User ({user_id}): {query}"
    initial_messages = [
        ("system", system_prompt),
        ("user", user_prompt)
    ]
    events = graph.stream(
        {
            "messages": initial_messages,
            "llm_with_tools_instance": llm_with_tools_instance,
            "user_id": user_id
        },
        stream_mode="values",
    )
    final_response = None
    for event in events:
        if "messages" in event:
            for msg in event["messages"]:
                if isinstance(msg, dict):
                    if msg.get("type") == "ai":
                        final_response = msg.get("content")
                    elif msg.get("type") == "text" and "text" in msg:
                        final_response = msg["text"]
                    else:
                        final_response = json.dumps(msg)
                elif hasattr(msg, "type") and hasattr(msg, "content"):
                    if msg.type == "ai":
                        final_response = msg.content
                    else:
                        final_response = getattr(msg, "text", getattr(msg, "content", str(msg)))
                else:
                    final_response = str(msg)
    if isinstance(final_response, list) and final_response:
        first = final_response[0]
        if isinstance(first, dict) and "text" in first:
            return first["text"]
        return str(first)
    if isinstance(final_response, dict) and "text" in final_response:
        return final_response["text"]
    if isinstance(final_response, str):
        return final_response
    return "No response generated."
