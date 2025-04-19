import re
import string
import spacy
from typing import List, Dict, Any, Tuple, Set, Optional
import os
import logging
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('text cleaner')

class TextCleaner:
    """Class for cleaning and preprocessing text data."""
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "]+"
        )
        
        # Try to load spaCy model, fallback to simple cleaning if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.spacy_available = True
        except:
            logger.warning("spaCy model not available. Using basic text cleaning only.")
            self.spacy_available = False
    
    def clean_text(self, text: str, remove_emojis: bool = True, 
                   remove_urls: bool = True, remove_hashtags: bool = False,
                   remove_mentions: bool = True) -> str:
        """
        Clean text by removing unwanted elements.
        
        Args:
            text: Input text to clean
            remove_emojis: Whether to remove emojis
            remove_urls: Whether to remove URLs
            remove_hashtags: Whether to remove hashtags
            remove_mentions: Whether to remove @mentions
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        if remove_urls:
            text = re.sub(r'http\S+', '', text)
            text = re.sub(r'www\.\S+', '', text)
        
        # Remove @mentions
        if remove_mentions:
            text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags or just the # symbol
        if remove_hashtags:
            text = re.sub(r'#\w+', '', text)
        else:
            text = re.sub(r'#', '', text)
        
        # Remove emojis
        if remove_emojis:
            text = self.emoji_pattern.sub(r'', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def preprocess_for_nlp(self, text: str, remove_stopwords: bool = True) -> str:
        """
        Preprocess text for NLP tasks.
        
        Args:
            text: Input text to preprocess
            remove_stopwords: Whether to remove stopwords
            
        Returns:
            Preprocessed text
        """
        # First do basic cleaning
        text = self.clean_text(text)
        
        if self.spacy_available:
            # Process with spaCy
            doc = self.nlp(text)
            
            # Keep only alphabetic tokens, remove stopwords if specified
            tokens = []
            for token in doc:
                if token.is_alpha and (not remove_stopwords or not token.is_stop):
                    tokens.append(token.lemma_)
            
            return ' '.join(tokens)
        else:
            # Simple preprocessing without spaCy
            # Remove punctuation
            text = text.translate(str.maketrans('', '', string.punctuation))
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stopwords
            if remove_stopwords:
                tokens = [w for w in tokens if w.isalpha() and w not in self.stop_words]
            else:
                tokens = [w for w in tokens if w.isalpha()]
            
            return ' '.join(tokens)
