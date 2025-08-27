from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage, BaseMessage
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv()

model = os.getenv("OLLAMA_MODEL", "llama3.1")

llm = ChatOllama(
    model=model,
    temperature=0.3,
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

checkpointer = InMemorySaver()

graph = StateGraph(ChatbotState)

# nodes
graph.add_node("chat_node", chat_node)

# edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node",END)

chatbot = graph.compile(checkpointer=checkpointer)

response = chatbot.invoke({"messages":[HumanMessage("Hi")]})

print(response)


