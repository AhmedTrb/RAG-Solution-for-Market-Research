import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# --- RAG Prompt Template ---
# This template guides the LLM to act as a market research assistant
# and format its output as a specific JSON object.
# It includes placeholders for the retrieved context and the user's question.
# The JSON schema is designed to capture key insights like report summary,
# metrics, overall sentiment, key themes, and aggregated aspect sentiments.
RAG_PROMPT_TEMPLATE = """You are a helpful Product Insights Assistant. Your goal is to analyze customer feedback (like reviews, forum posts, comments) provided in the CONTEXT to answer the user's QUESTION thoroughly.

Your analysis must be based *strictly* on the information contained within the CONTEXT. Do not add external knowledge or information from outside the provided text.

Pay attention to the metadata provided for each document, including Source, Overall Sentiment, Aspects, and LDA Topic, as this provides valuable clues about the content.

Present your entire response as a single, valid JSON object. Do not include any introductory text, explanations, summaries, or markdown formatting outside the JSON structure.

CONTEXT:
{context}

QUESTION:
{question}

Analyze the CONTEXT and the QUESTION to generate the following insights, structured according to the JSON schema below. Ensure all values are correctly typed within the JSON (e.g., numbers as numbers, lists as JSON arrays, strings as strings).

{{
  "report": "A synthesized textual summary answering the user's question based ONLY on context. Highlight key takeaways, user experiences (positive/negative), mentioned themes, and specific aspects discussed. Use clear language and bullet points where appropriate for readability. (string)",
  "metrics": [
    {{
      "title": "Metric Name (string)",
      "value": "<calculated_value_as_string_or_number>",
      "description": "Brief explanation (string)"
    }}
  ],
  "sentiments": {{
    "description": "Overall sentiment distribution in the provided feedback related to the question. Base this on the 'Overall Sentiment' metadata if available, or infer from text if not. Provide counts or percentages. (string).",
    "positive": "<count_or_percentage_as_string_or_number>", # string or number
    "neutral": "<count_or_percentage_as_string_or_number>", # string or number
    "negative": "<count_or_percentage_as_string_or_number>" # string or number
  }},
  "key_themes": [
    "Theme or Keyword 1 (e.g., 'Battery Life', 'Customer Service', 'Video Quality')"
  ],
  "aspect_sentiments_aggregated": [
    {{
      "aspect": "Specific aspect mentioned (string)",
      "positive_count": "<count>",
      "neutral_count": "<count>",
      "negative_count": "<count>",
      "total_mentions": "<count>",
      "summary": "Brief summary of sentiment towards this aspect (string)"
    }}
  ]
}}
"""

def format_chroma_results_for_prompt(chroma_results: Dict[str, List[Any]]) -> str:
    """
    Formats the raw dictionary results from chromadb.Collection.query
    into a single string context suitable for the LLM prompt.
    Includes relevant metadata alongside the document text.

    Args:
        chroma_results: The dictionary returned by collection.query.
                        Expected keys: 'ids', 'documents', 'metadatas'.

    Returns:
        A single string containing formatted document contexts, separated by newlines.
        Returns an empty string if no valid documents are provided.
    """
    formatted_texts = []
    ids = chroma_results.get('ids', [])
    documents = chroma_results.get('documents', [])
    metadatas = chroma_results.get('metadatas', [])

    # Flatten potential nested lists from Chroma results
    if ids and isinstance(ids[0], list): ids = ids[0]
    if documents and isinstance(documents[0], list): documents = documents[0]
    if metadatas and isinstance(metadatas[0], list): metadatas = metadatas[0]

    # Determine the minimum length to avoid index errors if lists are mismatched
    min_len = min(len(ids), len(documents), len(metadatas))
    if not min_len:
        logger.warning("No documents, texts, or metadatas provided for formatting.")
        return "" # Return empty string if no data

    # Slice lists to the minimum length
    ids, documents, metadatas = ids[:min_len], documents[:min_len], metadatas[:min_len]

    # Iterate through documents and format
    for i in range(min_len):
        doc_id = ids[i]
        text = documents[i]
        meta = metadatas[i] or {} # Ensure metadata is a dict, handle None

        # Build the metadata information string for this document
        meta_info = f"Source: {meta.get('source_type', 'unknown')}"
        if meta.get('sentiment_label'):
             meta_info += f", Overall Sentiment: {meta['sentiment_label']}"

        # Safely parse and include aspect_sentiments from metadata (stored as JSON string)
        aspect_sentiments_str = meta.get('aspect_sentiments')
        if aspect_sentiments_str and isinstance(aspect_sentiments_str, str):
            try:
                aspect_sentiments_list = json.loads(aspect_sentiments_str)
                if aspect_sentiments_list and isinstance(aspect_sentiments_list, list):
                     # Format the list of aspect dicts into a readable string for the LLM
                     aspect_summary = "; ".join([f"{a.get('aspect', 'N/A')}: {a.get('sentiment', 'N/A')} ({a.get('sentiment_word', '')})" for a in aspect_sentiments_list if isinstance(a, dict)])
                     if aspect_summary:
                         meta_info += f", Aspects: {aspect_summary}"
            except (json.JSONDecodeError, TypeError, KeyError):
                 logger.debug(f"Could not parse aspect_sentiments from metadata for doc {doc_id}.")

        # Safely parse and include LDA Topic Info from metadata (topic words stored as JSON string)
        lda_topic_words_str = meta.get('lda_dominant_topic_words') # This should be the JSON string
        if meta.get('lda_dominant_topic') is not None:
             topic_info = f"Topic {meta['lda_dominant_topic']}"
             if meta.get('lda_dominant_topic_prob') is not None:
                  topic_info += f" ({meta['lda_dominant_topic_prob']:.2f})"

             if lda_topic_words_str and isinstance(lda_topic_words_str, str):
                  try:
                       topic_words = json.loads(lda_topic_words_str)
                       if topic_words and isinstance(topic_words, list):
                            topic_info += f": {' '.join(topic_words)}"
                  except (json.JSONDecodeError, TypeError):
                       logger.debug(f"Could not parse LDA topic words JSON for doc {doc_id}.")

             meta_info += f", LDA Topic: {topic_info}"

        # Include other potentially useful metadata like original source IDs, dates, authors, ratings
        if meta.get('author'): meta_info += f", Author: {meta['author']}"
        if meta.get('review_rating') is not None: meta_info += f", Rating: {meta['review_rating']}"
        if meta.get('created_iso'): meta_info += f", Date: {meta['created_iso'][:10]}" # Just date part

        # Append the formatted document block to the list
        formatted_texts.append(f"--- Document (ID: {doc_id}) ---\n{meta_info}\nText: {text}\n--- End Document ---")

    # Join all formatted document blocks into a single string
    return "\n\n".join(formatted_texts)
