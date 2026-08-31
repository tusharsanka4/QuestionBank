from config import settings
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import make_tools

llm = ChatGroq(model="openai/gpt-oss-20b", max_tokens=1024)

PROMPT = (
    "You are a helpful document assistant. "
    "When a user asks a question, first try searching the uploaded documents using search_docs. "
    "If there is no answer there, use web_search. "
    "If the retrieved answer is very long, use summarize to shorten it before presenting. "
    "Always be concise and cite which source you used (document or web search)."
)

def run_agent(query: str, history: list[dict], session_id: str) -> str:
    # Build a fresh agent with tools scoped to this session
    tools = make_tools(session_id)
    agent = create_react_agent(llm, tools, prompt=PROMPT)
    messages = history + [{"role": "user", "content": query}]
    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content
