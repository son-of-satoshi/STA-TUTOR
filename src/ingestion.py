import os
from pypdf import PdfReader

DOCS_DIR = os.path.join("data", "documents")
print(f"--- Debug: Looking inside folder: {os.path.abspath(DOCS_DIR)} ---")

if os.path.exists(DOCS_DIR):
    all_files = os.listdir(DOCS_DIR)
    print(f"All files found in folder: {all_files}")
    
    # Check for PDFs (case-insensitive so .PDF or .pdf both work)
    pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
    print(f"Matched PDF files: {pdf_files}")

    for file in pdf_files:
        file_path = os.path.join(DOCS_DIR, file)
        reader = PdfReader(file_path)
        print(f"-> Successfully read '{file}': {len(reader.pages)} pages found.")
else:
    print("Error: The data/documents directory does not exist!")