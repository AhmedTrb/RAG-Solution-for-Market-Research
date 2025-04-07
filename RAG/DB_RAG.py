from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.embeddings import AzureOpenAIEmbeddings  # Importer la bonne classe pour Azure
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from dotenv import load_dotenv
import os
import shutil

# Chargement des variables d'environnement
load_dotenv()

# Clés et configuration Azure OpenAI
AZURE_API_KEY = os.getenv("5PBW3sDM1p8GgpKG9iS80Y706oZqeXyPkkfpvDwS35usk24FZxgtJQQJ99BDACYeBjFXJ3w3AAABACOGhdSX")
AZURE_API_BASE = os.getenv("https://pcd.openai.azure.com/")
AZURE_API_VERSION = os.getenv("2023-05-15")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("text-embedding-ada-002")

# Chemins de stockage
CHROMA_PATH = "chroma"
CSV_PATH = "products_details.csv"  # Assurez-vous que ce fichier est présent

def main():
    generate_data_store()

def generate_data_store():
    documents = load_csv_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

def load_csv_documents():
    loader = CSVLoader(
        file_path=CSV_PATH,
        encoding="utf-8",
        csv_args={
            'delimiter': ',',
            'fieldnames': None  # Modifier si votre CSV n’a pas d’en-têtes
        }
    )
    return loader.load()

def split_text(documents: list[Document]):
    text_splitter = CharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separator="\n",
        length_function=len,
        is_separator_regex=False
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"Split {len(documents)} documents en {len(chunks)} chunks")
    print("\nExemple de chunk:")
    print(chunks[0].page_content[:200] + "...")
    print("\nMétadonnées:", chunks[0].metadata)
    
    return chunks

def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Utilisation d'AzureOpenAIEmbeddings pour Azure
    embeddings = AzureOpenAIEmbeddings(
        deployment=AZURE_EMBEDDING_DEPLOYMENT,
        model="text-embedding-ada-002",  # Le modèle utilisé dans Azure
        openai_api_key=AZURE_API_KEY,
        openai_api_base=AZURE_API_BASE,
        openai_api_version=AZURE_API_VERSION
    )
    
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"\nBase Chroma mise à jour avec {len(chunks)} chunks")

if __name__ == "__main__":
    main()
