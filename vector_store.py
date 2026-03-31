import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.embeddings = []
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    def add_documents(self, documents):
        """Add documents with embeddings"""
        for doc in documents:
            content = doc['content']
            metadata = doc.get('metadata', {})
            
            # Generate embedding
            embedding = self.embedding_model.encode([content])[0]
            
            # Store
            self.documents.append(content)
            self.metadata.append(metadata)
            self.embeddings.append(embedding)
        
        print(f"Added {len(documents)} document chunks to vector store")
    
    def search(self, query, top_k=3):
        """Search for relevant documents using cosine similarity"""
        if len(self.documents) == 0:
            return {'documents': [[]], 'metadatas': [[]]}
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculate cosine similarities
        similarities = cosine_similarity(
            [query_embedding],
            self.embeddings
        )[0]
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Get results
        documents = [self.documents[i] for i in top_indices]
        metadatas = [self.metadata[i] for i in top_indices]
        
        return {
            'documents': [documents],
            'metadatas': [metadatas]
        }
