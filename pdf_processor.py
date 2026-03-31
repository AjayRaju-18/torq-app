from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP
import os

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a single PDF file"""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def process_pdfs(self, pdf_directory):
        """Process all PDFs in a directory"""
        documents = []
        
        if not os.path.exists(pdf_directory):
            raise FileNotFoundError(f"Directory {pdf_directory} not found")
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_directory, pdf_file)
            print(f"Processing: {pdf_file}")
            
            text = self.extract_text_from_pdf(pdf_path)
            chunks = self.text_splitter.split_text(text)
            
            for i, chunk in enumerate(chunks):
                documents.append({
                    'content': chunk,
                    'metadata': {
                        'source': pdf_file,
                        'chunk_id': i
                    }
                })
        
        return documents
