import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import pandas as pd
import logging
import os
import json
# Ensure these are correctly imported based on your file structure
from product_mention_analyzer import ProductMentionAnalyzer
# Assuming helper functions like safe_utc_isoformat etc. are defined above or in a separate helpers.py
# from helpers import safe_utc_isoformat, parse_price, parse_rating, parse_review_count

# Set up logging
# Assume basic logging is already set up in the main script
logger = logging.getLogger('data_processor')

# --- Helper Functions (Keep or place in a separate helpers.py and import) ---
# Assuming these are correct and accessible:
def safe_utc_isoformat(timestamp_str_or_float: Optional[Any]) -> Optional[str]:
    """Safely converts UTC timestamp string or float to ISO 8601 string."""
    if timestamp_str_or_float is None: return None
    try:
        if isinstance(timestamp_str_or_float, str):
             # Attempt common formats, including handling potential timezone info like 'Z'
             try:
                 # Try parsing as float string first, if it looks like one
                 float_val = float(timestamp_str_or_float)
                 return datetime.fromtimestamp(float_val, timezone.utc).isoformat()
             except ValueError:
                  pass # Not a float string, try date formats

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

             logger.warning(f"Could not parse string timestamp '{timestamp_str_or_float}' with known formats.")
             return None # Could not parse string format

        elif isinstance(timestamp_str_or_float, (int, float)):
             # Handle Unix timestamps
             return datetime.fromtimestamp(timestamp_str_or_float, timezone.utc).isoformat()
        else:
            logger.warning(f"Unsupported type for timestamp: {type(timestamp_str_or_float)}")
            return None

    except Exception as e:
        logger.warning(f"An unexpected error occurred while parsing timestamp '{timestamp_str_or_float}': {e}")
    return None


def parse_price(price_str: Optional[str]) -> Optional[float]:
    """Safely parses a price string into a float."""
    if not price_str or not isinstance(price_str, str): return None
    try:
        # Remove currency symbols, spaces, and handle comma as decimal separator if present
        cleaned_price = re.sub(r'[$\s€£]', '', price_str).strip()
        # Handle cases like "1.234,56" or "1,234.56". Assuming European format if only ',' is present
        if ',' in cleaned_price and '.' not in cleaned_price:
             cleaned_price = cleaned_price.replace(',', '.')
        # Remove thousands separators (commas or periods followed by 3 digits, but only if there's also a decimal)
        if '.' in cleaned_price:
             cleaned_price = re.sub(r'[,.](\d{3})($|\.)', r'\1\2', cleaned_price) # Crude attempt to remove thousands separators
             cleaned_price = re.sub(r'[,.](\d{3})[,.]', r'\1', cleaned_price) # Handle inner separators

        # Final cleaning for non-numeric characters except decimal point
        cleaned_price = re.sub(r'[^\d.]', '', cleaned_price)

        if not cleaned_price: return None # Return None if cleaning results in empty string

        return float(cleaned_price)
    except ValueError:
        logger.warning(f"Could not parse price: '{price_str}' into float."); return None
    except Exception as e:
         logger.error(f"Unexpected error parsing price '{price_str}': {e}"); return None


def parse_rating(rating_str: Optional[str]) -> Optional[float]:
    """Safely parses a rating string (e.g., '4.3 out of 5') into a float."""
    if not rating_str or not isinstance(rating_str, str) or rating_str.strip().upper() in ['N/A', 'NONE']: return None
    try:
        # Look for a number at the start or within the string
        match = re.search(r'(\d+(\.\d+)?)\s*(?:out of \d+)?', rating_str.strip())
        if match:
             return float(match.group(1))
        else:
            # If no specific pattern matched, try a direct float conversion
             return float(rating_str.strip())
    except ValueError:
        logger.warning(f"Could not parse rating: '{rating_str}' into float."); return None
    except Exception as e:
         logger.error(f"Unexpected error parsing rating '{rating_str}': {e}"); return None


def parse_review_count(rc_str: Optional[str]) -> Optional[int]:
    """Safely parses a review count string (e.g., '2,430 reviews') into an int."""
    if not rc_str or not isinstance(rc_str, str) or rc_str.strip().upper() in ['N/A', 'NONE']: return None
    try:
        # Remove non-digit characters except comma/period for thousands, then remove comma/period
        cleaned_rc = re.sub(r'[^\d,.]', '', rc_str.strip())
        cleaned_rc = re.sub(r'[,.]', '', cleaned_rc) # Remove thousands separators

        if not cleaned_rc: return None # Return None if cleaning results in empty string

        return int(cleaned_rc)
    except ValueError:
        logger.warning(f"Could not parse review count: '{rc_str}' into int."); return None
    except Exception as e:
         logger.error(f"Unexpected error parsing review count '{rc_str}': {e}"); return None

# --- Add necessary imports for TF-IDF and LDA ---
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np # Often useful with numerical features

# --- Add imports for ChromaDB (conceptual) ---
# import chromadb
# from chromadb.utils import embedding_functions # You'll need an embedding function here


# --- DataProcessor Class ---
class DataProcessor:
    """Main class for processing data from different sources."""
    def __init__(self, global_product_keywords: List[str] = None):
        # Pass global keywords to the analyzer
        self.product_mention_analyzer = ProductMentionAnalyzer(global_product_keywords=global_product_keywords)
        logger.info(f"DataProcessor initialized with {len(global_product_keywords or [])} global product keywords.")

        # Parameters for corpus-level features (TF-IDF/LDA)
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.lda_model: Optional[LatentDirichletAllocation] = None
        self.tfidf_features_calculated = False
        self.lda_topics_calculated = False


    def process_amazon_json(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes Amazon product data including reviews.
        Input: List of product dictionaries, each containing a 'reviews' list.
        Output: List of analysis result dictionaries, one per review.
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
            # Use product title directly as a key contextual keyword
            product_title = item.get('Title', '').strip()
            # Attempt to extract ASIN from URL if available, otherwise use title or index
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
            product_asin = asin_match.group(1) if asin_match else None

            # Extract and parse product-level metadata
            product_meta = {
                'source': 'amazon',
                'source_type': 'amazon_product', # This meta belongs to the product, not each review doc
                'product_url': product_url if product_url else None, # Store None if empty
                'product_title': product_title if product_title else None,
                'product_asin': product_asin,
                'product_price': parse_price(item.get('Price')),
                'product_rating_overall': parse_rating(item.get('Rating')),
                'product_review_count': parse_review_count(item.get('Review Count')),
                 # Add other product details if available (e.g., Description - but maybe too long for metadata?)
                 # 'product_description': item.get('Description', '').strip() # Can be very long, use cautiously in metadata
            }
            # Clean None values from metadata dict
            product_meta = {k: v for k, v in product_meta.items() if v is not None}


            reviews = item.get('reviews', [])
            if not isinstance(reviews, list):
                logger.warning(f"Reviews field for Amazon item {product_asin or product_title or i} is not a list. Skipping reviews.")
                continue

            if not reviews:
                logger.debug(f"No reviews found for Amazon item: {product_title or product_url or i}.")
                continue

            logger.debug(f"Processing {len(reviews)} reviews for product: {product_title or product_url or i}")

            # Pass product title as a contextual keyword for reviews of this product
            contextual_keywords = [product_title] if product_title else []
            if product_meta.get('product_asin'): # Add ASIN as a keyword too
                 contextual_keywords.append(product_meta['product_asin'])
            # Consider adding known brand names related to this product


            for r_idx, review in enumerate(reviews):
                if not isinstance(review, dict):
                    logger.warning(f"Skipping invalid review object at index {r_idx} for product {product_asin or product_title or i}.")
                    continue

                # Extract and parse review-level data
                review_title = review.get('title', '').strip()
                review_comment = review.get('comment', '').strip()
                # Extract rating specifically from the review title string
                review_rating_from_title = parse_rating(review_title)
                review_date_str = review.get('date', '').replace('Reviewed in the United States on', '').strip()
                review_iso_date = safe_utc_isoformat(review_date_str)


                # Handle missing review text - skip if both title and comment are empty
                if not review_title and not review_comment:
                    logger.debug(f"Skipping empty review at index {r_idx} for product {product_asin or product_title or i}.")
                    continue

                # Combine title and comment for analysis text
                # Add a separator that's unlikely to appear naturally
                text_to_process = f"{review_title} [SEP] {review_comment}".strip() if review_title and review_comment else (review_title or review_comment)
                text_to_process = text_to_process.replace('[SEP]', '. ') # Replace separator for readability after combine

                # Ensure a unique ID for each review document
                # Prioritize review ID if Amazon provides one (they usually don't directly in this format)
                # Fallback to product ASIN + review index
                review_unique_id = f"amazon_review_{product_asin or 'unknown'}_{r_idx}"
                # Add a UUID if you need absolute uniqueness across multiple scrape runs without ASIN
                # import uuid
                # review_unique_id = f"amazon_review_{uuid.uuid4()}"

                # Prepare metadata specific to this review document
                review_doc_meta = {
                    # Link back to product meta
                    'product_asin': product_meta.get('product_asin'),
                    'product_title': product_meta.get('product_title'),
                    'product_url': product_meta.get('product_url'),
                    # Review-specific meta
                    'source_type': 'amazon_review', # Explicitly set document source type
                    'review_id': review_unique_id, # The unique ID for this document
                    'review_title_orig': review_title, # Keep original title
                    'review_comment_orig': review_comment, # Keep original comment
                    'review_rating': review_rating_from_title,
                    'review_created_iso': review_iso_date,
                    # Add other parsed product meta if needed for *every* review doc
                    # 'product_rating_overall': product_meta.get('product_rating_overall'),
                    # 'product_review_count': product_meta.get('product_review_count'),
                     # Store original Amazon metadata fields if they are useful
                    # 'amazon_review_date_raw': review.get('date'),
                    # 'amazon_review_title_raw': review.get('title'),
                 }
                review_doc_meta = {k: v for k, v in review_doc_meta.items() if v is not None} # Clean None values


                # Analyze the combined text using the ProductMentionAnalyzer
                analysis_result = self.product_mention_analyzer.analyze_text(
                    text_to_process,
                    source_type='amazon_review', # Pass explicit source type
                    meta=review_doc_meta, # Pass review-specific metadata
                    contextual_keywords=contextual_keywords # Pass product keywords
                )

                # Add the analysis result to the list
                processed_reviews.append(analysis_result)

        logger.info(f"Finished processing Amazon data. Generated {len(processed_reviews)} review analysis results.")
        return processed_reviews

    def process_reddit_thread_list(self, thread_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a list of Reddit threads (post + comments).
        Input: List of thread dictionaries.
        Output: List of analysis result dictionaries, one per post/comment.
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
                 continue # Skip thread if main post ID is missing

            # Extract and clean post data
            post_title = thread_data.get('title', '').strip().replace('\n', ' ')
            post_selftext = thread_data.get('selftext', '').strip().replace('\n', ' ') # Use selftext if available
            post_author = thread_data.get('author', '').strip() or None # Store None if empty
            post_score = thread_data.get('score')
            post_url = thread_data.get('url', '').strip() or None
            post_permalink_suffix = post_id # Base permalink on post ID
            post_permalink = f"https://www.reddit.com/comments/{post_permalink_suffix}/" if post_permalink_suffix else post_url
            post_num_comments = thread_data.get('num_comments')
            post_subreddit = thread_data.get('subreddit', '').strip() or None
            post_created_iso = safe_utc_isoformat(thread_data.get('created_utc'))


            # Determine text to analyze for the post (prefer selftext over title)
            text_to_analyze_post = post_selftext if post_selftext else post_title

            # Handle empty post text - skip processing this post if both selftext and title are empty
            if not text_to_analyze_post:
                logger.debug(f"Skipping empty Reddit post {post_id or i} (no title or selftext).")
                # We still might process comments if they exist, but the post itself yields no document
            else:
                # Prepare metadata specific to this post document
                post_doc_meta = {
                     'source': 'reddit', # General source
                     'source_type': 'reddit_post', # Explicitly set document source type
                     'post_id': post_id, # The unique ID for this document
                     'author': post_author,
                     'score': post_score,
                     'title_orig': post_title, # Keep original title
                     'url': post_url,
                     'permalink': post_permalink,
                     'num_comments': post_num_comments,
                     'subreddit': post_subreddit,
                     'created_iso': post_created_iso,
                     # 'selftext_orig': post_selftext # Can be long, use cautiously in metadata
                 }
                post_doc_meta = {k: v for k, v in post_doc_meta.items() if v is not None} # Clean None values


                # Analyze the post text
                # For Reddit posts, we might not have specific product keywords from the "product title"
                # unless we add general keywords or derive them from subreddit or post title.
                # Using global_product_keywords is appropriate here.
                analysis_result_post = self.product_mention_analyzer.analyze_text(
                    text_to_analyze_post,
                    source_type='reddit_post', # Pass explicit source type
                    meta=post_doc_meta, # Pass post-specific metadata
                    contextual_keywords=[] # No specific product context from the structure itself
                )
                 # Add the analysis result for the post
                processed_reddit_items.append(analysis_result_post)


            # --- Process Comments ---
            comments = thread_data.get('comments', [])
            if not isinstance(comments, list):
                logger.warning(f"Comments field for Reddit thread {post_id or i} is not a list. Skipping comments.")
                continue

            if not comments:
                 logger.debug(f"No comments found for Reddit thread: {post_id or i}.")

            logger.debug(f"Processing {len(comments)} comments for Reddit thread: {post_id or i}")

            for comment in comments:
                if not isinstance(comment, dict):
                    logger.warning(f"Skipping invalid comment object in thread {post_id or i}.")
                    continue

                # Extract and clean comment data
                comment_id = comment.get('comment_id') or comment.get('id') # Use 'id' if 'comment_id' isn't present
                comment_body = comment.get('body', '').strip().replace('\n', ' ')
                comment_author = comment.get('author', '').strip() or None
                comment_score = comment.get('score')
                comment_parent_id = comment.get('parent_id')
                comment_created_iso = safe_utc_isoformat(comment.get('created_utc'))

                # Handle missing comment ID or empty body - skip
                if not comment_id or not comment_body:
                    logger.debug(f"Skipping empty or ID-less Reddit comment in thread {post_id or i}.")
                    continue

                # Ensure a unique ID for each comment document
                comment_unique_id = f"reddit_comment_{comment_id}"

                # Prepare metadata specific to this comment document
                comment_doc_meta = {
                    # Link back to post meta
                    'post_id': post_id,
                    'subreddit': post_subreddit,
                     'post_title_orig': post_title, # Link post title for context
                     # 'post_url': post_url, # Link post URL for context
                    # Comment-specific meta
                    'source': 'reddit', # General source
                    'source_type': 'reddit_comment', # Explicitly set document source type
                    'comment_id': comment_unique_id, # The unique ID for this document
                    'author': comment_author,
                    'score': comment_score,
                    'parent_id': comment_parent_id, # Link to parent comment/post
                    'permalink': f"https://www.reddit.com/comments/{post_id}/_/{comment_id}/" if post_id and comment_id else None,
                    'created_iso': comment_created_iso,
                    # 'body_orig': comment_body # Keep original body, but can be long
                }
                comment_doc_meta = {k: v for k, v in comment_doc_meta.items() if v is not None} # Clean None values


                # Analyze the comment text
                # Comments share the same context as the post, so global keywords apply.
                # Could potentially derive contextual keywords from the parent post's extracted entities?
                # For now, stick to global keywords.
                analysis_result_comment = self.product_mention_analyzer.analyze_text(
                    comment_body,
                    source_type='reddit_comment', # Pass explicit source type
                    meta=comment_doc_meta, # Pass comment-specific metadata
                    contextual_keywords=[] # No specific product context from the structure itself
                )
                 # Add the analysis result for the comment
                processed_reddit_items.append(analysis_result_comment)


        logger.info(f"Finished processing Reddit data. Generated {len(processed_reddit_items)} item analysis results (posts/comments).")
        return processed_reddit_items

    # --- New Method for Corpus-Level Feature Calculation (TF-IDF/LDA) ---
    def calculate_corpus_features(self, processed_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates corpus-level features (like TF-IDF or LDA topics) and adds them
        to the processed items.

        Args:
            processed_items: A flat list of dictionaries resulting from processing
                             Amazon and/or Reddit data.

        Returns:
            The same list of dictionaries, with TF-IDF vectors/scores and LDA topics added.
        """
        if not processed_items:
            logger.warning("No processed items available to calculate corpus features.")
            return processed_items

        logger.info(f"Calculating corpus features for {len(processed_items)} documents.")

        # Extract the cleaned text documents for corpus analysis
        # Use only items that have cleaned text
        corpus_docs = [(item.get('cleaned_text', ''), i) for i, item in enumerate(processed_items) if item.get('cleaned_text', '').strip()]
        if not corpus_docs:
            logger.warning("No documents with non-empty cleaned text found for corpus feature calculation.")
            # Add None placeholders to all items even if no calculation was done
            for item in processed_items:
                 item['tfidf_features'] = None
                 item['lda_topics'] = None
            return processed_items


        # Separate documents and their original indices
        texts_for_corpus = [doc[0] for doc in corpus_docs]
        original_indices = [doc[1] for doc in corpus_docs]

        # --- TF-IDF Calculation ---
        # You can adjust parameters like max_features, min_df, max_df, ngram_range
        # stopwords are already removed in TextCleaner, so don't pass stop_words here
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.95)
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts_for_corpus)
            self.tfidf_features_calculated = True
            logger.info(f"TF-IDF features calculated. Shape: {tfidf_matrix.shape}")

            # Add TF-IDF scores (or potentially just the vector) to each corresponding item
            # Storing the sparse vector directly in metadata might not be ideal for ChromaDB
            # A common approach is to get the top N TF-IDF terms per document or similar
            # For simplicity here, let's extract top terms and their scores, or just the vector (will need serialization for metadata)

            # Option 1: Store top N terms and scores (more human-readable, less information)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            for doc_idx, original_list_idx in enumerate(original_indices):
                 # Get features and scores for this document
                 feature_index = tfidf_matrix[doc_idx,:].nonzero()[1] # Get non-zero feature indices
                 tfidf_scores = zip(feature_index, [tfidf_matrix[doc_idx, x] for x in feature_index])

                 # Get top N terms by score
                 top_n = 10 # Or another number
                 # Sort by score descending, take top N
                 sorted_scores = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)[:top_n]

                 # Create a list of (term, score) tuples or just terms
                 # Storing as JSON string in metadata is usually required for complex objects
                 top_terms_with_scores = [(feature_names[i], round(score, 4)) for i, score in sorted_scores]
                 # Or just the terms: top_terms = [feature_names[i] for i, score in sorted_scores]

                 # Add to the original item dictionary
                 processed_items[original_list_idx]['tfidf_features'] = top_terms_with_scores
                 # processed_items[original_list_idx]['tfidf_vector'] = tfidf_matrix[doc_idx].todense().tolist()[0] # Store dense vector (large!) - probably not for metadata


        except Exception as e:
            logger.error(f"Error during TF-IDF calculation: {e}")
            self.tfidf_features_calculated = False
            # Ensure all items have None if calculation failed
            for item in processed_items:
                 item['tfidf_features'] = None


        # --- LDA Topic Modeling Calculation ---
        # LDA works best on raw counts, not TF-IDF, but TF-IDF output can be used
        # A better approach might be to use CountVectorizer here, or run LDA before TF-IDF
        # Let's use CountVectorizer specifically for LDA input
        from sklearn.feature_extraction.text import CountVectorizer
        count_vectorizer = CountVectorizer(max_features=tfidf_matrix.shape[1] if self.tfidf_features_calculated else 5000,
                                           min_df=5, max_df=0.95) # Match vocabulary size if TF-IDF was done
        try:
            count_matrix = count_vectorizer.fit_transform(texts_for_corpus)

            num_topics = 10 # You can tune the number of topics
            self.lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42, n_jobs=-1) # n_jobs=-1 uses all cores
            lda_topic_distributions = self.lda_model.fit_transform(count_matrix)
            self.lda_topics_calculated = True
            logger.info(f"LDA topics calculated. Shape: {lda_topic_distributions.shape}")

            # Assign the dominant topic and/or topic distribution to each document
            feature_names_cv = count_vectorizer.get_feature_names_out() # Vocabulary from CountVectorizer

            for doc_idx, original_list_idx in enumerate(original_indices):
                # Get topic distribution for this document
                topic_distribution = lda_topic_distributions[doc_idx]
                # Get the index of the dominant topic
                dominant_topic_index = int(np.argmax(topic_distribution)) # Ensure int type
                dominant_topic_probability = float(np.max(topic_distribution)) # Ensure float type

                # Optionally, get the top words for the dominant topic for context
                topic_top_words_indices = self.lda_model.components_[dominant_topic_index].argsort()[:-10-1:-1] # Top 10 words
                topic_top_words = [feature_names_cv[i] for i in topic_top_words_indices]

                # Store in the original item dictionary
                processed_items[original_list_idx]['lda_dominant_topic'] = dominant_topic_index
                processed_items[original_list_idx]['lda_dominant_topic_prob'] = dominant_topic_probability
                processed_items[original_list_idx]['lda_dominant_topic_words'] = topic_top_words # Top words of the dominant topic
                # processed_items[original_list_idx]['lda_topic_distribution'] = topic_distribution.tolist() # Store full distribution (can be large)

        except Exception as e:
             logger.error(f"Error during LDA calculation: {e}")
             self.lda_topics_calculated = False
             # Ensure all items have None if calculation failed
             for item in processed_items:
                 item['lda_dominant_topic'] = None
                 item['lda_dominant_topic_prob'] = None
                 item['lda_dominant_topic_words'] = None
                 # item['lda_topic_distribution'] = None


        logger.info("Corpus feature calculation complete.")
        return processed_items # Return the list with added features


    # --- Method to format processed data for ChromaDB ---
    def prepare_for_chromadb(
        self,
        processed_items: List[Dict[str, Any]] # Takes a flat list of analysis results
    ) -> Dict[str, List[Any]]:
        """
        Formats a list of processed analysis results into ChromaDB format.

        Args:
            processed_items: A flat list where each item is the dictionary
                             output of product_mention_analyzer.analyze_text,
                             potentially enriched with corpus features.

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

            # Get the unique ID for the document
            # This should have been created and stored in the 'meta' during processing
            doc_meta = analysis_result.get('meta', {})
            source_type = analysis_result.get('source_type', 'unknown') # Use source_type from analysis result
            # Use the unique ID stored in the meta dictionary during processing
            if source_type == 'amazon_review':
                chroma_id = doc_meta.get('review_id')
            elif source_type == 'reddit_post':
                chroma_id = doc_meta.get('post_id')
            elif source_type == 'reddit_comment':
                 chroma_id = doc_meta.get('comment_id')
            # Add other source types if needed
            else:
                 # Fallback ID if source_type is unknown or no specific ID found
                 chroma_id = f"item_{i}"
                 logger.warning(f"Could not determine unique ID for item {i} (source_type: {source_type}). Using fallback ID {chroma_id}.")


            if not chroma_id:
                 logger.warning(f"Skipping item {i} due to missing unique ID after processing.")
                 continue # Skip if ID is missing


            # Use the cleaned text as the document content for embedding
            chroma_doc = analysis_result.get('cleaned_text', '')

            # Skip if no text content to embed
            if not chroma_doc.strip():
                # This check is also in analyze_text, but double-checking here
                logger.debug(f"Skipping item {chroma_id} due to empty or whitespace-only cleaned text for ChromaDB.")
                continue


            # Prepare metadata for ChromaDB
            # Include analysis results and original metadata
            chroma_meta = {
                # Core analysis results
                'source_type': analysis_result.get('source_type'),
                'sentiment_label': analysis_result.get('sentiment_label'),
                'sentiment_compound_score': analysis_result.get('sentiment', {}).get('compound'), # Specific score
                # Note: sentiment pos/neu/neg scores can also be added if useful for filtering/metadata search
                'product_mentions': analysis_result.get('product_mentions', []), # List of strings
                'entities': analysis_result.get('entities', {}), # Dictionary of lists

                # Corpus features (will be None if not calculated)
                'tfidf_features': analysis_result.get('tfidf_features'), # Top terms/scores (list of tuples)
                'lda_dominant_topic': analysis_result.get('lda_dominant_topic'), # Dominant topic index (int)
                'lda_dominant_topic_prob': analysis_result.get('lda_dominant_topic_prob'), # Dominant topic probability (float)
                'lda_dominant_topic_words': analysis_result.get('lda_dominant_topic_words', []), # Top words of dominant topic (list of strings)
                # 'lda_topic_distribution': analysis_result.get('lda_topic_distribution'), # Full distribution (list of floats) - potentially large


                # Original metadata passed during analysis (flattened into the metadata dict)
                **doc_meta, # Includes original IDs, dates, authors, scores, URLs etc.
                 # Add original text for context if needed, but be mindful of size limits in metadata
                'original_text': analysis_result.get('original_text', ''), # Keep original text for display/context
            }

            # Clean None values and convert lists/dicts to JSON strings where necessary for ChromaDB
            # ChromaDB usually handles lists/dicts of primitive types well, but JSON string is safest for complex nesting
            final_chroma_meta = {}
            for k, v in chroma_meta.items():
                if v is not None:
                     if isinstance(v, (list, dict)):
                          # Convert non-empty lists/dicts to JSON strings
                          if v: # Only dump if not empty
                             try:
                                 final_chroma_meta[k] = json.dumps(v)
                             except TypeError:
                                 logger.warning(f"Could not JSON serialize metadata key '{k}' with value '{v}'. Skipping or storing as string if possible.")
                                 final_chroma_meta[k] = str(v) # Fallback to string representation
                          # else: empty list/dict is None, which we already filtered, or we store empty JSON like "{}" or "[]"
                          # Decide if you want empty lists/dicts stored as "{}" or "[]" vs skipping them (currently skipping via v is not None)
                     elif isinstance(v, (str, int, float, bool)):
                          final_chroma_meta[k] = v
                     else:
                          logger.warning(f"Metadata key '{k}' has unsupported type {type(v)}. Skipping or converting to string.")
                          final_chroma_meta[k] = str(v) # Fallback for other types

            chroma_ids.append(str(chroma_id)) # Ensure ID is a string
            chroma_documents.append(chroma_doc)
            chroma_metadatas.append(final_chroma_meta) # Use the cleaned metadata dict


        logger.info(f"Formatted {len(chroma_ids)} documents for ChromaDB.")
        # Note: If you were providing embeddings, you would add 'embeddings': [...] here
        return {'ids': chroma_ids, 'documents': chroma_documents, 'metadatas': chroma_metadatas}

    # Keep save_processed_data_to_csv as it is for saving the intermediate analysis results
    # and save_to_csv functionality seems fine.
    def save_processed_data_to_csv(self, processed_items: List[Dict[str, Any]], filename: str = "processed_analysis_results.csv"):
        """Saves the direct analysis results (one row per review/post/comment) to CSV."""
        if not processed_items:
            logger.warning("No processed items provided to save to CSV.")
            return
        try:
            # Flatten the data somewhat for CSV
            flat_data = []
            for item in processed_items:
                row = {
                    'source_type': item.get('source_type'),
                    'original_text': item.get('original_text'),
                    'cleaned_text': item.get('cleaned_text'),
                    'sentiment_label': item.get('sentiment_label'),
                    'sentiment_compound_score': item.get('sentiment', {}).get('compound'),
                    # Convert lists/dicts to strings for CSV columns
                    'product_mentions': json.dumps(item.get('product_mentions', [])),
                    'entities_json': json.dumps(item.get('entities', {})),
                    'tfidf_features_json': json.dumps(item.get('tfidf_features')), # Include TF-IDF
                    'lda_dominant_topic': item.get('lda_dominant_topic'), # Include LDA
                    'lda_dominant_topic_prob': item.get('lda_dominant_topic_prob'),
                    'lda_dominant_topic_words_json': json.dumps(item.get('lda_dominant_topic_words')),
                    **item.get('meta', {}) # Add all metadata fields (need to handle potential conflicts or complex types here)
                }
                # Simple flattening for nested meta dictionaries might be needed depending on complexity
                # For basic flat meta, this **item.get('meta', {}) works. For nested, need more logic.
                # Ensure no complex objects remain in the row before creating DataFrame
                cleaned_row = {}
                for k, v in row.items():
                     if isinstance(v, (list, dict)):
                          cleaned_row[k] = json.dumps(v) # Ensure lists/dicts are JSON strings
                     elif v is not None:
                          cleaned_row[k] = v
                     else:
                          cleaned_row[k] = None # Explicitly keep None if value was None

                flat_data.append(cleaned_row)

            df = pd.DataFrame(flat_data)

            # Handle potential columns with non-standard types that pandas might struggle with or need serialization
            # (Already attempted in cleaned_row creation, but double-check if errors occur)


            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")

            df.to_csv(filename, index=False, quoting=1) 
            logger.info(f"Saved {len(processed_items)} analysis results to {filename}")
        except Exception as e:
            logger.error(f"Failed to save processed data to CSV {filename}: {e}")
