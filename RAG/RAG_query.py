from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

# --- Load environment variables ---
import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- ChromaDB ---
persist_directory = "./chroma_db_market_research"
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

# Initialize the LLM (ensure GOOGLE_API_KEY is set)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1,google_api_key="AIzaSyAVecBp5oOHIgB9cTRLwIulq-l9PdteA1g")

db_reloaded = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="market_data_main",
    )
retriever_reloaded = db_reloaded.as_retriever(search_kwargs={'k': 5})

# Create the retriever from the vector store
retriever = db_reloaded.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 5} # Retrieve top 4 most similar chunks
)

# Define the RAG prompt template
template = """You are a helpful Product Insights Assistant. Your goal is to analyze customer feedback (like reviews, forum posts, comments) provided in the CONTEXT to answer the user's QUESTION thoroughly.

Your analysis must be based *strictly* on the information contained within the CONTEXT. Do not add external knowledge or information from outside the provided text.

Present your entire response as a single, valid JSON object. Do not include any introductory text, explanations, summaries, or markdown formatting outside the JSON structure.

CONTEXT:
{context}

QUESTION:
{question}

Analyze the CONTEXT and the QUESTION to generate the following insights, structured according to the JSON schema below:

1.  **Generate Report ("report"):** Write a clear and concise summary that directly answers the user's QUESTION. Synthesize the key findings, themes, positive points, and negative points or pain points mentioned in the CONTEXT. Use bullet points if helpful for lists of issues or praised aspects. Maintain an informative yet accessible tone.
2.  **Identify Key Metrics ("metrics"):** Extract 2-4 quantifiable data points relevant to the QUESTION from the CONTEXT. Examples: Count of comments mentioning 'customer service', percentage of reviews mentioning 'battery life', number of 1-star reviews provided.
3.  **Summarize Sentiments ("sentiments"):** Calculate the overall sentiment distribution (positive, neutral, negative counts or percentages) across all relevant feedback within the CONTEXT. Provide a brief description clarifying the scope.
4.  **Extract Key Themes ("key_themes"):** Identify the top 3-5 most prominent topics, features, or issues discussed in the CONTEXT related to the QUESTION. List them as keywords or short phrases.

REQUIRED JSON OUTPUT SCHEMA:
```json
{{
  "report": "A synthesized textual Long summary answering the user's question. Highlight key takeaways, user experiences (positive/negative), mentioned themes, and specific examples found *only* in the provided context. Use clear language and bullet points where appropriate for readability.must be in a coherant paragraph format with a clear structure in markdown format.",
  "metrics": [
    {{
      "title": "Metric Name (e.g., 'Contract Issue Mentions', 'Positive Camera Feedback Count')",
      "value": "<calculated_value_as_string_or_number>",
      "description": "Brief explanation (e.g., 'Number of comments discussing contract problems', 'Count of reviews praising the camera')"
    }}
  ],
  "sentiments": {{
    "description": "Overall sentiment distribution in the provided feedback related to the question.",
    "positive": "<count_or_percentage>",
    "neutral": "<count_or_percentage>",
    "negative": "<count_or_percentage>"
  }},
  "key_themes": [
    "Theme or Keyword 1 (e.g., 'Customer Service')",
    "Theme or Keyword 2 (e.g., 'Performance')",
    "Theme or Keyword 3 (e.g., 'Value for Money')",
    "Theme or Keyword 4 (e.g., 'Cancellation Policy')"
  ]
}}
```"""
prompt = ChatPromptTemplate.from_template(template)

# Helper function to format retrieved documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Build the RAG chain using LangChain Expression Language (LCEL)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("\nRAG chain created successfully.")

# --- Example Usage ---
if __name__ == "__main__":
    # Example questions:
    query1 = "Analyze discussions from the past 6 months across Amazon reviews, Reddit, Twitter, and tech review sites regarding Ring, Google Nest Cam, Wyze Cam, and Eufy security cameras. Synthesize the primary user concerns related to data privacy and security vulnerabilities for each brand. Additionally, evaluate user sentiment towards the necessity and cost of each brand's subscription plan (e.g., Ring Protect, Nest Aware). Identify which features users most frequently mention as being locked behind paywalls and the reaction to this."

    print(f"\nQuery 1: {query1}")
    response1 = rag_chain.invoke(query1)
    print(f"Answer 1: {response1}")
