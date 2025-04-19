import pandas as pd
import numpy as np
import re
import os
import logging
import json # Ensure json is imported
import ast

# --- LangChain/ChromaDB Imports ---
import chromadb
import dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from chromadb.utils import embedding_functions

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('chroma_csv_loader')

dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found.")
    exit(1)

# --- Configuration ---
csv_file_path = "output_data_processed/chroma_prepared_final.csv" # Adjust if needed
persist_directory = "./chroma_db_market_research"
collection_name = "market_data_main"
id_column = "chroma_id"
document_column = "document_text"

# --- Load Data ---
try:
    data = pd.read_csv(csv_file_path, header=0, keep_default_na=False)
    logger.info(f"Loaded {len(data)} rows from {csv_file_path}")
except FileNotFoundError:
    logger.error(f"CSV file not found: {csv_file_path}")
    exit(1)
except Exception as e:
    logger.error(f"Error loading CSV: {e}")
    exit(1)

# --- Prepare for ChromaDB ---
if id_column not in data.columns or document_column not in data.columns:
    logger.error(f"CSV must contain '{id_column}' and '{document_column}' columns.")
    exit(1)

chroma_ids = data[id_column].astype(str).tolist()
chroma_documents = data[document_column].astype(str).tolist()
metadata_columns = [col for col in data.columns if col not in [id_column, document_column]]
chroma_metadatas = []

for index, row in data.iterrows():
    meta = {}
    for col in metadata_columns:
        value = row[col]

        if isinstance(value, str) and not value.strip(): continue
        if pd.isna(value): continue

        # Attempt to parse list/dict strings AND convert back to JSON string
        if col in ['product_mentions', 'entities_json']:
            try:
                parsed_value = ast.literal_eval(value)
                # *** FIX: Convert parsed object to JSON string for ChromaDB ***
                meta[col] = json.dumps(parsed_value)
            except (ValueError, SyntaxError, TypeError):
                logger.debug(f"Could not parse '{col}' value: {value}. Storing as raw string.")
                meta[col] = str(value) # Store original string if parsing fails
        else:
            # Handle numpy types
            if isinstance(value, (np.integer, np.int64)): meta[col] = int(value)
            elif isinstance(value, (np.floating, np.float64)): meta[col] = float(value)
            elif isinstance(value, (np.bool_, bool)): meta[col] = bool(value)
            else: meta[col] = str(value) # Default to string

    chroma_metadatas.append(meta)

if not (len(chroma_ids) == len(chroma_documents) == len(chroma_metadatas)):
     logger.error("Length mismatch in prepared ChromaDB lists.")
     exit(1)

logger.info(f"Prepared {len(chroma_ids)} items for ChromaDB ingestion.")

# --- Initialize Embeddings and ChromaDB ---
try:
    google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=GOOGLE_API_KEY, model_name="models/embedding-001"
    )
    client = chromadb.PersistentClient(path=persist_directory)
    logger.info("Embedding function helper and ChromaDB client initialized.")
except Exception as e:
    logger.error(f"Error initializing embeddings function or Chroma client: {e}")
    exit(1)

# --- Load data into ChromaDB ---
logger.info(f"Adding/updating documents in collection '{collection_name}'...")
try:
    collection = client.get_or_create_collection(
         name=collection_name,
         embedding_function=google_ef
    )

    batch_size = 100
    total_items = len(chroma_ids)
    for i in range(0, total_items, batch_size):
        batch_end = min(i + batch_size, total_items)
        batch_ids = chroma_ids[i:batch_end]
        batch_docs = chroma_documents[i:batch_end]
        batch_metas = chroma_metadatas[i:batch_end]

        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas
        )
        logger.info(f"Added batch {i//batch_size + 1}/{(total_items + batch_size - 1)//batch_size} ({batch_end}/{total_items} items)")

    logger.info(f"Successfully added/updated {total_items} documents in ChromaDB collection '{collection_name}'.")

except ValueError as ve:
     # Catch specific metadata validation errors if they still occur
     logger.error(f"Metadata validation error during ChromaDB add: {ve}", exc_info=True)
     # You might want to inspect the failing batch here:
     # print("Problematic Batch IDs:", batch_ids)
     # print("Problematic Batch Metadatas:", batch_metas)
     exit(1)
except Exception as e:
    logger.error(f"Failed to add documents to ChromaDB: {e}", exc_info=True)
    exit(1)

logger.info("ChromaDB loading process finished.")