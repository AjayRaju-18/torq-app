import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class VectorStore:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.document_vectors = None
    
    def _preprocess_text(self, text):
        """Simple text preprocessing"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def add_documents(self, documents):
        """Add documents with TF-IDF embeddings"""
        for doc in documents:
            content = self._preprocess_text(doc['content'])
            metadata = doc.get('metadata', {})
            
            self.documents.append(content)
            self.metadata.append(metadata)
        
        # Fit vectorizer and transform all documents
        if self.documents:
            self.document_vectors = self.vectorizer.fit_transform(self.documents)
        
        print(f"Added {len(documents)} document chunks to vector store")
    
    def search(self, query, top_k=3):
        """Search for relevant documents using TF-IDF and cosine similarity"""
        if len(self.documents) == 0 or self.document_vectors is None:
            return {'documents': [[]], 'metadatas': [[]]}
        
        # Preprocess and vectorize query
        processed_query = self._preprocess_text(query)
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Filter out results with very low similarity
        filtered_indices = [i for i in top_indices if similarities[i] > 0.01]
        
        # Get results
        documents = [self.documents[i] for i in filtered_indices]
        metadatas = [self.metadata[i] for i in filtered_indices]
        
        return {
            'documents': [documents],
            'metadatas': [metadatas]
        }