import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import pandas as pd
import logging
import os
import json

# Import your processing modules
# Assuming they are in the same directory or accessible via package structure
from text_cleaner import TextCleaner
from sentiment_analyzer import SentimentAnalyzer # For document-level sentiment
from entity_extractor import EntityExtractor

from aspect_sentiment_analyzer import AspectSentimentAnalyzer
# Import libraries for corpus-level features (TF-IDF/LDA)
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np 

# Set up logging
logger = logging.getLogger(__name__)

# --- Helper Functions (Keep these or place in a separate helpers.py and import) ---
# Assuming these are correct and accessible:
def safe_utc_isoformat(timestamp_str_or_float: Optional[Any]) -> Optional[str]:
    """Safely converts UTC timestamp string or float to ISO 8601 string."""
    if timestamp_str_or_float is None: return None
    try:
        if isinstance(timestamp_str_or_float, str):
             try: # Format like "Month Day, Year" from Amazon reviews
                 dt_naive = datetime.strptime(timestamp_str_or_float.strip(), '%B %d, %Y')
                 dt_aware = dt_naive.replace(tzinfo=timezone.utc) # Assume UTC if not specified
                 return dt_aware.isoformat()
             except ValueError:
                 pass # Not the Month Day, Year format

             try: # ISO 8601 format with potential Z
                 return datetime.fromisoformat(timestamp_str_or_float.replace('Z', '+00:00')).isoformat()
             except ValueError:
                 pass # Not ISO format

             # Attempt parsing as a float string (Unix timestamp) if it looks like one
             try:
                 float_val = float(timestamp_str_or_float)
                 return datetime.fromtimestamp(float_val, timezone.utc).isoformat()
             except ValueError:
                  pass # Not a float string

             logger.debug(f"Could not parse string timestamp '{timestamp_str_or_float}' with known formats.")
             return None # Could not parse string format

        elif isinstance(timestamp_str_or_float, (int, float)):
             # Handle Unix timestamps
             return datetime.fromtimestamp(timestamp_str_or_float, timezone.utc).isoformat()
        else:
            logger.debug(f"Unsupported type for timestamp: {type(timestamp_str_or_float)}")
            return None

    except Exception as e:
        logger.warning(f"An unexpected error occurred while parsing timestamp '{timestamp_str_or_float}': {e}")
    return None


def parse_price(price_str: Optional[str]) -> Optional[float]:
    """Safely parses a price string into a float."""
    if not price_str or not isinstance(price_str, str): return None
    try:
        cleaned_price = re.sub(r'[$\s€£]', '', price_str).strip()
        if ',' in cleaned_price and '.' not in cleaned_price:
             cleaned_price = cleaned_price.replace(',', '.')
        # Basic attempt to remove thousands separators (e.g., 1,234.56 -> 1234.56)
        cleaned_price = re.sub(r'(?<=\d)[,.](?=\d{3}(?:,|$|\.))', '', cleaned_price) # Remove comma/period followed by 3 digits, if it's not the decimal
        cleaned_price = re.sub(r'[^\d.]', '', cleaned_price) # Remove any remaining non-digit, non-period chars

        if not cleaned_price: return None
        return float(cleaned_price)
    except ValueError:
        logger.debug(f"Could not parse price: '{price_str}' into float."); return None
    except Exception as e:
         logger.warning(f"Unexpected error parsing price '{price_str}': {e}"); return None


def parse_rating(rating_str: Optional[str]) -> Optional[float]:
    """Safely parses a rating string (e.g., '4.3 out of 5') into a float."""
    if not rating_str or not isinstance(rating_str, str) or rating_str.strip().upper() in ['N/A', 'NONE']: return None
    try:
        match = re.search(r'(\d+(\.\d+)?)\s*(?:out of \d+)?', rating_str.strip())
        if match:
             return float(match.group(1))
        else:
             return float(rating_str.strip())
    except ValueError:
        logger.debug(f"Could not parse rating: '{rating_str}' into float."); return None
    except Exception as e:
         logger.warning(f"Unexpected error parsing rating '{rating_str}': {e}"); return None


def parse_review_count(rc_str: Optional[str]) -> Optional[int]:
    """Safely parses a review count string (e.g., '2,430 reviews') into an int."""
    if not rc_str or not isinstance(rc_str, str) or rc_str.strip().upper() in ['N/A', 'NONE']: return None
    try:
        cleaned_rc = re.sub(r'[^\d,.]', '', rc_str.strip())
        cleaned_rc = re.sub(r'[,.]', '', cleaned_rc) # Remove thousands separators
        if not cleaned_rc: return None
        return int(cleaned_rc)
    except ValueError:
        logger.debug(f"Could not parse review count: '{rc_str}' into int."); return None
    except Exception as e:
         logger.warning(f"Unexpected error parsing review count '{rc_str}': {e}"); return None


# --- DataProcessor Class ---
class DataProcessor:
    """Main class for processing data from different sources."""
    def __init__(self, global_product_keywords: List[str] = None):
        # Initialize the core analyzers
        self.text_cleaner = TextCleaner()
        self.sentiment_analyzer = SentimentAnalyzer() # Document-level
        self.entity_extractor = EntityExtractor(global_product_keywords=global_product_keywords)
        # Initialize ABSA analyzer
        self.aspect_sentiment_analyzer = AspectSentimentAnalyzer()

        # Parameters for corpus-level features (TF-IDF/LDA)
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.lda_model: Optional[LatentDirichletAllocation] = None
        self.count_vectorizer_lda: Optional[CountVectorizer] = None # Keep CV used for LDA
        self.tfidf_features_calculated = False
        self.lda_topics_calculated = False
        self.lda_num_topics = 10 # Configurable number of LDA topics
        self.tfidf_max_features = 5000 # Configurable TF-IDF features

        logger.info(f"DataProcessor initialized with {len(global_product_keywords or [])} global product keywords.")

    def analyze_text_item(self, text: str, source_type: str, meta: Dict[str, Any] = None, contextual_keywords: List[str] = None, absa_method: str = 'rule_based') -> Dict[str, Any]:
        """
        Analyzes a single text item (review, post, comment) for product mentions,
        entities, sentiment, and aspects. This is the core analysis method.

        Args:
            text: Input text to analyze.
            source_type: Source type of the text (e.g., 'amazon_review', 'reddit_post').
            meta: Additional metadata dictionary to include in the output.
            contextual_keywords: Keywords specific to this text's context (e.g., product title).
            absa_method: The ABSA method to use ('rule_based', 'lexicon_simple').

        Returns:
            Dictionary with analysis results and original/meta data.
        """
        # Handle empty/invalid text input early
        if not text or not isinstance(text, str) or not text.strip():
            logger.debug(f"analyze_text_item received empty or invalid text for source_type: {source_type}. Returning empty result.")
            return {
                'original_text': text,
                'cleaned_text': '',
                'product_mentions': [],
                'entities': {},
                'sentiment': {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0},
                'sentiment_label': 'neutral',
                'aspect_sentiments': [], # Ensure this is present even if empty
                'source_type': source_type,
                'meta': meta or {},
                'tfidf_features': None,
                'lda_dominant_topic': None,
                'lda_dominant_topic_prob': None,
                'lda_dominant_topic_words': None,
            }

        # Clean text - use preprocess_for_nlp for text used in NLP tasks
        # This version removes stopwords and lemmatizes if spaCy is available
        cleaned_text = self.text_cleaner.preprocess_for_nlp(text, remove_stopwords=True)

        # Ensure cleaned_text is not empty after processing, fallback if necessary
        if not cleaned_text.strip():
             logger.debug(f"Cleaned text became empty after processing for source_type: {source_type}. Original: '{text[:50]}...'.")
             # Fallback: use basic cleaning if preprocess made it empty
             cleaned_text_fallback = self.text_cleaner.clean_text(text)
             if not cleaned_text_fallback.strip():
                  # If even basic cleaning results in empty, log and return empty analysis
                 logger.warning(f"Text cleaning resulted in empty text for source_type: {source_type}, original: '{text[:50]}...'. Skipping analysis.")
                 return {
                    'original_text': text,
                    'cleaned_text': '', # Still report empty cleaned text
                    'product_mentions': [],
                    'entities': {},
                    'sentiment': {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0},
                    'sentiment_label': 'neutral',
                    'aspect_sentiments': [], # Ensure this is present even if empty
                    'source_type': source_type,
                    'meta': meta or {},
                    'tfidf_features': None,
                    'lda_dominant_topic': None,
                    'lda_dominant_topic_prob': None,
                    'lda_dominant_topic_words': None,
                }
             else:
                  cleaned_text = cleaned_text_fallback # Use basic cleaned text if preprocess failed


        # Extract entities, passing contextual keywords
        entities = self.entity_extractor.extract_entities(cleaned_text, contextual_keywords=contextual_keywords)
        product_mentions = entities.get('PRODUCT', []) # Product mentions are part of entities

        # Analyze document-level sentiment
        sentiment = self.sentiment_analyzer.analyze_sentiment(cleaned_text)
        sentiment_label = self.sentiment_analyzer.get_sentiment_label(sentiment['compound'])

        # Perform Aspect-Based Sentiment Analysis (ABSA) using the specified method
        # ABSA is performed on the cleaned text
        aspect_sentiments = self.aspect_sentiment_analyzer.analyze_aspect_sentiment(cleaned_text, method=absa_method)
        # logger.debug(f"ABSA results for text: {aspect_sentiments}") # Too verbose for info level


        # Build result dict
        result = {
            'original_text': text, # Keep original for reference
            'cleaned_text': cleaned_text, # Text used for analysis and embedding
            'product_mentions': product_mentions, # From entity extraction
            'entities': entities, # All extracted entities
            'sentiment': sentiment, # Document-level sentiment scores
            'sentiment_label': sentiment_label, # Document-level label
            'aspect_sentiments': aspect_sentiments, # ABSA results (list of dicts)
            'source_type': source_type, # e.g., 'amazon_review'
            'meta': meta or {}, # Original metadata passed in
            # Placeholders for corpus-level features calculated later
            'tfidf_features': None,
            'lda_dominant_topic': None,
            'lda_dominant_topic_prob': None,
            'lda_dominant_topic_words': None,
        }

        return result

    # Keep process_amazon_json and process_reddit_thread_list methods
    # They should call self.analyze_text_item for each review/post/comment
    # They now accept the absa_method parameter and pass it down

    def process_amazon_json(self, data: List[Dict[str, Any]], absa_method: str = 'rule_based') -> List[Dict[str, Any]]:
        """
        Processes Amazon product data including reviews.
        Calls analyze_text_item for each review.
        Accepts and passes down the absa_method.
        """
        processed_reviews = []
        if not isinstance(data, list):
             logger.error("Invalid input data format for process_amazon_json: Expected a list.")
             return []

        logger.info(f"Starting processing of {len(data)} Amazon product items.")
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                logger.warning(f"Skipping Amazon item {i} due to invalid format (not a dictionary).")
                continue

            product_url = item.get('URL', '')
            product_title = item.get('Title', '').strip()
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
            product_asin = asin_match.group(1) if asin_match else None

            product_meta = {
                'source': 'amazon',
                'source_type_product': 'amazon_product', # Meta specific to the product object itself
                'product_url': product_url if product_url else None,
                'product_title': product_title if product_title else None,
                'product_asin': product_asin,
                'product_price': parse_price(item.get('Price')),
                'product_rating_overall': parse_rating(item.get('Rating')),
                'product_review_count': parse_review_count(item.get('Review Count')),
            }
            product_meta = {k: v for k, v in product_meta.items() if v is not None}

            reviews = item.get('reviews', [])
            if not isinstance(reviews, list):
                logger.warning(f"Reviews field for Amazon item {product_asin or product_title or i} is not a list. Skipping reviews.")
                continue
            if not reviews:
                logger.debug(f"No reviews found for Amazon item: {product_title or product_url or i}.")
                continue

            contextual_keywords = [kw for kw in [product_title, product_asin] if kw]
            # Consider adding brand names if they are not already in global keywords

            for r_idx, review in enumerate(reviews):
                if not isinstance(review, dict):
                    logger.warning(f"Skipping invalid review object at index {r_idx} for product {product_asin or product_title or i}.")
                    continue

                review_title = review.get('title', '').strip()
                review_comment = review.get('comment', '').strip()
                review_rating_from_title = parse_rating(review_title)
                review_date_str = review.get('date', '').replace('Reviewed in the United States on', '').strip()
                review_iso_date = safe_utc_isoformat(review_date_str)

                if not review_title and not review_comment:
                    logger.debug(f"Skipping empty review at index {r_idx} for product {product_asin or product_title or i}.")
                    continue

                text_to_process = f"{review_title}. {review_comment}".strip() if review_title and review_comment else (review_title or review_comment)
                review_unique_id = f"amazon_review_{product_asin or 'unknown'}_{r_idx}"

                review_doc_meta = {
                    'product_asin': product_meta.get('product_asin'),
                    'product_title': product_meta.get('product_title'),
                    'product_url': product_meta.get('product_url'),
                    'source_type': 'amazon_review',
                    'doc_id': review_unique_id, # Use a generic 'doc_id' key for consistency
                    'review_title_orig': review_title,
                    'review_comment_orig': review_comment,
                    'review_rating': review_rating_from_title,
                    'review_created_iso': review_iso_date,
                    'product_rating_overall': product_meta.get('product_rating_overall'),
                    'product_review_count': product_meta.get('product_review_count'),
                 }
                review_doc_meta = {k: v for k, v in review_doc_meta.items() if v is not None}

                # Call analyze_text_item with the specified ABSA method
                analysis_result = self.analyze_text_item(
                    text_to_process,
                    source_type='amazon_review',
                    meta=review_doc_meta,
                    contextual_keywords=contextual_keywords,
                    absa_method=absa_method # Pass the chosen ABSA method
                )

                processed_reviews.append(analysis_result)

        logger.info(f"Finished processing Amazon data. Generated {len(processed_reviews)} review analysis results.")
        return processed_reviews


    def process_reddit_thread_list(self, thread_list: List[Dict[str, Any]], absa_method: str = 'rule_based') -> List[Dict[str, Any]]:
        """
        Processes a list of Reddit threads (post + comments).
        Calls analyze_text_item for each post and comment.
        Accepts and passes down the absa_method.
        """
        processed_reddit_items = []
        if not isinstance(thread_list, list):
             logger.error("Invalid input data format for process_reddit_thread_list: Expected a list.")
             return []

        logger.info(f"Starting processing of {len(thread_list)} Reddit threads.")

        for i, thread_data in enumerate(thread_list):
            if not isinstance(thread_data, dict):
                logger.warning(f"Skipping Reddit thread item {i} due to invalid format (not a dictionary).")
                continue

            # --- Process Post ---
            post_id = thread_data.get('id')
            if not post_id:
                 logger.warning(f"Skipping Reddit thread item {i} due to missing post ID.")
                 continue

            post_title = thread_data.get('title', '').strip().replace('\n', ' ')
            post_selftext = thread_data.get('selftext', '').strip().replace('\n', ' ')
            post_author = thread_data.get('author', '').strip() or None
            post_score = thread_data.get('score')
            post_url = thread_data.get('url', '').strip() or None
            post_permalink = f"https://www.reddit.com/comments/{post_id}/" if post_id else post_url
            post_num_comments = thread_data.get('num_comments')
            post_subreddit = thread_data.get('subreddit', '').strip() or None
            post_created_iso = safe_utc_isoformat(thread_data.get('created_utc'))

            text_to_analyze_post = post_selftext if post_selftext else post_title

            if text_to_analyze_post.strip(): # Only process post if text exists
                post_doc_meta = {
                     'source': 'reddit',
                     'source_type': 'reddit_post', # Explicitly set document source type
                     'doc_id': post_id, # Use a generic 'doc_id' key
                     'author': post_author,
                     'score': post_score,
                     'title_orig': post_title,
                     'url': post_url,
                     'permalink': post_permalink,
                     'num_comments': post_num_comments,
                     'subreddit': post_subreddit,
                     'created_iso': post_created_iso,
                 }
                post_doc_meta = {k: v for k, v in post_doc_meta.items() if v is not None}

                contextual_keywords = [post_subreddit] if post_subreddit else []
                # Call analyze_text_item with the specified ABSA method
                analysis_result_post = self.analyze_text_item(
                    text_to_analyze_post,
                    source_type='reddit_post',
                    meta=post_doc_meta,
                    contextual_keywords=contextual_keywords,
                    absa_method=absa_method # Pass the chosen ABSA method
                )
                processed_reddit_items.append(analysis_result_post)


            comments = thread_data.get('comments', [])
            if not isinstance(comments, list):
                logger.warning(f"Comments field for Reddit thread {post_id or i} is not a list. Skipping comments.")
                continue
            if not comments:
                 logger.debug(f"No comments found for Reddit thread: {post_id or i}.")
                 pass # No comments, move to next thread

            for comment in comments:
                if not isinstance(comment, dict):
                    logger.warning(f"Skipping invalid comment object in thread {post_id or i}.")
                    continue

                comment_id = comment.get('comment_id') or comment.get('id')
                comment_body = comment.get('body', '').strip().replace('\n', ' ')
                comment_author = comment.get('author', '').strip() or None
                comment_score = comment.get('score')
                comment_parent_id = comment.get('parent_id')
                comment_created_iso = safe_utc_isoformat(comment.get('created_utc'))

                if not comment_id or not comment_body.strip():
                    logger.debug(f"Skipping empty or ID-less Reddit comment in thread {post_id or i}.")
                    continue

                comment_unique_id = f"reddit_comment_{comment_id}"

                comment_doc_meta = {
                    'post_id': post_id,
                    'subreddit': post_subreddit,
                    'post_title_orig': post_title,
                    'source': 'reddit',
                    'source_type': 'reddit_comment',
                    'doc_id': comment_unique_id, # Use a generic 'doc_id' key
                    'author': comment_author,
                    'score': comment_score,
                    'parent_id': comment_parent_id,
                    'permalink': f"https://www.reddit.com/comments/{post_id}/_/{comment_id}/" if post_id and comment_id else None,
                    'created_iso': comment_created_iso,
                 }
                comment_doc_meta = {k: v for k, v in comment_doc_meta.items() if v is not None}

                contextual_keywords_comment = [post_subreddit, post_title] if post_subreddit or post_title else []
                # Call analyze_text_item with the specified ABSA method
                analysis_result_comment = self.analyze_text_item(
                    comment_body,
                    source_type='reddit_comment',
                    meta=comment_doc_meta,
                    contextual_keywords=contextual_keywords_comment,
                    absa_method=absa_method # Pass the chosen ABSA method
                )
                processed_reddit_items.append(analysis_result_comment)


        logger.info(f"Finished processing Reddit data. Generated {len(processed_reddit_items)} item analysis results (posts/comments).")
        return processed_reddit_items


    def calculate_corpus_features(self, processed_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates corpus-level features (like TF-IDF or LDA topics) and adds them
        to the processed items. Modifies the list in place.

        Args:
            processed_items: A flat list of dictionaries resulting from processing
                             Amazon and/or Reddit data, containing 'cleaned_text'.

        Returns:
            The same list of dictionaries, with TF-IDF vectors/scores and LDA topics added.
        """
        if not processed_items:
            logger.warning("No processed items available to calculate corpus features.")
            return processed_items

        logger.info(f"Calculating corpus features for {len(processed_items)} potential documents.")

        # Extract the cleaned text documents for corpus analysis
        # Use only items that have non-empty cleaned text
        corpus_docs = [(item.get('cleaned_text', ''), i) for i, item in enumerate(processed_items) if item.get('cleaned_text', '').strip()]
        if not corpus_docs:
            logger.warning("No documents with non-empty cleaned text found for corpus feature calculation. Skipping TF-IDF/LDA.")
            # Ensure all items have None placeholders if calculation was skipped
            for item in processed_items:
                 item['tfidf_features'] = None
                 item['lda_dominant_topic'] = None
                 item['lda_dominant_topic_prob'] = None
                 item['lda_dominant_topic_words'] = None
            return processed_items


        # Separate documents and their original indices
        texts_for_corpus = [doc[0] for doc in corpus_docs]
        original_indices = [doc[1] for doc in corpus_docs]

        # --- Count Vectorizer (Used for both TF-IDF and LDA) ---
        logger.info("Starting CountVectorizer fitting...")
        self.count_vectorizer_lda = CountVectorizer(
            max_features=self.tfidf_max_features, # Limit vocabulary size
            min_df=5, # Ignore terms that appear in less than 5 documents
            max_df=0.95 # Ignore terms that appear in more than 95% of documents
            # stop_words are already removed in TextCleaner
        )
        try:
            count_matrix = self.count_vectorizer_lda.fit_transform(texts_for_corpus)
            feature_names_cv = self.count_vectorizer_lda.get_feature_names_out()
            logger.info(f"CountVectorizer fitted. Matrix shape: {count_matrix.shape}")

            # --- TF-IDF Calculation ---
            logger.info("Starting TF-IDF calculation...")
            # Use TfidfVectorizer with the same vocabulary from CountVectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                 vocabulary=feature_names_cv # Use the same vocabulary
            )
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts_for_corpus)
            feature_names_tfidf = self.tfidf_vectorizer.get_feature_names_out() # Should be same as feature_names_cv

            self.tfidf_features_calculated = True
            logger.info(f"TF-IDF features calculated. Matrix shape: {tfidf_matrix.shape}")

            # Store top N TF-IDF terms and scores per document
            top_n_tfidf = 10 # Number of top TF-IDF terms to store per document
            for doc_idx, original_list_idx in enumerate(original_indices):
                 # Get features and scores for this document
                 feature_index = tfidf_matrix[doc_idx,:].nonzero()[1]
                 tfidf_scores_for_doc = zip(feature_index, [tfidf_matrix[doc_idx, x] for x in feature_index])

                 # Get top N terms by score
                 sorted_scores = sorted(tfidf_scores_for_doc, key=lambda x: x[1], reverse=True)[:top_n_tfidf]

                 # Create a list of (term, score) tuples
                 top_terms_with_scores = [(feature_names_tfidf[i], round(score, 4)) for i, score in sorted_scores]

                 # Add to the original item dictionary
                 processed_items[original_list_idx]['tfidf_features'] = top_terms_with_scores

        except Exception as e:
            logger.error(f"Error during TF-IDF calculation: {e}", exc_info=True)
            self.tfidf_features_calculated = False
            # Ensure all items have None if calculation failed
            for item in processed_items:
                 item['tfidf_features'] = None


        # --- LDA Topic Modeling Calculation ---
        logger.info("Starting LDA topic modeling calculation...")
        # LDA is typically run on the CountVectorizer output
        if self.count_vectorizer_lda is not None and count_matrix is not None: # Only run LDA if CountVectorizer succeeded
            try:
                self.lda_model = LatentDirichletAllocation(
                    n_components=self.lda_num_topics,
                    random_state=42, # for reproducibility
                    n_jobs=-1 # Use all available CPU cores
                )
                lda_topic_distributions = self.lda_model.fit_transform(count_matrix)
                self.lda_topics_calculated = True
                logger.info(f"LDA model fitted. Topic distribution shape: {lda_topic_distributions.shape}")

                # Get top words for each topic (useful for interpreting topics)
                top_words_per_topic = 10 # Number of top words to represent each topic
                topic_top_words_list = []
                for topic_idx, topic in enumerate(self.lda_model.components_):
                    top_word_indices = topic.argsort()[:-top_words_per_topic - 1:-1]
                    top_words = [feature_names_cv[i] for i in top_word_indices]
                    topic_top_words_list.append(top_words)
                    # logger.debug(f"Topic #{topic_idx}: {' '.join(top_words)}") # Log topics for inspection


                for doc_idx, original_list_idx in enumerate(original_indices):
                    # Get topic distribution for this document
                    topic_distribution = lda_topic_distributions[doc_idx]
                    # Get the index of the dominant topic
                    dominant_topic_index = int(np.argmax(topic_distribution)) # Ensure int type
                    dominant_topic_probability = float(np.max(topic_distribution)) # Ensure float type

                    # Get the top words for the dominant topic of this document
                    dominant_topic_words = topic_top_words_list[dominant_topic_index]

                    # Store in the original item dictionary
                    processed_items[original_list_idx]['lda_dominant_topic'] = dominant_topic_index
                    processed_items[original_list_idx]['lda_dominant_topic_prob'] = dominant_topic_probability
                    processed_items[original_list_idx]['lda_dominant_topic_words'] = dominant_topic_words # Top words of the dominant topic
                    # processed_items[original_list_idx]['lda_topic_distribution'] = topic_distribution.tolist() # Store full distribution (can be large)

            except Exception as e:
                 logger.error(f"Error during LDA calculation: {e}", exc_info=True)
                 self.lda_topics_calculated = False
                 # Ensure all items have None if calculation failed
                 for item in processed_items:
                     item['lda_dominant_topic'] = None
                     item['lda_dominant_topic_prob'] = None
                     item['lda_dominant_topic_words'] = None
        else:
             logger.warning("LDA calculation skipped because CountVectorizer failed.")
             for item in processed_items:
                 item['lda_dominant_topic'] = None
                 item['lda_dominant_topic_prob'] = None
                 item['lda_dominant_topic_words'] = None


        logger.info("Corpus feature calculation complete.")
        return processed_items # Return the list with added features


    def prepare_for_chromadb(
        self,
        processed_items: List[Dict[str, Any]]
    ) -> Dict[str, List[Any]]:
        """
        Formats a list of processed analysis results into ChromaDB format.

        Args:
            processed_items: A flat list where each item is the dictionary
                             output of analyze_text_item, potentially enriched
                             with corpus features.

        Returns:
            A dictionary {'ids': [], 'documents': [], 'metadatas': []} ready for ChromaDB.
        """
        chroma_ids = []
        chroma_documents = []
        chroma_metadatas = []
        logger.info(f"Preparing {len(processed_items)} processed items for ChromaDB format.")

        for i, analysis_result in enumerate(processed_items):
            if not isinstance(analysis_result, dict):
                logger.warning(f"Skipping item {i} as it's not a dictionary during ChromaDB preparation.")
                continue

            # Get the unique ID for the document from the 'meta' dictionary
            doc_meta = analysis_result.get('meta', {})
            # Use the generic 'doc_id' key we added during processing
            chroma_id = doc_meta.get('doc_id')

            if not chroma_id:
                 logger.warning(f"Skipping item {i} due to missing unique 'doc_id' in metadata.")
                 continue # Skip if ID is missing


            # Use the cleaned text as the document content for embedding
            chroma_doc = analysis_result.get('cleaned_text', '')

            # Skip if no text content to embed
            if not chroma_doc.strip():
                logger.debug(f"Skipping item {chroma_id} due to empty or whitespace-only cleaned text for ChromaDB.")
                continue


            # Prepare metadata for ChromaDB
            # Include analysis results and original metadata
            chroma_meta = {
                # Core analysis results
                'source_type': analysis_result.get('source_type'),
                'sentiment_label': analysis_result.get('sentiment_label'),
                'sentiment_compound_score': analysis_result.get('sentiment', {}).get('compound'),

                'product_mentions': analysis_result.get('product_mentions', []), # List of strings
                'entities': analysis_result.get('entities', {}), # Dictionary of lists
                'aspect_sentiments': analysis_result.get('aspect_sentiments', []), # List of dicts

                # Corpus features (will be None if not calculated)
                'tfidf_features': analysis_result.get('tfidf_features'), # List of (term, score) tuples
                'lda_dominant_topic': analysis_result.get('lda_dominant_topic'), # Dominant topic index (int)
                'lda_dominant_topic_prob': analysis_result.get('lda_dominant_topic_prob'), # Dominant topic probability (float)
                'lda_dominant_topic_words': analysis_result.get('lda_dominant_topic_words', []), # Top words of dominant topic (list of strings)

                # Original metadata passed during analysis (flattened into the metadata dict)
                **doc_meta, # Includes original IDs, dates, authors, scores, URLs etc.
                 # Add original text for context if needed, but be mindful of size limits in metadata
                'original_text': analysis_result.get('original_text', ''), # Keep original text for display/context
            }

            # Clean None values and convert lists/dicts to JSON strings for ChromaDB
            final_chroma_meta = {}
            for k, v in chroma_meta.items():
                if v is not None:
                     # Convert lists/dicts to JSON strings
                     if isinstance(v, (list, dict)):
                          if v: # Only dump non-empty ones
                             try:
                                 final_chroma_meta[k] = json.dumps(v)
                             except TypeError:
                                 logger.warning(f"Could not JSON serialize metadata key '{k}'. Skipping or storing as string.")
                                 final_chroma_meta[k] = str(v)
                          # If you want empty lists/dicts stored as "{}" or "[]"
                          # else:
                          #      final_chroma_meta[k] = json.dumps(v)
                     elif isinstance(v, (str, int, float, bool)):
                          final_chroma_meta[k] = v
                     else:
                          logger.warning(f"Metadata key '{k}' has unsupported type {type(v)}. Skipping or converting to string.")
                          final_chroma_meta[k] = str(v)


            chroma_ids.append(str(chroma_id)) # Ensure ID is a string
            chroma_documents.append(chroma_doc)
            chroma_metadatas.append(final_chroma_meta)


        logger.info(f"Formatted {len(chroma_ids)} documents for ChromaDB.")
        return {'ids': chroma_ids, 'documents': chroma_documents, 'metadatas': chroma_metadatas}

    # Keep save_processed_data_to_csv method, it's useful for inspection
    def save_processed_data_to_csv(self, processed_items: List[Dict[str, Any]], filename: str = "processed_analysis_results.csv"):
        """Saves the direct analysis results (one row per review/post/comment) to CSV."""
        if not processed_items:
            logger.warning("No processed items provided to save to CSV.")
            return
        try:
            flat_data = []
            for item in processed_items:
                row = {
                    'source_type': item.get('source_type'),
                    'original_text': item.get('original_text'),
                    'cleaned_text': item.get('cleaned_text'),
                    'sentiment_label': item.get('sentiment_label'),
                    'sentiment_compound_score': item.get('sentiment', {}).get('compound'),
                    # Convert lists/dicts to JSON strings for CSV columns
                    'product_mentions_json': json.dumps(item.get('product_mentions', [])), # Renamed to avoid potential conflict
                    'entities_json': json.dumps(item.get('entities', {})),
                    'aspect_sentiments_json': json.dumps(item.get('aspect_sentiments', [])), # Include ABSA
                    'tfidf_features_json': json.dumps(item.get('tfidf_features')), # Include TF-IDF
                    'lda_dominant_topic': item.get('lda_dominant_topic'), # Include LDA
                    'lda_dominant_topic_prob': item.get('lda_dominant_topic_prob'),
                    'lda_dominant_topic_words_json': json.dumps(item.get('lda_dominant_topic_words')),
                    **item.get('meta', {}) # Add all metadata fields
                }
                # Ensure no complex objects remain in the row before creating DataFrame
                cleaned_row = {}
                for k, v in row.items():
                     if isinstance(v, (list, dict)):
                          # This case should ideally be handled above with _json suffixes,
                          # but as a fallback, ensure lists/dicts are JSON strings.
                          try:
                              cleaned_row[k] = json.dumps(v)
                          except TypeError:
                              logger.warning(f"Could not JSON serialize CSV key '{k}'. Storing as string.")
                              cleaned_row[k] = str(v)
                     elif v is not None:
                          cleaned_row[k] = v
                     else:
                          cleaned_row[k] = None # Explicitly keep None if value was None

                flat_data.append(cleaned_row)

            df = pd.DataFrame(flat_data)

            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")

            df.to_csv(filename, index=False, quoting=1)
            logger.info(f"Saved {len(processed_items)} analysis results to {filename}")
        except Exception as e:
            logger.error(f"Failed to save processed data to CSV {filename}: {e}", exc_info=True)
