import chromadb
from sentence_transformers import SentenceTransformer
from config import VECTOR_DB_PATH, EMBEDDING_MODEL

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.collection = self.client.get_or_create_collection(name="torq_mechanical_engineering")
    
    def add_documents(self, documents):
        """Add documents to the vector store"""
        texts = [doc['content'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        ids = [f"{doc['metadata']['source']}_{doc['metadata']['chunk_id']}" for doc in documents]
        
        embeddings = self.embedding_model.encode(texts).tolist()
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} document chunks to vector store")
    
    def search(self, query, top_k=3):
        """Search for relevant documents"""
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        return results
