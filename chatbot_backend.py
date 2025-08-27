from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage, BaseMessage
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated


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
    messages: Annotated[list[BaseMessage], ]

