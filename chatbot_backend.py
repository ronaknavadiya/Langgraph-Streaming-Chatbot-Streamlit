from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage, BaseMessage
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


load_dotenv()


# --------------------------  configure DB -----------------------------#
connectionStr = sqlite3.connect("Chatbot-Database", check_same_thread=False)

# --------------------------  configure LLM -----------------------------#

model = os.getenv("OLLAMA_MODEL", "llama3.1")
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

llm = ChatOllama(
    model=model,
    temperature=0.3,
    base_url=base_url
)
# messages = [
#     (
#         "system",
#         "You are a helpful assistant that translates English to French. Translate the user sentence.",
#     ),
#     ("human", "I love programming."),
# ]
# ai_msg = llm.invoke(messages)

class ChatbotState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatbotState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages":[response]}

checkpointer = SqliteSaver(conn=connectionStr)

graph = StateGraph(ChatbotState)

# nodes
graph.add_node("chat_node", chat_node)

# edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node",END)

chatbot = graph.compile(checkpointer=checkpointer)


# extract existing threads from database
def extract_unique_threads():
    unique_threads = set()
    for checkpoint in checkpointer.list(None):
        unique_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(unique_threads)


#----------------------- Test Backend functions ---------------------------  #

# response = chatbot.invoke({"messages":[HumanMessage("Hi, Ronak here..")]}, config={'configurable': {'thread_id': 'thread-1'}})

# print(response)

# print(chatbot.get_state(
#                 config={'configurable': {'thread_id': '356a5548-23e9-49a8-ac74-7f0a6bcd66d8'}}
#             ))


