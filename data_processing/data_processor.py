import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import pandas as pd
import logging
import os, json
from product_mention_analyzer import ProductMentionAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_processor')
# Helper Function for Timestamp Conversion (ensure this is accessible)
def safe_utc_isoformat(timestamp_str_or_float: Optional[Any]) -> Optional[str]:
    """Safely converts UTC timestamp string or float to ISO 8601 string."""
    if timestamp_str_or_float is None: return None
    try:
        if isinstance(timestamp_str_or_float, str):
             try: dt_naive = datetime.strptime(timestamp_str_or_float, '%Y-%m-%d %H:%M:%S'); dt_aware = dt_naive.replace(tzinfo=timezone.utc); return dt_aware.isoformat()
             except ValueError: return datetime.fromisoformat(timestamp_str_or_float.replace('Z', '+00:00')).isoformat()
        elif isinstance(timestamp_str_or_float, (int, float)): return datetime.fromtimestamp(timestamp_str_or_float, timezone.utc).isoformat()
    except Exception as e: logger.warning(f"Could not parse timestamp '{timestamp_str_or_float}': {e}")
    return None


def parse_price(price_str: Optional[str]) -> Optional[float]:
    if not price_str or not isinstance(price_str, str): return None
    try:
        cleaned_price = re.sub(r'[$\sEUR€£]', '', price_str).strip().replace(',', '.')
        if '.' in cleaned_price: parts = cleaned_price.split('.'); cleaned_price = "".join(parts[:-1]) + "." + parts[-1] if len(parts) > 2 else cleaned_price
        return float(cleaned_price)
    except ValueError: logger.warning(f"Could not parse price: {price_str}"); return None

def parse_rating(rating_str: Optional[str]) -> Optional[float]:
    if not rating_str or not isinstance(rating_str, str) or rating_str.strip().upper() == 'N/A': return None
    try:
        match = re.match(r'(\d+(\.\d+)?)', rating_str); return float(match.group(1)) if match else float(rating_str.strip())
    except ValueError: logger.warning(f"Could not parse rating: {rating_str}"); return None

def parse_review_count(rc_str: Optional[str]) -> Optional[int]:
    if not rc_str or not isinstance(rc_str, str) or rc_str.strip().upper() == 'N/A': return None
    try:
        match = re.search(r'\d+', rc_str); return int(match.group(0)) if match else int(rc_str.strip())
    except ValueError: logger.warning(f"Could not parse review count: {rc_str}"); return None
    
    
class DataProcessor:
    """Main class for processing data from different sources."""
    def __init__(self, product_keywords: List[str] = None):
        self.product_keywords = product_keywords or []
        # Initialize the core analyzer
        self.product_mention_analyzer = ProductMentionAnalyzer(self.product_keywords)
        logger.info(f"DataProcessor initialized with {len(self.product_keywords)} product keywords.")

    # --- Keep existing process_twitter_data if needed ---
    # ... (process_twitter_data method here) ...

    # --- Method to process Amazon data (adapted for your format) ---
    def process_amazon_json(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes Amazon product data including reviews.
        Input: List of product dictionaries, each containing a 'reviews' list.
        Output: List of analysis result dictionaries, one per review.
        """
        processed_reviews = []
        logger.info(f"Starting processing of {len(data)} Amazon product items.")
        for i, item in enumerate(data):
            if not isinstance(item, dict): continue
            logger.debug(f"Processing Amazon item {i+1}/{len(data)} - URL: {item.get('URL', 'N/A')}")

            product_url = item.get('URL', '')
            product_title = item.get('Title', '').strip()
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
            product_asin = asin_match.group(1) if asin_match else None

            product_meta = {
                'source': 'amazon', 'product_url': product_url, 'product_title': product_title,
                'product_asin': product_asin, 'product_price': parse_price(item.get('Price')),
                'product_rating_overall': parse_rating(item.get('Rating')),
                'product_review_count': parse_review_count(item.get('Review Count')),
            }
            product_meta = {k: v for k, v in product_meta.items() if v is not None}

            reviews = item.get('reviews', [])
            if not isinstance(reviews, list): reviews = []

            if not reviews: logger.debug(f"No reviews for Amazon item: {product_title or product_url}"); continue

            for r_idx, review in enumerate(reviews):
                if not isinstance(review, dict): continue

                review_title = review.get('title', '').strip()
                review_comment = review.get('comment', '').strip()
                review_rating_from_title = parse_rating(review_title)
                text_to_process = f"{review_title}. {review_comment}".strip()
                if not text_to_process: continue

                review_date_str = review.get('date', '').replace('Reviewed in the United States on', '').strip()
                review_iso_date = None
                try: review_iso_date = datetime.strptime(review_date_str, '%B %d, %Y').replace(tzinfo=timezone.utc).isoformat()
                except ValueError: logger.debug(f"Could not parse review date format: {review_date_str}")

                # Use ASIN + index as a unique part for review ID
                review_unique_part = f"{product_asin}_{r_idx}" if product_asin else f"{product_title[:20].replace(' ','_')}_{r_idx}"

                review_meta = {
                    **product_meta,
                    'source_type': 'amazon_review',
                    'review_id': f"amazon_{review_unique_part}", # Construct review ID
                    'review_title': review_title,
                    'review_rating': review_rating_from_title,
                    'review_created_iso': review_iso_date,
                }
                review_meta = {k: v for k, v in review_meta.items() if v is not None}

                # Analyze the combined title and comment
                analysis_result = self.product_mention_analyzer.analyze_text(
                    text_to_process,
                    source='amazon_review',
                    meta=review_meta
                )

                # Ensure product title is mentioned
                if product_title and product_title not in analysis_result['product_mentions']:
                    analysis_result['product_mentions'].insert(0, product_title)

                processed_reviews.append(analysis_result) # Add analysis result for this review

        logger.info(f"Finished processing. Extracted {len(processed_reviews)} Amazon reviews for analysis.")
        return processed_reviews

    # --- NEW: Method to process list of Reddit Threads ---
    def process_reddit_thread_list(self, thread_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a list of Reddit threads (post + comments).
        Input: List of thread dictionaries.
        Output: List of analysis result dictionaries, one per post/comment.
        """
        processed_reddit_items = []
        logger.info(f"Starting processing of {len(thread_list)} Reddit threads.")

        for i, thread_data in enumerate(thread_list):
             if not isinstance(thread_data, dict): continue
             post_id = thread_data.get('id')
             logger.debug(f"Processing Reddit thread {i+1}/{len(thread_list)} - ID: {post_id}")

             # 1. Process Post
             post_text = thread_data.get('selftext', '').strip().replace('\n', ' ')
             post_title = thread_data.get('title', '').strip().replace('\n', ' ')
             text_to_analyze = post_text if post_text else post_title
             if text_to_analyze:
                 post_meta = {
                    'source_type': 'reddit_post', 'post_id': post_id, 'author': thread_data.get('author'),
                    'title': post_title, 'score': thread_data.get('score'), 'url': thread_data.get('url'),
                    'permalink': f"https://www.reddit.com/comments/{post_id}/" if post_id else thread_data.get('url'),
                    'num_comments': thread_data.get('num_comments'), 'subreddit': thread_data.get('subreddit'),
                    'created_iso': safe_utc_isoformat(thread_data.get('created_utc')),
                 }
                 post_meta = {k: v for k, v in post_meta.items() if v is not None}
                 analysis_result = self.product_mention_analyzer.analyze_text(text_to_analyze, source='reddit_post', meta=post_meta)
                 processed_reddit_items.append(analysis_result)

             # 2. Process Comments
             comments = thread_data.get('comments', [])
             if not isinstance(comments, list): comments = []
             for comment in comments:
                 if not isinstance(comment, dict): continue
                 comment_id = comment.get('comment_id')
                 comment_body = comment.get('body', '').strip().replace('\n', ' ')
                 if not comment_id or not comment_body: continue

                 comment_meta = {
                    'source_type': 'reddit_comment', 'comment_id': comment_id, 'post_id': post_id,
                    'author': comment.get('author'), 'score': comment.get('score'),
                    'parent_id': comment.get('parent_id'), 'subreddit': thread_data.get('subreddit'),
                    'permalink': f"https://www.reddit.com/comments/{post_id}/_/{comment_id}/",
                    'created_iso': safe_utc_isoformat(comment.get('created_utc')),
                 }
                 comment_meta = {k: v for k, v in comment_meta.items() if v is not None}
                 analysis_result = self.product_mention_analyzer.analyze_text(comment_body, source='reddit_comment', meta=comment_meta)
                 processed_reddit_items.append(analysis_result)

        logger.info(f"Finished processing Reddit threads. Generated {len(processed_reddit_items)} items (posts/comments).")
        return processed_reddit_items


    # --- NEW: Method to format processed data for ChromaDB ---
    def prepare_for_chromadb(
        self,
        processed_items: List[Dict[str, Any]] # Takes a flat list of analysis results
    ) -> Dict[str, List[Any]]:
        """
        Formats a list of processed analysis results into ChromaDB format.

        Args:
            processed_items: A flat list where each item is the dictionary
                             output of product_mention_analyzer.analyze_text.

        Returns:
            A dictionary {'ids': [], 'documents': [], 'metadatas': []} ready for ChromaDB.
        """
        chroma_ids = []
        chroma_documents = []
        chroma_metadatas = []
        logger.info(f"Preparing {len(processed_items)} processed items for ChromaDB format.")

        for i, analysis_result in enumerate(processed_items):
            if not isinstance(analysis_result, dict):
                 logger.warning(f"Skipping item {i} as it's not a dictionary.")
                 continue

            meta = analysis_result.get('meta', {})
            source_type = analysis_result.get('source', 'unknown') # e.g., 'amazon_review', 'reddit_post'

            # Determine a unique ID based on source type
            unique_id_part = "item_" + str(i) # Default fallback ID
            if source_type == 'amazon_review':
                unique_id_part = meta.get('review_id', unique_id_part)
            elif source_type == 'reddit_post':
                unique_id_part = meta.get('post_id', unique_id_part)
            elif source_type == 'reddit_comment':
                unique_id_part = meta.get('comment_id', unique_id_part)
            elif source_type == 'twitter_tweet': # Assuming twitter processing exists
                unique_id_part = meta.get('tweet_id', meta.get('id', unique_id_part))
            # Add more source types if needed

            chroma_id = f"{source_type}_{unique_id_part}"
            chroma_doc = analysis_result.get('cleaned_text', '') # Use cleaned text for embedding

            # Skip if no text content to embed
            if not chroma_doc:
                 logger.debug(f"Skipping item {chroma_id} due to empty cleaned text.")
                 continue

            # Prepare metadata for ChromaDB
            chroma_meta = {
                **meta, # Include all original metadata passed to analyze_text
                'original_text': analysis_result.get('original_text', ''),
                'sentiment_label': analysis_result.get('sentiment_label'),
                'sentiment_score': analysis_result.get('sentiment', {}).get('compound'),
                'product_mentions': analysis_result.get('product_mentions', []),
                 # Store entities as JSON string for better compatibility if needed
                'entities_json': json.dumps(analysis_result.get('entities', {}))
            }
            # Ensure metadata values are Chroma-compatible types (str, int, float, bool)
            # Convert lists/dicts to JSON strings if necessary, or rely on ChromaDB handling
            chroma_meta = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                           for k, v in chroma_meta.items() if v is not None}


            chroma_ids.append(chroma_id)
            chroma_documents.append(chroma_doc)
            chroma_metadatas.append(chroma_meta)

        logger.info(f"Formatted {len(chroma_ids)} documents for ChromaDB.")
        return {'ids': chroma_ids, 'documents': chroma_documents, 'metadatas': chroma_metadatas}

    # --- Optional: Keep or adapt save_to_csv ---
    def save_processed_data_to_csv(self, processed_items: List[Dict[str, Any]], filename: str = "processed_analysis_results.csv"):
        """Saves the direct analysis results (one row per review/post/comment) to CSV."""
        if not processed_items:
            logger.warning("No processed items provided to save.")
            return
        try:
            # Flatten the data somewhat for CSV
            flat_data = []
            for item in processed_items:
                 row = {
                     'source': item.get('source'),
                     'original_text': item.get('original_text'),
                     'cleaned_text': item.get('cleaned_text'),
                     'sentiment_label': item.get('sentiment_label'),
                     'sentiment_score': item.get('sentiment', {}).get('compound'),
                     'product_mentions': ", ".join(item.get('product_mentions', [])), # Comma-separated
                     'entities_json': json.dumps(item.get('entities', {})),
                     **item.get('meta', {}) # Add all metadata fields
                 }
                 flat_data.append(row)

            df = pd.DataFrame(flat_data)
            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                 os.makedirs(output_dir)
                 logger.info(f"Created output directory: {output_dir}")

            df.to_csv(filename, index=False, quoting=1)
            logger.info(f"Saved {len(processed_items)} analysis results to {filename}")
        except Exception as e:
            logger.error(f"Failed to save processed data to CSV {filename}: {e}")
