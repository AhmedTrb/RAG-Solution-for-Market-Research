import logging
import chromadb
# Import the base class for custom embedding functions from ChromaDB utils
from chromadb.utils.embedding_functions import EmbeddingFunction
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from typing import List # Needed for type hinting in the wrapper

# Import configuration constants from the local package config file
# Assuming 'config.py' is in the same package directory
try:
    from . import config
except ImportError:
    # Fallback import if running as a standalone script or not in a package
    import config


logger = logging.getLogger(__name__)

# Define a custom wrapper class that inherits from ChromaDB's EmbeddingFunction
# This ensures the __call__ method has the signature ChromaDB expects.
class ChromaEmbeddingFunctionWrapper(EmbeddingFunction):
    """
    A wrapper to make a LangChain Embedding model compatible with ChromaDB's
    expected EmbeddingFunction signature.

    ChromaDB's EmbeddingFunction expects a __call__ method that takes
    'input: List[str]' and returns 'List[List[float]]'.
    """
    def __init__(self, langchain_embeddings: GoogleGenerativeAIEmbeddings):
        # Store the actual LangChain embeddings instance
        self._langchain_embeddings = langchain_embeddings
        logger.info("ChromaEmbeddingFunctionWrapper initialized with LangChain embeddings.")

    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        Implements the __call__ method required by ChromaDB's EmbeddingFunction.
        It takes a list of strings and passes it to the wrapped LangChain embeddings
        instance's method that handles batch embedding (typically embed_documents).
        """
        # Call the LangChain embeddings model's method that handles a list of texts
        # GoogleGenerativeAIEmbeddings has an embed_documents method for this.
        logger.debug(f"ChromaEmbeddingFunctionWrapper calling embed_documents for {len(input)} texts.")
        return self._langchain_embeddings.embed_documents(input)


def initialize_rag_components():
    """
    Initializes core RAG components: ChromaDB collection, Google Generative AI Embeddings,
    and Google Generative AI Chat Model.

    Returns:
        tuple: (chroma_collection, rag_llm)
               chroma_collection: The initialized ChromaDB collection object.
               rag_llm: The initialized LangChain ChatGoogleGenerativeAI LLM for RAG.

    Raises:
        ValueError: If GOOGLE_API_KEY is not found in configuration.
        Exception: Catches and re-raises any other errors during initialization.
    """
    logger.info("Initializing RAG components...")

    # Check if the Google API key is available from the config module
    if not config.GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY not found in configuration.")
        raise ValueError("GOOGLE_API_KEY not found in configuration.")

    try:
        # Initialize Embeddings model using LangChain
        # This is the instance we will wrap to make it ChromaDB-compatible
        langchain_embeddings_instance = GoogleGenerativeAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            google_api_key=config.GOOGLE_API_KEY
        )
        logger.info(f"Initialized LangChain Embedding Model: {config.EMBEDDING_MODEL}")

        # Wrap the LangChain embeddings instance with the custom ChromaDB wrapper
        # This wrapped instance conforms to the signature ChromaDB expects
        chroma_embedding_function = ChromaEmbeddingFunctionWrapper(langchain_embeddings_instance)
        logger.info("Wrapped LangChain embeddings for ChromaDB compatibility.")


        # Initialize ChromaDB Persistent Client
        client = chromadb.PersistentClient(path=config.PERSIST_DIRECTORY)

        # Get or create the collection, passing the WRAPPED embedding function
        # This is the crucial step to resolve the signature error.
        collection = client.get_or_create_collection(
             name=config.COLLECTION_NAME,
             embedding_function=chroma_embedding_function # Use the wrapped function here
        )
        logger.info(f"Initialized ChromaDB Client: {config.PERSIST_DIRECTORY}, Collection: {config.COLLECTION_NAME}")
        collection_count = collection.count()
        logger.info(f"ChromaDB collection count: {collection_count} documents.")

        # Initialize the LLM used for generating the final report based on retrieved context
        llm = ChatGoogleGenerativeAI(
            model=config.CHAT_MODEL,
            temperature=config.TEMPERATURE,
            google_api_key=config.GOOGLE_API_KEY
        )
        logger.info(f"Initialized Chat Model: {config.CHAT_MODEL}")

        # Return the initialized collection and LLM instances
        return collection, llm

    except Exception as e:
        # Log any exceptions during initialization and re-raise
        logger.error(f"Failed to initialize RAG components: {e}", exc_info=True)
        raise # Re-raise the exception for the calling script to handle
