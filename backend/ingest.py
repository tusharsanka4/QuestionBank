from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_core.embeddings import Embeddings

CHROMA_DIR = "./chroma_db"

class ChromaDefaultEmbedder(Embeddings):
    def __init__(self):
        self.fn = DefaultEmbeddingFunction()
    def embed_documents(self, texts):
        return self.fn(texts)
    def embed_query(self, text):
        return self.fn([text])[0]

embedder = ChromaDefaultEmbedder()

def ingest_pdf(file_path: str, session_id: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedder,
        collection_name=session_id      # each session gets its own collection
    )
    vectorstore.add_documents(chunks)
    return vectorstore

def load_vectorstore(session_id: str):
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedder,
        collection_name=session_id      # loads only that session's docs
    )
