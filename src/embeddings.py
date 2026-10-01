import os
from pypdf import PdfReader
import chromadb

# Paths
DOCS_DIR = os.path.join("data", "documents")
DB_DIR = os.path.join("data", "vector_db")

def chunk_text(text, chunk_size=500, overlap=50):
    """Splits long text into smaller chunks with some overlap so context isn't lost."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

def process_and_store_documents():
    print("Initializing local Vector Database (ChromaDB)...")
    # Set up ChromaDB to save data locally in our project folder
    client = chromadb.PersistentClient(path=DB_DIR)
    
    # Create a collection for our STA course materials
    collection = client.get_or_create_collection(name="sta_materials")

    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")]
    
    total_chunks = 0

    for file in pdf_files:
        file_path = os.path.join(DOCS_DIR, file)
        print(f"Processing '{file}'...")
        
        reader = PdfReader(file_path)
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text.strip():
                continue # Skip empty pages
                
            # Break page into bite-sized chunks
            chunks = chunk_text(text)
            
            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"{file}_p{page_num+1}_c{chunk_idx}"
                
                # Add chunk to ChromaDB
                collection.add(
                    documents=[chunk],
                    metadatas=[{"source": file, "page": page_num + 1}],
                    ids=[chunk_id]
                )
                total_chunks += 1

    print(f"\nSuccess! Processed all documents and stored {total_chunks} text chunks into ChromaDB.")

if __name__ == "__main__":
    process_and_store_documents()