import logging
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import configuration and RAG components from your predefined files
try:
    import config 
    from RAG.RAG_components import initialize_rag_components
    from RAG.retrieval_methods import RetrievalMethods
    from RAG.prompt_formatter import RAG_PROMPT_TEMPLATE, format_chroma_results_for_prompt
except ImportError as e:
    logging.error(f"Failed to import RAG components. Ensure they are in a valid Python package: {e}")
    # Exit or handle appropriately if core components cannot be imported
    exit(1)


# LangChain Imports for the chain structure
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


# --- Basic Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Global/Cached RAG Components ---
# Initialize these once when the app starts
chroma_collection = None
rag_llm = None
rag_chain = None
retriever_methods = None # Instance of RetrievalMethods class


def initialize_rag_components_app():
    """Initializes the expensive RAG components for the Flask app."""
    global chroma_collection, rag_llm, rag_chain, retriever_methods

    if rag_chain is not None:
        logger.info("RAG components already initialized.")
        return

    logger.info("Initializing RAG components for app...")

    # Use the function from rag_experiment.rag_components
    chroma_collection, rag_llm = initialize_rag_components()

    # Instantiate RetrievalMethods class
    retriever_methods = RetrievalMethods(chroma_collection, k=config.RETRIEVER_K)
    logger.info("RetrievalMethods instance created.")

    # --- RAG Chain Setup ---
    # Build the RAG chain structure using the initialized LLM and Prompt Template
    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    rag_chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
        | rag_prompt
        | rag_llm
        | StrOutputParser()
    )
    logger.info("RAG chain structure built.")


# --- API Endpoint ---

@app.route('/api/research', methods=['POST'])
def generate_research_report():
    """
    Endpoint to generate a market research report using RAG.
    Accepts query and optional retrieval_method in the request body.
    """
    # Ensure RAG components are initialized before processing requests
    if rag_chain is None or retriever_methods is None:
        logger.error("RAG components not initialized.")
        # Attempt initialization, but likely indicates a startup issue
        try:
            initialize_rag_components_app()
            if rag_chain is None or retriever_methods is None:
                 return jsonify({"error": "Research service is not available (initialization failed)."}), 503 # Service Unavailable
        except Exception as e:
             logger.error(f"Failed to re-initialize components on request: {e}")
             return jsonify({"error": "Research service is not available (re-initialization failed)."}), 503


    data = request.get_json()
    query = data.get('query')
    # Get retrieval method from request, default to similarity
    retrieval_method = data.get('retrieval_method', 'similarity')

    if not query or not isinstance(query, str):
        return jsonify({"error": "Missing or invalid 'query' parameter"}), 400

    if retrieval_method not in retriever_methods.get_supported_methods():
         return jsonify({"error": f"Invalid retrieval_method. Supported methods: {', '.join(retriever_methods.get_supported_methods())}"}), 400

    logger.info(f"Received research query (Method: {retrieval_method}): {query[:100]}...")

    # --- Perform Retrieval ---
    retrieved_docs_chroma_format = retriever_methods.retrieve(query, retrieval_method)

    if not retrieved_docs_chroma_format.get('ids'):
        logger.warning(f"No documents retrieved for query '{query[:50]}...' with method '{retrieval_method}'.")
        # Return a specific response indicating no context found
        report_data = {
            "report": "No relevant information found in the database for this query.",
            "metrics": [],
            "sentiments": {"description": "N/A", "positive": 0, "neutral": 0, "negative": 0},
            "key_themes": [],
            "aspect_sentiments_aggregated": [],
            "retrieval_method_used": retrieval_method,
            "retrieved_document_count": 0
        }
        return jsonify(report_data), 200 # Return 200 with empty data


    # --- Format Retrieved Documents and Invoke RAG Chain ---
    formatted_context = format_chroma_results_for_prompt(retrieved_docs_chroma_format)

    if not formatted_context.strip():
         logger.warning("Formatted context is empty after retrieval.")
         report_data = {
            "report": "Relevant documents were found, but their content was empty after processing. Cannot generate report.",
            "metrics": [],
            "sentiments": {"description": "N/A", "positive": 0, "neutral": 0, "negative": 0},
            "key_themes": [],
            "aspect_sentiments_aggregated": [],
            "retrieval_method_used": retrieval_method,
            "retrieved_document_count": len(retrieved_docs_chroma_format.get('ids', []))
         }
         return jsonify(report_data), 200


    # Invoke the RAG chain
    llm_output_string = rag_chain.invoke({"context": formatted_context, "question": query})
    logger.info("RAG chain invocation successful.")

    # Attempt to parse the string output as JSON
    report_data = {}
    json_match = re.search(r'\{.*\}', llm_output_string, re.DOTALL)
    if json_match:
        json_string = json_match.group(0)
        try:
            report_data = json.loads(json_string)
            logger.info("Successfully parsed LLM output as JSON.")

            # Add metadata about the retrieval method and count to the report data
            report_data["retrieval_method_used"] = retrieval_method
            report_data["retrieved_document_count"] = len(retrieved_docs_chroma_format.get('ids', []))

            return jsonify(report_data), 200 # Return the parsed JSON

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM output as JSON: {e}")
            logger.error(f"Raw LLM output: {llm_output_string}")
            return jsonify({"error": "Failed to parse report from AI.", "raw_output": llm_output_string}), 500 # Internal server error for parsing failure
    else:
         logger.error("LLM output did not contain a detectable JSON object.")
         logger.error(f"Raw LLM output: {llm_output_string}")
         return jsonify({"error": "AI did not return a valid report format.", "raw_output": llm_output_string}), 500 # Internal server error for format issue

    
# --- Health Check Endpoint ---
@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify if the service is running.
    Returns a simple JSON response indicating the service status.
    """
    return jsonify({"status": "ok", "message": "Research service is running."}), 200

# --- App Startup ---
with app.app_context():
    initialize_rag_components_app()


if __name__ == '__main__':
    app.run(debug=True, port=5000) # Run on port 5000
    print("Flask app is running on url http://localhost:5000 ...")