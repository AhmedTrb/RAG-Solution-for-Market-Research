import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sentiment analyzer')
class SentimentAnalyzer:
    """Class for analyzing sentiment in text using VADER."""
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment in text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text or not isinstance(text, str):
            return {
                'compound': 0.0,
                'pos': 0.0,
                'neu': 0.0,
                'neg': 0.0
            }
        
        return self.analyzer.polarity_scores(text)
    
    def get_sentiment_label(self, compound_score: float) -> str:
        """
        Get sentiment label based on compound score.
        
        Args:
            compound_score: Compound sentiment score
            
        Returns:
            Sentiment label (positive, neutral, negative)
        """
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
