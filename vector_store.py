import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, persist_directory="faiss_vectordb"):
        self.persist_directory = persist_directory
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
        self.index = None
        self.documents = []
        self.metadata = []
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        os.makedirs(persist_directory, exist_ok=True)
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        index_path = os.path.join(self.persist_directory, "index.faiss")
        docs_path = os.path.join(self.persist_directory, "documents.pkl")
        
        if os.path.exists(index_path) and os.path.exists(docs_path):
            self.index = faiss.read_index(index_path)
            with open(docs_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def _save_index(self):
        """Save index to disk"""
        index_path = os.path.join(self.persist_directory, "index.faiss")
        docs_path = os.path.join(self.persist_directory, "documents.pkl")
        
        faiss.write_index(self.index, index_path)
        with open(docs_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
    
    def add_documents(self, documents):
        """Add documents with embeddings"""
        for doc in documents:
            content = doc['content']
            metadata = doc.get('metadata', {})
            
            # Generate embedding
            embedding = self.embedding_model.encode([content])[0]
            
            # Add to FAISS index
            self.index.add(np.array([embedding], dtype=np.float32))
            
            # Store document and metadata
            self.documents.append(content)
            self.metadata.append(metadata)
        
        self._save_index()
        print(f"Added {len(documents)} document chunks to vector store")
    
    def search(self, query, top_k=3):
        """Search for relevant documents"""
        if self.index.ntotal == 0:
            return {'documents': [[]], 'metadatas': [[]]}
        
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32), 
            min(top_k, self.index.ntotal)
        )
        
        documents = []
        metadatas = []
        for idx in indices[0]:
            if idx < len(self.documents):
                documents.append(self.documents[idx])
                metadatas.append(self.metadata[idx])
        
        return {
            'documents': [documents],
            'metadatas': [metadatas]
        }
