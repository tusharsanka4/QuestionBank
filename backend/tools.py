from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import StructuredTool
from ingest import load_vectorstore

def make_tools(session_id: str):
    """Build a tool list scoped to a specific session."""

    def search_docs(query: str) -> str:
        vectorstore = load_vectorstore(session_id)
        if vectorstore is None:
            return "No documents uploaded"
        results = vectorstore.similarity_search(query, k=4)
        if not results:
            return "No relevant documents found"
        return "\n\n".join([f"[Chunk {i+1}]: {r.page_content}" for i, r in enumerate(results)])

    def web_search(query: str) -> str:
        tavily = TavilySearchResults(max_results=3)
        results = tavily.invoke(query)
        if not results:
            return "Nothing relevant was found on web, please try something else"
        return "\n\n".join([f"[{r['url']}]\n{r['content']}" for r in results])

    def summarize(query: str) -> str:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model="openai/gpt-oss-20b", max_tokens=1024)
        response = llm.invoke(f"Summarize the following in clear bullet points:\n\n{query}")
        return response.content

    return [
        StructuredTool.from_function(
            func=search_docs,
            name="search_docs",
            description="Search the uploaded documents for relevant information."
        ),
        StructuredTool.from_function(
            func=web_search,
            name="web_search",
            description="Search the web for information not found in documents."
        ),
        StructuredTool.from_function(
            func=summarize,
            name="summarize",
            description="Summarize a long block of text into key points."
        ),
    ]
