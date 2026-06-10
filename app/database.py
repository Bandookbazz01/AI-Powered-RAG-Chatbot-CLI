import os
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

# We initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
Path(CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)

# Initialize vector store
vector_store = Chroma(
    collection_name="chatbot_knowledge",
    embedding_function=embeddings,
    persist_directory=CHROMA_PERSIST_DIR
)

def get_vector_store():
    """Get the vector store instance"""
    return vector_store

def add_to_knowledge_base(texts: list[str], metadatas: list[dict] = None):
    """Add multiple texts to the vector database"""
    if metadatas is None:
        metadatas = [{} for _ in texts]
    vector_store.add_texts(texts=texts, metadatas=metadatas)

def initialize_knowledge_base():
    """Initialize with sample knowledge if empty"""
    try:
        collection = vector_store._collection
        count = collection.count()
        
        if count == 0:
            print("📚 Initializing knowledge base with sample data...")
            sample_docs = [
                "I am an advanced AI chatbot assistant designed to help users with information, answer questions, and engage in meaningful conversations.",
                "This system is powered by the Google Gemini API for state-of-the-art natural language processing and understanding.",
                "It uses MongoDB for persistent chat history, ensuring conversations are remembered across sessions.",
                "ChromaDB is integrated for efficient vector storage and semantic search, allowing me to retrieve relevant context quickly.",
                "I am continually learning and can adapt to various topics based on the context provided."
            ]
            metadatas = [{"source": "system_initialization"} for _ in sample_docs]
            add_to_knowledge_base(sample_docs, metadatas)
            print("✅ Knowledge base initialized successfully!")
    except Exception as e:
        print(f"⚠️  Could not initialize knowledge base: {str(e)}")

def process_and_add_pdf(file_path: str):
    """Read a PDF file and add its contents to the knowledge base."""
    import fitz  # PyMuPDF
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    try:
        print(f"📄 Processing PDF: {file_path}")
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
            
        if not text.strip():
            print("⚠️ PDF appears to be empty or unscannable.")
            return False
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        
        metadatas = [{"source": os.path.basename(file_path)} for _ in chunks]
        add_to_knowledge_base(chunks, metadatas)
        print(f"✅ Successfully added {len(chunks)} chunks from {os.path.basename(file_path)} to the knowledge base!")
        return True
    except Exception as e:
        print(f"❌ Error processing PDF: {str(e)}")
        return False
