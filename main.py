from pdf_processor import PDFProcessor
from vector_store import VectorStore
from torq_model import TORQModel
import sys

def train_torq(pdf_directory):
    """Train TORQ by processing PDFs and building vector store"""
    print("=== TORQ Training Started ===")
    
    processor = PDFProcessor()
    vector_store = VectorStore()
    
    print(f"Processing PDFs from: {pdf_directory}")
    documents = processor.process_pdfs(pdf_directory)
    
    print(f"Adding {len(documents)} chunks to vector store...")
    vector_store.add_documents(documents)
    
    print("=== TORQ Training Complete ===")

def query_torq(question):
    """Query TORQ model"""
    torq = TORQModel()
    result = torq.generate_response(question)
    
    print("\n=== TORQ Response ===")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSources: {', '.join(result['sources'])}")
    print("\n" + "="*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Train: python main.py train <pdf_directory>")
        print("  Query: python main.py query '<your question>'")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "train":
        if len(sys.argv) < 3:
            print("Please provide PDF directory path")
            sys.exit(1)
        train_torq(sys.argv[2])
    
    elif mode == "query":
        if len(sys.argv) < 3:
            print("Please provide a question")
            sys.exit(1)
        query_torq(sys.argv[2])
    
    else:
        print("Invalid mode. Use 'train' or 'query'")
