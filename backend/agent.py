import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import tools

load_dotenv()

llm = ChatGroq(model = "llama-3.1-8b-instant", max_tokens = 1024)

agent = create_react_agent(
        llm, tools, prompt = (
            "You are a helpful document assistant"
            "When user asks a question, first try searching the uploaded documents using search_docs"
            "If there is no answer there, use web_search"
            "If the retrieved answer is very long, use summarize to shorten the answer before presenting it"
            "Always be consise and cite which source you used, document or web search")
        )

def run_agent(query : str, history: list[dict]) -> str:
    messages = history + [{"role" : "user", "content": query}]
    result = agent.invoke({"messages" : messages})
    return result["messages"][-1].content


