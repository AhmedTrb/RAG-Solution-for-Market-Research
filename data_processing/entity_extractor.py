import re
import spacy
from typing import Dict, List, Tuple, Optional
import logging


# Set up logging
# Assume basic logging is already set up in the main script or data_processor
logger = logging.getLogger('entity extractor')

# Try to load spaCy model once
try:
    # Use a larger model like en_core_web_md or en_core_web_lg for better results if resources allow
    # spaCy downloads needed: python -m spacy download en_core_web_sm
    nlp_model = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
    logger.info("spaCy model 'en_core_web_sm' loaded successfully.")
except OSError:
    logger.warning("spaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'.")
    logger.warning("Entity extraction will be limited without spaCy.")
    nlp_model = None
    SPACY_AVAILABLE = False


class EntityExtractor:
    """Class for extracting entities from text using spaCy and custom patterns."""
    def __init__(self, global_product_keywords: List[str] = None):
        # Global keywords applicable across all texts
        self.global_product_keywords = global_product_keywords or []
        self.global_product_patterns = [re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE) for kw in self.global_product_keywords]
        self.nlp = nlp_model # Use the globally loaded model
        self.spacy_available = SPACY_AVAILABLE
        logger.info(f"EntityExtractor initialized with {len(self.global_product_keywords)} global product keywords.")

    def extract_entities(self, text: str, contextual_keywords: List[str] = None) -> Dict[str, List[str]]:
        """
        Extract entities from text, including product mentions based on global and contextual keywords.

        Args:
            text: Input text
            contextual_keywords: A list of keywords specific to the current context
                                 (e.g., the title of the Amazon product being reviewed).

        Returns:
            Dictionary with entity types and values.
        """
        entities = {
            'PRODUCT': [],
            'BRAND': [],
            'ORG': [],
            'PERSON': [],
            'GPE': [],  # Countries, cities, etc.
        }

        if not text or not isinstance(text, str) or not text.strip():
            logger.debug("Skipping entity extraction for empty text.")
            return entities # Return empty entities for empty text

        # Extract custom product mentions (global and contextual)
        all_keywords = self.global_product_keywords + (contextual_keywords or [])
        all_patterns = self.global_product_patterns + [re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE) for kw in (contextual_keywords or [])]

        for pattern, keyword in zip(all_patterns, all_keywords):
             # Use search for efficiency if we only need to know if it exists
            if pattern.search(text):
                # Add original keyword text, not the regex pattern
                entities['PRODUCT'].append(keyword)

        # Use spaCy for additional entity extraction if available
        if self.spacy_available:
            try:
                doc = self.nlp(text)

                # Extract named entities
                for ent in doc.ents:
                    if ent.label_ == 'ORG':
                         entities['ORG'].append(ent.text)
                         # Organizations often can be brands
                         # Add to BRAND only if not already in ORG to avoid immediate duplication before list processing
                         if ent.text not in entities['BRAND']:
                             entities['BRAND'].append(ent.text)
                    elif ent.label_ == 'PERSON':
                        entities['PERSON'].append(ent.text)
                    elif ent.label_ == 'GPE':
                        entities['GPE'].append(ent.text)

            except Exception as e:
                 logger.error(f"Error during spaCy entity extraction: {e}")


        # Remove duplicates and keep order (using dict.fromkeys is Python 3.7+ ordered)
        for entity_type in entities:
             # Ensure we only add non-empty strings
            entities[entity_type] = list(dict.fromkeys([e for e in entities[entity_type] if e and isinstance(e, str)]))

        return entities