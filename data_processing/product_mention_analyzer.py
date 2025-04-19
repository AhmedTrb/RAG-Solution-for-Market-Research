from typing import List, Dict, Any
import logging

from entity_extractor import EntityExtractor
from sentiment_analyzer import SentimentAnalyzer
from text_cleaner import TextCleaner

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('product mention analyzer')


class ProductMentionAnalyzer:
    """Class for analyzing product mentions in text data."""
    def __init__(self, product_keywords: List[str] = None):
        self.text_cleaner = TextCleaner()
        self.entity_extractor = EntityExtractor(product_keywords)
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_text(self, text: str, source: str = None, meta: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze text for product mentions and sentiment.
        
        Args:
            text: Input text to analyze
            source: Source of the text (e.g., 'amazon', 'reddit')
            meta: Additional metadata
            
        Returns:
            Dictionary with analysis results
        """
        if not text or not isinstance(text, str):
            return {
                'product_mentions': [],
                'entities': {},
                'sentiment': {
                    'compound': 0.0,
                    'pos': 0.0,
                    'neu': 0.0,
                    'neg': 0.0
                },
                'sentiment_label': 'neutral',
                'source': source,
                'meta': meta or {}
            }
        
        # Clean text
        cleaned_text = self.text_cleaner.clean_text(text)
        
        # Extract entities
        entities = self.entity_extractor.extract_entities(cleaned_text)
        
        # Extract product mentions
        product_mentions = self.entity_extractor.extract_product_mentions(cleaned_text)
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze_sentiment(cleaned_text)
        sentiment_label = self.sentiment_analyzer.get_sentiment_label(sentiment['compound'])
        
        # Build result dict
        result = {
            'original_text': text,
            'cleaned_text': cleaned_text,
            'product_mentions': product_mentions,
            'entities': entities,
            'sentiment': sentiment,
            'sentiment_label': sentiment_label,
            'source': source,
            'meta': meta or {}
        }
        
        return result
