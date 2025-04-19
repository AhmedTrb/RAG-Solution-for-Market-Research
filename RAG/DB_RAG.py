import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CHROMA_PATH = "chroma"
CSV_PATH = "./poc_output/ecommerce_processed_20250409-102422.csv"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def load_documents():
    loader = CSVLoader(
        file_path=CSV_PATH,
        encoding="utf-8",
        csv_args={"delimiter": ","}
    )
    return loader.load()

def split_documents(documents):
    splitter = CharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separator="\n"
    )
    chunks = splitter.split_documents(documents)
    print(f"Split {len(documents)} docs into {len(chunks)} chunks.")
    return chunks

def embed_and_store(chunks):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Stored {len(chunks)} chunks in Chroma vector DB.")

def query_rag(question: str):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    results = db.similarity_search_with_relevance_scores(question, k=3)
    if not results or results[0][1] < 0.7:
        return "No good match found in the knowledge base."

    context = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(
        context=context, question=question
    )

    model = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )

    response = model.invoke(prompt)
    sources = [doc.metadata.get("source", "N/A") for doc, _ in results]

    return {
        "response": response.content,
        "sources": sources
    }

def main():
    documents = load_documents()
    chunks = split_documents(documents)
    embed_and_store(chunks)

if __name__ == "__main__":
    main()
