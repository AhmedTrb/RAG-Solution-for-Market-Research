import re
import spacy
from typing import Dict, List, Tuple
import logging


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('entity extractor')

class EntityExtractor:
    """Class for extracting entities from text using spaCy."""
    def __init__(self, product_keywords: List[str] = None):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.spacy_available = True
        except:
            logger.warning("spaCy model not available. Entity extraction will be limited.")
            self.spacy_available = False
        
        # Custom product keywords to look for
        self.product_keywords = product_keywords or []
        self.product_patterns = [re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE) for kw in self.product_keywords]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with entity types and values
        """
        entities = {
            'PRODUCT': [],
            'BRAND': [],
            'ORG': [],
            'PERSON': [],
            'GPE': []  # Countries, cities, etc.
        }
        
        # Extract custom product mentions
        for pattern, keyword in zip(self.product_patterns, self.product_keywords):
            if pattern.search(text):
                entities['PRODUCT'].append(keyword)
        
        # Use spaCy for additional entity extraction
        if self.spacy_available and text.strip():
            doc = self.nlp(text)
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ == 'ORG':
                    entities['ORG'].append(ent.text)
                    # Organizations often can be brands
                    entities['BRAND'].append(ent.text)
                elif ent.label_ == 'PERSON':
                    entities['PERSON'].append(ent.text)
                elif ent.label_ == 'GPE':
                    entities['GPE'].append(ent.text)
                # spaCy doesn't have a PRODUCT label by default,
                # but sometimes PRODUCT entities are labeled as ORG
        
        # Remove duplicates and keep order
        for entity_type in entities:
            entities[entity_type] = list(dict.fromkeys(entities[entity_type]))
        
        return entities
    
    def extract_product_mentions(self, text: str, additional_patterns: List[Tuple[str, str]] = None) -> List[str]:
        """
        Extract product mentions using patterns and rules.
        
        Args:
            text: Input text
            additional_patterns: Additional regex patterns as (pattern, product_name) tuples
            
        Returns:
            List of product mentions
        """
        products = set()
        
        # Use predefined product keywords
        for pattern, keyword in zip(self.product_patterns, self.product_keywords):
            if pattern.search(text):
                products.add(keyword)
        
        # Use additional patterns
        if additional_patterns:
            for pattern_str, product_name in additional_patterns:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                if pattern.search(text):
                    products.add(product_name)
        
        # Look for common product review patterns
        product_prefixes = [
            r'my new (\w+)',
            r'just bought (?:a|an) (\w+)',
            r'purchased (?:a|an) (\w+)',
            r'ordered (?:a|an) (\w+)',
            r'got (?:a|an) (\w+)',
            r'using (?:a|an) (\w+)',
            r'reviewed? (?:a|an) (\w+)',
            r'trying? (?:a|an) (\w+)',
            r'love (?:my|this) (\w+)',
            r'hate (?:my|this) (\w+)'
        ]
        
        for prefix in product_prefixes:
            matches = re.findall(prefix, text, re.IGNORECASE)
            products.update(matches)
        
        return list(products)
