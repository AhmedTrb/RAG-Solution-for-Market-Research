import logging
import json
import re
from typing import List, Dict, Any

# Import modules from the local package
import config
from RAG_components import initialize_rag_components
from retrieval_methods import RetrievalMethods
from prompt_formatter import RAG_PROMPT_TEMPLATE, format_chroma_results_for_prompt

# LangChain Imports for the chain structure
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Main Execution ---
if __name__ == "__main__":
    try:
        # Initialize RAG components (Chroma collection, LLM)
        # This function handles loading env vars and setting up clients
        chroma_collection, rag_llm = initialize_rag_components()
    except ValueError as e:
        logger.error(f"Initialization failed: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during initialization: {e}")
        exit(1)

    # Instantiate RetrievalMethods class with the initialized collection and k
    retriever_methods = RetrievalMethods(chroma_collection, k=config.RETRIEVER_K)

    # Define the sample query for testing
    sample_query = "Analyze user feedback regarding the Arlo Essential Security Camera, focusing on battery life and video quality."

    # Get the list of supported retrieval methods from config
    retrieval_methods_to_test = config.SUPPORTED_RETRIEVAL_METHODS

    print(f"\n--- Testing RAG with Different Retrieval Methods ---")
    print(f"Query: {sample_query}")
    print("-" * 50)

    # Dictionary to store results from each method (optional, for later analysis)
    all_results = {}

    # --- RAG Chain Setup (using the initialized LLM and Prompt) ---
    # The chain defines the flow: context and question -> prompt -> LLM -> output parser
    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    rag_chain = (
        # Pass the context and question directly to the prompt
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
        | rag_prompt # Apply the prompt template
        | rag_llm # Invoke the LLM
        | StrOutputParser() # Parse the LLM output as a string
    )
    logger.info("RAG chain structure built.")


    # --- Loop through each retrieval method and run the RAG pipeline ---
    for method_name in retrieval_methods_to_test:
        print(f"\n>>> Running with Retrieval Method: {method_name} <<<")
        # Initialize empty results for the current method
        retrieved_docs_chroma_format = {"ids": [], "documents": [], "metadatas": []}

        try:
            # --- Perform Retrieval using the selected method ---
            # The retrieve method handles calling the specific ChromaDB query logic
            retrieved_docs_chroma_format = retriever_methods.retrieve(sample_query, method_name)

            # Check if any documents were retrieved
            if not retrieved_docs_chroma_format.get('ids'):
                logger.warning(f"No documents retrieved for method '{method_name}'. Skipping RAG.")
                # Create a placeholder report indicating no context was found
                report_data = {
                    "report": "No relevant context found in the database for this query.",
                    "retrieval_method_used": method_name,
                    "retrieved_document_count": 0,
                }
                print("\n--- Generated Report ---")
                print(json.dumps(report_data, indent=2))
                print("\n--- Retrieved Documents (Raw) ---")
                print(json.dumps(retrieved_docs_chroma_format, indent=2))
                print("-" * 50)
                continue # Move to the next retrieval method

            # --- Format Retrieved Documents into Context String ---
            # Use the helper function to create the context string for the LLM
            formatted_context = format_chroma_results_for_prompt(retrieved_docs_chroma_format)

            # Check if the formatted context is empty (e.g., if documents had no text)
            if not formatted_context.strip():
                 logger.warning(f"Formatted context is empty for method '{method_name}'. Skipping RAG.")
                 # Create a placeholder report indicating empty context
                 report_data = {
                     "report": "Relevant documents were retrieved, but their content was empty after formatting. Cannot generate report.",
                     "retrieval_method_used": method_name,
                     "retrieved_document_count": len(retrieved_docs_chroma_format.get('ids', [])),
                 }
                 print("\n--- Generated Report ---")
                 print(json.dumps(report_data, indent=2))
                 print("\n--- Retrieved Documents (Raw) ---")
                 print(json.dumps(retrieved_docs_chroma_format, indent=2))
                 print("-" * 50)
                 continue

            # --- Invoke RAG Chain ---
            # Pass the formatted context and the original query to the RAG chain
            logger.info(f"Invoking RAG chain for method '{method_name}'...")
            llm_output_string = rag_chain.invoke({"context": formatted_context, "question": sample_query})

            # --- Parse LLM Output (Expected JSON) ---
            report_data = {}
            # Use regex to find the JSON object within the LLM's string output
            json_match = re.search(r'\{.*\}', llm_output_string, re.DOTALL)
            if json_match:
                try:
                    # Parse the extracted JSON string
                    report_data = json.loads(json_match.group(0))
                    # Add metadata about the retrieval method and document count to the report
                    report_data["retrieval_method_used"] = method_name
                    report_data["retrieved_document_count"] = len(retrieved_docs_chroma_format.get('ids', []))
                except json.JSONDecodeError as e:
                    # Handle JSON parsing errors
                    logger.error(f"Failed to parse LLM output as JSON for method '{method_name}': {e}")
                    report_data = {"error": "Failed to parse LLM output JSON", "raw_output": llm_output_string, "retrieval_method_used": method_name}
            else:
                # Handle cases where no JSON object was found in the output
                logger.error(f"LLM output did not contain JSON for method '{method_name}'.")
                report_data = {"error": "LLM output did not contain JSON", "raw_output": llm_output_string, "retrieval_method_used": method_name}

            # Store the results (optional)
            all_results[method_name] = report_data

            # --- Print Results for this Method ---
            print("\n--- Generated Report ---")
            # Print the generated report JSON with indentation
            print(json.dumps(report_data, indent=2))

            # Optional: Uncomment the lines below to print the raw retrieved documents for each method
            # print("\n--- Retrieved Documents (Raw) ---")
            # print(json.dumps(retrieved_docs_chroma_format, indent=2))

            print("-" * 50) # Separator for clarity between methods

        except Exception as e:
            # Catch and log any unexpected errors during the process for a specific method
            logger.error(f"An error occurred for method '{method_name}': {e}", exc_info=True)
            report_data = {"error": f"Processing failed for method {method_name}: {e}", "retrieval_method_used": method_name}
            all_results[method_name] = report_data
            print(f"\n--- Error for Method: {method_name} ---")
            print(json.dumps(report_data, indent=2))
            print("-" * 50)


    print("\n--- All Retrieval Methods Tested ---")
    # Optional: Save all_results to a JSON file for later analysis.
    with open("rag_comparison_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
        logger.info("Saved comparison results to rag_comparison_results.json")

    print("\nManual Review:")
    print("Review the generated reports for each method to compare the output.")
