import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from ingest import load_vectorstore

load_dotenv()

@tool(description = "Search the uploaded documents for relevant information.")
def search_docs(query: str) -> str:
    vectorstore = load_vectorstore()
    if vectorstore is None:
        return "No documents uploaded"
    results = vectorstore.similarity_search(query, k=4)
    if not results:
        return "No relevant documents found"
    return "\n\n".join([f"[Chunk {i+1}]: {r.page_content}" for i, r in enumerate(results)])

@tool(description="Search the web for information not found in documents.")
def web_search(query: str) -> str:
    tavily = TavilySearchResults(max_results =3)
    results = tavily.invoke(query)
    if not results:
        return "Nothing relevant was found on web, please try something else"
    return "\n\n".join([f"[{r['url']}]\n{r['content']}" for r in results])

@tool(description="Summarize a long block of text into key points.")
def summarize(query: str) -> str:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.1-8b-instant", max_tokens=512)
    response = llm.invoke(f"Summarize the following in clear bullet points:\n\n{query}")
    return response.content


tools = [search_docs, web_search, summarize]

