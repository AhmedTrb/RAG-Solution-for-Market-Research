import logging
import nltk
from data_processor import DataProcessor
import json
import os
import pandas as pd
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_processor')

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    logger.warning("Failed to download NLTK data. Some features may not work properly.")


# Example usage
if __name__ == "__main__":
    
    # # 1. Load your sample JSON data
    # with open("all_products_Lenovo.json", "r", encoding="utf-8") as f:
    #     all_data = json.load(f)   # Expecting a list of product dicts

    # # 2. Load reddit JSON data
    # with open("homesecurity_top_10posts.json", "r", encoding="utf-8") as f:
    #     reddit_data = json.load(f)  # Expecting a list of reddit posts
        
    # amazon_data = all_data["amazon"]
    
    # # 3. Instantiate the processor (you can pass any product keywords you like)
    # product_keywords = [item.get("Title", "").split()[0] for item in amazon_data]
    # processor = DataProcessor(product_keywords=product_keywords)

    # # 4. Process the Amazon JSON
    # processed_reviews = processor.process_amazon_json(amazon_data)
    # logger.info(f"Processed {len(processed_reviews)} Amazon reviews.")

    # # 5. Process the Reddit data
    # processed_reddit_data = processor.process_reddit_data(reddit_data)
    # logger.info(f"Processed {len(processed_reddit_data)} Reddit posts and comments.")
    
    # # Optionally, save to CSV
    # processor.save_to_csv({"ecommerce": processed_reviews}, output_dir="poc_output")
    
    
    
    logger.info("Starting data processing for ChromaDB preparation...")

    # --- Define the list of JSON filenames to load ---
    # Replace this with your actual list of filenames
    amazon_json_filenames = [
        "all_products_eufyCam_2C_Pro.json",
        "all_products_eufyCam_2C.json",
        "all_products_Google_Nest_Cam_(Wired).json",
        "all_products_Google_Nest_Cam_with_Floodlight.json",
        "all_products_Ring_Pan-Tilt_Indoor_Cam.json",        
    ]
    json_directory = "."
    # --- Initialize an empty list to accumulate data from all files ---
    amazon_data = []
    total_loaded_count = 0
    files_processed_count = 0
    files_failed_count = 0
    for filename in amazon_json_filenames:
        # Construct the full path to the file
        file_path = os.path.join(json_directory, filename)
        logger.debug(f"Attempting to load file: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Load the entire JSON structure from the file
                file_data = json.load(f)

                # Expecting structure like: {"amazon": [list_of_products]}
                # Use .get() for safety in case the 'amazon' key is missing
                product_list_from_file = file_data.get("amazon", [])

                # Ensure the extracted data is actually a list before extending
                if isinstance(product_list_from_file, list):
                    amazon_data.extend(product_list_from_file)
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


    # --- Log summary ---
    logger.info(f"Finished loading Amazon data.")
    logger.info(f"Processed {files_processed_count} files successfully.")
    if files_failed_count > 0:
        logger.warning(f"Failed to process {files_failed_count} files.")
    logger.info(f"Total Amazon product items loaded: {total_loaded_count}")

    # 2. Load Reddit JSON data
    try:
        with open("homesecurity_top_10posts.json", "r", encoding="utf-8") as f:
            # Assuming this file contains a LIST of Reddit thread dictionaries
            reddit_thread_list = json.load(f)
            if not isinstance(reddit_thread_list, list):
                 logger.warning("Reddit JSON does not contain a list. Adjust loading if needed.")
                 reddit_thread_list = []
            logger.info(f"Loaded {len(reddit_thread_list)} threads from Reddit JSON.")
    except FileNotFoundError:
        logger.error("Reddit JSON file not found. Please provide the correct path.")
        reddit_thread_list = []
    except json.JSONDecodeError:
         logger.error("Error decoding Reddit JSON file.")
         reddit_thread_list = []


    # 3. Instantiate the processor
    # Extract keywords dynamically or use a predefined list
    # Using keywords from Amazon titles might be noisy, consider a fixed list.
    # product_keywords = list(set([item.get("Title", "").split()[0] for item in amazon_data if item.get("Title")]))
    product_keywords = ["Home Security","Smart Home","Nest cam","Wyze","Ring"] # Example fixed list
    processor = DataProcessor(product_keywords=product_keywords)

    # 4. Process Amazon Data -> Returns list of analysis results per review
    processed_amazon_reviews = processor.process_amazon_json(amazon_data)

    # 5. Process Reddit Data -> Returns list of analysis results per post/comment
    processed_reddit_items = processor.process_reddit_thread_list(reddit_thread_list)

    # 6. Combine processed items from all sources
    all_processed_items = processed_amazon_reviews + processed_reddit_items
    # Add processed twitter items here if you implement twitter processing
    logger.info(f"Total processed text items (reviews, posts, comments): {len(all_processed_items)}")


    # 7. Prepare the combined data for ChromaDB
    chroma_ready_data = processor.prepare_for_chromadb(all_processed_items)

    # 8. Optional: Save the ChromaDB-ready data for inspection
    if chroma_ready_data['ids']:
         output_file = "output_data_processed/chroma_prepared_final.csv"
         # Reusing the save method, but adapting it slightly if needed or writing a new one
         # Example: Saving the direct ChromaDB formatted data (requires DataFrame handling)
         try:
             df_chroma = pd.DataFrame({
                 'chroma_id': chroma_ready_data['ids'],
                 'document_text': chroma_ready_data['documents'],
                 # Normalize metadata into columns for better CSV readability
                 **pd.json_normalize([meta for meta in chroma_ready_data['metadatas']]).to_dict(orient='list')
             })
             output_dir = os.path.dirname(output_file)
             if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
             df_chroma.to_csv(output_file, index=False, quoting=1)
             logger.info(f"Saved ChromaDB formatted data to {output_file}")
         except Exception as e:
              logger.error(f"Failed to save ChromaDB formatted data to CSV: {e}")
              # Fallback to saving the raw analysis list if preferred
              # processor.save_processed_data_to_csv(all_processed_items, filename="output_data_processed/analysis_results_combined.csv")

    else:
         logger.warning("No data was prepared for ChromaDB.")


    # --- Next Steps (Conceptual - where you'd use chroma_ready_data) ---
    # 1. Initialize ChromaDB client & collection
    # 2. Generate embeddings for chroma_ready_data['documents']
    # 3. Add to ChromaDB: collection.add(ids=..., documents=..., metadatas=..., embeddings=...)
    logger.info("Data processing complete. Output is ready for embedding and ChromaDB ingestion.")