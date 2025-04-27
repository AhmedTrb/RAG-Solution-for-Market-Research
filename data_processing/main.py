import logging
import nltk
from data_processor import DataProcessor 
import json
import os
import pandas as pd

# Set up logging (can be more sophisticated in a real app)
logging.basicConfig(
    level=logging.INFO, # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('main_pipeline') # Use a specific logger name

# Download required NLTK data (should be done once)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    logger.info("NLTK data (punkt, stopwords) checked/downloaded.")
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {e}. Some features may not work properly.")


# --- Configuration ---
JSON_DIRECTORY = "./data/" # Directory where your JSON files are located
AMAZON_JSON_FILENAMES = [
    "all_products_eufyCam_2C_Pro.json",
    "all_products_eufyCam_2C.json",
    "all_products_Google_Nest_Cam_(Wired).json",
    "all_products_Google_Nest_Cam_with_Floodlight.json",
    "all_products_Ring_Pan-Tilt_Indoor_Cam.json",
]
REDDIT_JSON_FILENAME = "homesecurity_top_10posts.json"

# Define global product keywords relevant to your domain
# These help the EntityExtractor identify mentions even without specific product context
GLOBAL_PRODUCT_KEYWORDS = [
    "Home Security", "Smart Home", "Nest cam", "Wyze", "Ring",
    "eufyCam", "Arlo", "ADT", "Simplisafe", 
    "security camera", "alarm system", "motion detection", "night vision",
    "wireless camera", "video doorbell", "smart lock" 
]

OUTPUT_DIR = "processed_output"
PROCESSED_CSV_FILENAME = os.path.join(OUTPUT_DIR, "analysis_results_combined.csv")
CHROMA_PREPARED_CSV_FILENAME = os.path.join(OUTPUT_DIR, "chroma_prepared_final.csv")

# --- Main Execution Logic ---
if __name__ == "__main__":
    logger.info("Starting main data processing pipeline.")

    # 1. Load Amazon Data from multiple files
    all_amazon_product_data = []
    total_loaded_count = 0
    files_processed_count = 0
    files_failed_count = 0

    logger.info(f"Loading Amazon data from {len(AMAZON_JSON_FILENAMES)} files in '{JSON_DIRECTORY}'.")
    for filename in AMAZON_JSON_FILENAMES:
        file_path = os.path.join(JSON_DIRECTORY, filename)
        logger.debug(f"Attempting to load file: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_data = json.load(f)

            product_list_from_file = file_data.get("amazon", [])

            if isinstance(product_list_from_file, list):
                all_amazon_product_data.extend(product_list_from_file)
                loaded_in_this_file = len(product_list_from_file)
                total_loaded_count += loaded_in_this_file
                logger.info(f"Successfully loaded {loaded_in_this_file} product items from {filename}.")
                files_processed_count += 1
            else:
                logger.warning(f"Expected a list under 'amazon' key in {filename}, but found type {type(product_list_from_file)}. Skipping file.")
                files_failed_count += 1

        except FileNotFoundError:
            logger.error(f"Amazon JSON file not found: {file_path}. Skipping.")
            files_failed_count += 1
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON file {file_path}: {e}. Skipping.")
            files_failed_count += 1
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing {file_path}: {e}. Skipping.")
            files_failed_count += 1

    logger.info(f"Finished loading Amazon data. Processed {files_processed_count} files, failed {files_failed_count}.")
    logger.info(f"Total Amazon product items loaded: {total_loaded_count}")

    # 2. Load Reddit Data
    reddit_thread_list = []
    reddit_file_path = os.path.join(JSON_DIRECTORY, REDDIT_JSON_FILENAME)
    logger.info(f"Loading Reddit data from '{reddit_file_path}'.")
    try:
        with open(reddit_file_path, "r", encoding="utf-8") as f:
            reddit_thread_list = json.load(f)
        if not isinstance(reddit_thread_list, list):
            logger.warning("Reddit JSON does not contain a list. Expected a list of threads.")
            reddit_thread_list = [] # Ensure it's a list even if loading failed partially
        logger.info(f"Loaded {len(reddit_thread_list)} threads from Reddit JSON.")
    except FileNotFoundError:
        logger.error(f"Reddit JSON file not found: {reddit_file_path}. Please provide the correct path.")
        reddit_thread_list = []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding Reddit JSON file {reddit_file_path}: {e}.")
        reddit_thread_list = []
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading {reddit_file_path}: {e}.")
        reddit_thread_list = []


    # 3. Instantiate the DataProcessor
    # Pass global keywords that are generally relevant to the domain (home security, smart home)
    processor = DataProcessor(global_product_keywords=GLOBAL_PRODUCT_KEYWORDS)

    # 4. Process Amazon Data -> Returns list of analysis results per review
    # The processor handles linking product meta and passing product title as contextual keyword internally now
    processed_amazon_reviews = processor.process_amazon_json(all_amazon_product_data)
    logger.info(f"Analysis complete for {len(processed_amazon_reviews)} Amazon reviews.")


    # 5. Process Reddit Data -> Returns list of analysis results per post/comment
    processed_reddit_items = processor.process_reddit_thread_list(reddit_thread_list)
    logger.info(f"Analysis complete for {len(processed_reddit_items)} Reddit posts and comments.")

    # 6. Combine processed items from all sources
    all_processed_items = processed_amazon_reviews + processed_reddit_items
    # Add processed twitter items here if you implement twitter processing
    logger.info(f"Total processed text items (reviews, posts, comments): {len(all_processed_items)}")

    # 7. Calculate Corpus-Level Features (TF-IDF, LDA)
    # This method modifies the items in all_processed_items in place
    all_processed_items = processor.calculate_corpus_features(all_processed_items)
    logger.info("Corpus feature calculation finished.")


    # 8. Prepare the combined data for ChromaDB
    # This method uses the updated items (including corpus features)
    chroma_ready_data = processor.prepare_for_chromadb(all_processed_items)
    logger.info(f"Prepared {len(chroma_ready_data.get('ids', []))} items for ChromaDB ingestion.")


    # 9. Optional: Save the intermediate analysis results to CSV
    # This saves the data structure *before* formatting strictly for ChromaDB
    if all_processed_items:
         processor.save_processed_data_to_csv(all_processed_items, filename=PROCESSED_CSV_FILENAME)
    else:
         logger.warning("No processed items to save to analysis results CSV.")

    # 10. Optional: Save the ChromaDB-ready data to CSV for inspection
    # This saves the {'ids': [], 'documents': [], 'metadatas': []} structure
    if chroma_ready_data.get('ids'):
        try:
            # Use pandas json_normalize to flatten metadata into columns
            # Handle cases where metadata might be missing keys across different items
            meta_df = pd.json_normalize(chroma_ready_data['metadatas'], sep='_')

            # Create the final DataFrame
            df_chroma = pd.DataFrame({
                'chroma_id': chroma_ready_data['ids'],
                'document_text': chroma_ready_data['documents'],
            })
            # Concatenate the normalized metadata DataFrame, aligning by index
            df_chroma = pd.concat([df_chroma, meta_df], axis=1)

            # Ensure output directory exists
            output_dir = os.path.dirname(CHROMA_PREPARED_CSV_FILENAME)
            if output_dir and not os.path.exists(output_dir):
               os.makedirs(output_dir)
               logger.info(f"Created output directory: {output_dir}")

            df_chroma.to_csv(CHROMA_PREPARED_CSV_FILENAME, index=False, quoting=1)
            logger.info(f"Saved ChromaDB formatted data to {CHROMA_PREPARED_CSV_FILENAME}")
        except Exception as e:
            logger.error(f"Failed to save ChromaDB formatted data to CSV {CHROMA_PREPARED_CSV_FILENAME}: {e}")
            logger.warning("Saving raw processed items to CSV as a fallback.")
            if all_processed_items:
                 processor.save_processed_data_to_csv(all_processed_items, filename=PROCESSED_CSV_FILENAME) # Fallback save


    else:
        logger.warning("No data was prepared for ChromaDB.")

    logger.info("Main pipeline execution finished.")