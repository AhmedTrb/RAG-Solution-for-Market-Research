import os
from dotenv import load_dotenv

# Load environment variables from .env file.
# Assumes the .env file is in the project root or accessible path.
load_dotenv()

# --- API Keys ---
# Ensure your .env file has GOOGLE_API_KEY set
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- ChromaDB Configuration ---
# Directory where ChromaDB will store its data
PERSIST_DIRECTORY = "./RAG-Agent-for-Market-Research/chroma_db_market_research"
# Name of the collection within ChromaDB
COLLECTION_NAME = "market_data_main"

# --- Model Configuration ---
# Google Generative AI Embedding Model
EMBEDDING_MODEL = "models/embedding-001"
# Google Generative AI Chat Model for RAG response generation
CHAT_MODEL = "gemini-2.0-flash" # Or your preferred model
# Temperature for the chat model (controls randomness)
TEMPERATURE = 0.1

# --- Retrieval Configuration ---
# Number of documents to retrieve for each method
RETRIEVER_K = 10

# --- Supported Retrieval Methods ---
# List of names for the different retrieval strategies available
SUPPORTED_RETRIEVAL_METHODS = [
    'similarity',
    'similarity_filter_positive',
    'similarity_filter_negative',
    'keyword',
    'hybrid_similarity_keyword'
]
