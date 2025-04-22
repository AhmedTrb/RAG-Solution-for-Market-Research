import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Any, List, Optional


from entity_extractor import EntityExtractor
from sentiment_analyzer import SentimentAnalyzer
from text_cleaner import TextCleaner

# Set up logging
logger = logging.getLogger('product mention analyzer')


class ProductMentionAnalyzer:
    """Class for analyzing product mentions and sentiment in text data."""
    def __init__(self, global_product_keywords: List[str] = None):
        # Pass global keywords to the extractor
        self.entity_extractor = EntityExtractor(global_product_keywords=global_product_keywords)
        self.sentiment_analyzer = SentimentAnalyzer() # VADER doesn't need keywords
        self.text_cleaner = TextCleaner() # TextCleaner doesn't need keywords
        logger.info("ProductMentionAnalyzer initialized.")


    def analyze_text(self, text: str, source_type: str, meta: Dict[str, Any] = None, contextual_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Analyze text for product mentions, entities, and sentiment.

        Args:
            text: Input text to analyze.
            source_type: Source type of the text (e.g., 'amazon_review', 'reddit_post', 'reddit_comment').
                         Used in the output dictionary.
            meta: Additional metadata dictionary to include in the output.
            contextual_keywords: Keywords specific to this text's context (e.g., product title).

        Returns:
            Dictionary with analysis results and original/meta data.
        """
        # Handle empty/invalid text input early
        if not text or not isinstance(text, str) or not text.strip():
            logger.debug(f"analyze_text received empty or invalid text for source_type: {source_type}. Returning empty result.")
            # Return a structured empty result to maintain consistency
            return {
                'original_text': text,
                'cleaned_text': '',
                'product_mentions': [],
                'entities': {},
                'sentiment': {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}, # Neutral sentiment for empty text
                'sentiment_label': 'neutral',
                'source_type': source_type,
                'meta': meta or {},
                # Placeholder for future features like TF-IDF/LDA
                'tfidf_features': None,
                'lda_topics': None,
            }

        # Clean text
        # Decide whether to remove stopwords here or keep them for analysis like TF-IDF/LDA later.
        # Keeping stopwords often helps with context for embeddings and some analyses.
        # Let's create two versions: one cleaned (more aggressive) and one raw but punctuation/symbol clean.
        # Or, the preprocess_for_nlp method in TextCleaner can handle this.
        # Let's use preprocess_for_nlp with stopwords removal for the primary 'cleaned_text'
        # used for sentiment/entities, as this is common.
        cleaned_text = self.text_cleaner.preprocess_for_nlp(text, remove_stopwords=True)
        # Optional: Keep a less aggressively cleaned version if needed for other features later
        # basic_cleaned_text = self.text_cleaner.clean_text(text)

        # Ensure cleaned_text is not empty after processing, fallback if necessary
        if not cleaned_text.strip():
             logger.debug(f"Cleaned text became empty after processing for source_type: {source_type}. Using original text for analysis if possible.")
             # Fallback: use basic cleaning if preprocess made it empty
             cleaned_text = self.text_cleaner.clean_text(text)
             if not cleaned_text.strip():
                  # If even basic cleaning results in empty, log and return empty analysis
                 logger.warning(f"Text cleaning resulted in empty text for source_type: {source_type}, original: '{text[:50]}...'. Skipping analysis.")
                 return {
                    'original_text': text,
                    'cleaned_text': '', # Still report empty cleaned text
                    'product_mentions': [],
                    'entities': {},
                    'sentiment': {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0},
                    'sentiment_label': 'neutral',
                    'source_type': source_type,
                    'meta': meta or {},
                    'tfidf_features': None,
                    'lda_topics': None,
                }


        # Extract entities, passing contextual keywords
        entities = self.entity_extractor.extract_entities(cleaned_text, contextual_keywords=contextual_keywords)

        # Product mentions are now included in the 'entities' dictionary under 'PRODUCT'
        product_mentions = entities.get('PRODUCT', [])

        # Analyze sentiment on the cleaned text
        sentiment = self.sentiment_analyzer.analyze_sentiment(cleaned_text)
        sentiment_label = self.sentiment_analyzer.get_sentiment_label(sentiment['compound'])

        # Build result dict
        result = {
            'original_text': text, # Keep original for reference
            'cleaned_text': cleaned_text, # Text used for analysis and embedding
            'product_mentions': product_mentions, # From entity extraction
            'entities': entities, # All extracted entities
            'sentiment': sentiment, # VADER scores
            'sentiment_label': sentiment_label, # Label based on compound score
            'source_type': source_type, # e.g., 'amazon_review'
            'meta': meta or {}, # Original metadata
            # Placeholder for future features like TF-IDF/LDA
            'tfidf_features': None,
            'lda_topics': None,
        }

        return result