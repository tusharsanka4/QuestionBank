import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

CHROMA_DIR = "./chroma_db"

embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def ingest_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedder,
        collection_name="documents"
    )
    vectorstore.add_documents(chunks)
    return vectorstore

def load_vectorstore():
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedder,
        collection_name="documents"
    )



