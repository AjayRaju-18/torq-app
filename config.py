import os
from dotenv import load_dotenv

load_dotenv()

# GROQ Configuration
GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.1-8b-instant"

# Vector Store Configuration
VECTOR_DB_PATH = "./torq_vectordb"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 3

# Upload Configuration
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {'pdf'}
