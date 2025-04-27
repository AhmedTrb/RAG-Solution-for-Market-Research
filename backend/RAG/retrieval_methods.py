import logging
import json
from typing import List, Dict, Any, Optional


# Import configuration constants from the local package config file
import config

logger = logging.getLogger(__name__)

class RetrievalMethods:
    """
    Contains different methods for retrieving documents from a ChromaDB collection.
    Initialized with a ChromaDB collection object and the number of documents (k) to retrieve.
    """
    def __init__(self, collection, k: int = config.RETRIEVER_K):
        self.collection = collection
        self.k = k
        # Ensure the collection was successfully initialized
        if self.collection is None:
             logger.error("RetrievalMethods initialized with None collection.")
             raise ValueError("ChromaDB collection must be initialized.")
        logger.info(f"RetrievalMethods initialized with k={self.k}.")

    def retrieve_similarity(self, query: str) -> Dict[str, List[Any]]:
        """
        Performs standard vector similarity search based on the query embedding.

        Args:
            query: The user's query string.

        Returns:
            Dict: Raw results from ChromaDB collection.query.
        """
        logger.info(f"Retrieving (similarity, k={self.k}): {query[:50]}...")
        # Use collection.query for flexibility, specifying query_texts and n_results
        # include=['documents', 'metadatas', 'distances'] ensures we get text, metadata, and similarity scores
        return self.collection.query(
            query_texts=[query],
            n_results=self.k,
            include=['documents', 'metadatas', 'distances']
        )

    def retrieve_similarity_filter_sentiment(self, query: str, sentiment_label: str) -> Dict[str, List[Any]]:
        """
        Performs vector similarity search filtered by a specific sentiment label metadata.

        Args:
            query: The user's query string.
            sentiment_label: The sentiment label to filter by ('positive', 'neutral', 'negative').

        Returns:
            Dict: Raw results from ChromaDB collection.query.
        """
        # Validate the sentiment label input
        if sentiment_label not in ['positive', 'neutral', 'negative']:
            logger.warning(f"Invalid sentiment_label '{sentiment_label}' for filtering. Using 'positive' as default.")
            sentiment_label = 'positive'

        logger.info(f"Retrieving (similarity + {sentiment_label} filter, k={self.k}): {query[:50]}...")
        # Use the 'where' clause in collection.query to filter metadata
        return self.collection.query(
            query_texts=[query],
            n_results=self.k,
            include=['documents', 'metadatas', 'distances'],
            where={"sentiment_label": sentiment_label} # Metadata filter condition
        )

    def retrieve_keyword(self, query: str) -> Dict[str, List[Any]]:
        """
        Performs basic keyword search using ChromaDB's $contains operator on document text.
        Note: This is a simple substring search.

        Args:
            query: The user's query string (used as the keyword phrase).

        Returns:
            Dict: Raw results from ChromaDB collection.query.
        """
        logger.info(f"Retrieving (keyword, k={self.k}): {query[:50]}...")
        # Use the 'where_document' clause with '$contains' to search within the document content
        # query_texts is still needed by the method signature, even if the primary search is keyword-based
        return self.collection.query(
            query_texts=[query],
            n_results=self.k,
            include=['documents', 'metadatas'],
            where_document={'$contains': query} # Keyword search condition
        )

    def retrieve_hybrid_similarity_keyword(self, query: str) -> Dict[str, List[Any]]:
        """
        Combines results from standard vector similarity search and basic keyword search.
        Retrieves k documents from each method and combines them, removing duplicates.

        Args:
            query: The user's query string.

        Returns:
            Dict: Combined results in the same format as collection.query output.
        """
        logger.info(f"Retrieving (hybrid, k={self.k} each): {query[:50]}...")

        # Perform Similarity Search
        sim_results = self.collection.query(
            query_texts=[query],
            n_results=self.k,
            include=['documents', 'metadatas', 'distances']
        )
        logger.info(f"Hybrid: Similarity search found {len(sim_results.get('ids', []))} documents.")

        # Perform Keyword Search
        keyword_results = self.collection.query(
            query_texts=[query], # Still need query_texts for embedding even if using where_document
            n_results=self.k,
            include=['documents', 'metadatas'],
            where_document={'$contains': query}
        )
        logger.info(f"Hybrid: Keyword search found {len(keyword_results.get('ids', []))} documents.")

        # Combine results - simple deduplication
        combined_ids, combined_docs, combined_metas = [], [], []
        seen_ids = set()

        # Helper to flatten nested lists from Chroma results (sometimes happens with batching/includes)
        def flatten_results(results):
             ids, docs, metas = results.get('ids', []), results.get('documents', []), results.get('metadatas', [])
             if ids and isinstance(ids[0], list): ids = ids[0]
             if docs and isinstance(docs[0], list): docs = docs[0]
             if metas and isinstance(metas[0], list): metas = metas[0]
             return ids, docs, metas

        # Add similarity results first
        sim_ids, sim_docs, sim_metas = flatten_results(sim_results)
        for i in range(len(sim_ids)):
             doc_id = sim_ids[i]
             if doc_id not in seen_ids:
                 combined_ids.append(doc_id)
                 combined_docs.append(sim_docs[i])
                 combined_metas.append(sim_metas[i])
                 seen_ids.add(doc_id)

        # Add keyword results, skipping duplicates already added from similarity
        keyword_ids, keyword_docs, keyword_metas = flatten_results(keyword_results)
        for i in range(len(keyword_ids)):
             doc_id = keyword_ids[i]
             if doc_id not in seen_ids:
                 combined_ids.append(doc_id)
                 combined_docs.append(keyword_docs[i])
                 combined_metas.append(keyword_metas[i])
                 seen_ids.add(doc_id)

        logger.info(f"Hybrid search combined {len(combined_ids)} unique documents.")

        # Return the combined results in the expected dictionary format
        return {"ids": combined_ids, "documents": combined_docs, "metadatas": combined_metas}

    def get_supported_methods(self) -> List[str]:
        """Returns a list of supported retrieval method names from config."""
        return config.SUPPORTED_RETRIEVAL_METHODS

    def retrieve(self, query: str, method_name: str) -> Dict[str, List[Any]]:
        """
        Calls the appropriate retrieval method based on the provided name.

        Args:
            query: The user's query string.
            method_name: The name of the retrieval method to use.

        Returns:
            Dict: Raw results from the selected ChromaDB retrieval method.

        Raises:
            ValueError: If the provided method_name is not supported.
        """
        if method_name == 'similarity':
            return self.retrieve_similarity(query)
        elif method_name == 'similarity_filter_positive':
            return self.retrieve_similarity_filter_sentiment(query, 'positive')
        elif method_name == 'similarity_filter_negative':
            return self.retrieve_similarity_filter_sentiment(query, 'negative')
        elif method_name == 'keyword':
            return self.retrieve_keyword(query)
        elif method_name == 'hybrid_similarity_keyword':
            return self.retrieve_hybrid_similarity_keyword(query)
        else:
            # Raise an error if an unsupported method name is provided
            raise ValueError(f"Unknown retrieval method: {method_name}. Supported methods are: {', '.join(self.get_supported_methods())}")
