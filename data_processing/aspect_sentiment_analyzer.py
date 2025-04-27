import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any, Optional
import logging
import json # Needed for potential complex results (though less likely now)

# --- Hugging Face Imports (Conceptual - REMOVED) ---
# Removed imports for transformers and deep learning frameworks

# Set up logging for this module
logger = logging.getLogger(__name__)

# --- SpaCy Model Loading ---
# Load spaCy model once when the module is imported.
# This is more efficient than loading it in the class constructor every time.
# Ensure you have run: python -m spacy download en_core_web_sm
try:
    # Using 'en_core_web_sm'.
    # Consider 'en_core_web_md' or 'en_core_web_lg' for potentially better parsing if resources allow.
    nlp_absa = spacy.load("en_core_web_sm")
    SPACY_ABSA_AVAILABLE = True
    logger.info("spaCy model 'en_core_web_sm' loaded successfully for ABSA.")
except OSError:
    logger.warning("SpaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'.")
    logger.warning("SpaCy-dependent ABSA methods will be skipped.")
    SPACY_ABSA_AVAILABLE = False
    nlp_absa = None # Set to None if loading fails


class AspectSentimentAnalyzer:
    """
    Performs Aspect-Based Sentiment Analysis (ABSA) using different methods.
    Requires spaCy and vaderSentiment for current methods.
    """
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer() # VADER for lexicon scoring
        self.nlp = nlp_absa # SpaCy for parsing
        self.spacy_available = SPACY_ABSA_AVAILABLE

        if not self.spacy_available:
            logger.warning("SpaCy not available. Rule-based and Lexicon-based ABSA methods will be limited.")


    def analyze_aspect_sentiment(self, text: str, method: str = 'rule_based') -> List[Dict[str, Any]]:
        """
        Analyzes text to extract aspects and their associated sentiment using a specified method.

        Args:
            text: The input text (should be cleaned text).
            method: The ABSA method to use ('rule_based', 'lexicon_simple').

        Returns:
            A list of dictionaries, where each dict contains 'aspect' (str)
            and 'sentiment' (str: 'positive', 'neutral', 'negative'), plus
            method-specific details like scores or sentiment words.
            Returns an empty list if the method is invalid, dependencies are missing,
            or text is empty/invalid.
        """
        if not text or not isinstance(text, str) or not text.strip():
            logger.debug(f"Skipping ABSA analysis (method: {method}): Input text is empty or invalid.")
            return []

        if method == 'rule_based':
            return self._analyze_rule_based(text)
        elif method == 'lexicon_simple':
             return self._analyze_lexicon_simple(text)
        # Removed elif for 'transformer_hf'
        else:
            logger.warning(f"Unknown ABSA method specified: {method}. Supported: 'rule_based', 'lexicon_simple'.")
            return []

    def _analyze_rule_based(self, text: str) -> List[Dict[str, Any]]:
        """
        Performs rule-based ABSA using spaCy dependency parsing and VADER lexicon.
        """
        if not self.spacy_available:
            logger.warning("Skipping rule_based ABSA: SpaCy model not available.")
            return []

        aspect_sentiments = []
        try:
            doc = self.nlp(text)
            processed_aspects_in_doc = set()

            for token in doc:
                if token.pos_ in ["ADJ", "ADV"]:
                    sentiment_word = token.text
                    word_sentiment_scores = self.analyzer.polarity_scores(sentiment_word)
                    word_compound_score = word_sentiment_scores['compound']

                    if abs(word_compound_score) >= 0.05:
                        potential_aspect = None

                        # Rule 1: Adjective directly modifying a noun ('amod')
                        if token.dep_ == 'amod' and token.head.pos_ == 'NOUN':
                            potential_aspect = token.head.text.lower()

                        # Rule 2: Adverb modifying a verb ('advmod') with noun subject/object
                        elif token.dep_ == 'advmod' and token.head.pos_ == 'VERB':
                            verb = token.head
                            subjects = [child for child in verb.children if child.dep_ == 'nsubj' and child.pos_ == 'NOUN']
                            objects = [child for child in verb.children if child.dep_ == 'dobj' and child.pos_ == 'NOUN']
                            if subjects: potential_aspect = subjects[0].text.lower()
                            elif objects: potential_aspect = objects[0].text.lower()

                        # Rule 3: Noun subject of passive verb modified by adverb
                        elif token.dep_ == 'advmod' and token.head.dep_ == 'auxpass' and token.head.head.pos_ == 'VERB':
                             passive_verb_head = token.head.head
                             subjects = [child for child in passive_verb_head.children if child.dep_ == 'nsubjpass' and child.pos_ == 'NOUN']
                             if subjects: potential_aspect = subjects[0].text.lower()


                        if potential_aspect and potential_aspect not in processed_aspects_in_doc:
                             if word_compound_score >= 0.05: sentiment_label = 'positive'
                             elif word_compound_score <= -0.05: sentiment_label = 'negative'
                             else: sentiment_label = 'neutral'

                             aspect_sentiments.append({
                                 'aspect': potential_aspect,
                                 'sentiment': sentiment_label,
                                 'sentiment_score': float(word_compound_score),
                                 'sentiment_word': sentiment_word,
                                 'method': 'rule_based' # Add method used
                             })
                             processed_aspects_in_doc.add(potential_aspect)

        except Exception as e:
            logger.error(f"Error during rule_based ABSA for text: '{text[:100]}...'", exc_info=True)
            return []

        return aspect_sentiments

    def _analyze_lexicon_simple(self, text: str) -> List[Dict[str, Any]]:
        """
        Performs simple lexicon-based ABSA. Finds noun chunks (potential aspects)
        and checks for nearby sentiment words from VADER's lexicon.
        Less accurate than rule-based as it ignores dependency structure.
        """
        if not self.spacy_available:
            logger.warning("Skipping lexicon_simple ABSA: SpaCy model not available.")
            return [] # Still need spaCy for noun chunks

        aspect_sentiments = []
        try:
            doc = self.nlp(text)
            processed_aspects_in_doc = set()

            # Iterate through noun chunks as potential aspects
            for chunk in doc.noun_chunks:
                aspect_text = chunk.text.lower()
                if not aspect_text or aspect_text in processed_aspects_in_doc: # Check for empty chunk text too
                    continue

                # Look for sentiment words within or near the noun chunk
                # Simple check: look at tokens within the chunk and a few tokens before/after
                start_index = max(0, chunk.start - 3)
                end_index = min(len(doc), chunk.end + 3)
                context_span = doc[start_index:end_index]

                for token in context_span:
                    if token.pos_ in ["ADJ", "ADV"]:
                        sentiment_word = token.text
                        word_sentiment_scores = self.analyzer.polarity_scores(sentiment_word)
                        word_compound_score = word_sentiment_scores['compound']

                        if abs(word_compound_score) >= 0.05:
                            # Found a sentiment word near the aspect
                            if word_compound_score >= 0.05: sentiment_label = 'positive'
                            elif word_compound_score <= -0.05: sentiment_label = 'negative'
                            else: sentiment_label = 'neutral'

                            aspect_sentiments.append({
                                'aspect': aspect_text,
                                'sentiment': sentiment_label,
                                'sentiment_score': float(word_compound_score),
                                'sentiment_word': sentiment_word,
                                'method': 'lexicon_simple'
                            })
                            processed_aspects_in_doc.add(aspect_text)
                            sentiment_found = True
                            break

        except Exception as e:
            logger.error(f"Error during lexicon_simple ABSA for text: '{text[:100]}...'", exc_info=True)
            return []

        return aspect_sentiments




