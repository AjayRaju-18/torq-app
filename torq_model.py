from groq import Groq
from vector_store import VectorStore
from config import GROQ_API_KEY, GROQ_MODEL, TOP_K_RESULTS

class TORQModel:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.vector_store = VectorStore()
        self.model = GROQ_MODEL
    
    def generate_response(self, query, chat_history=None):
        """Generate response using RAG with chat history"""
        # Retrieve relevant context
        search_results = self.vector_store.search(query, top_k=TOP_K_RESULTS)
        
        if search_results['documents'][0]:
            context = "\n\n".join(search_results['documents'][0])
            sources = [meta['source'] for meta in search_results['metadatas'][0]]
            
            # Create prompt with context
            prompt = f"""You are TORQ, a specialized mechanical engineering assistant trained on mechanical engineering textbooks and resources.

Context from mechanical engineering books:
{context}

Question: {query}

Provide a detailed, technical answer based on the context above. If the context doesn't contain enough information, answer based on your general knowledge."""
        else:
            # No relevant documents found, use general knowledge
            prompt = query
            sources = []
        
        # Build messages with chat history
        messages = [
            {
                "role": "system",
                "content": "You are TORQ, an expert mechanical engineering assistant. You help with mechanical engineering questions and general conversations."
            }
        ]
        
        # Add recent chat history (last 5 exchanges)
        if chat_history:
            recent_history = chat_history[-10:]
            for msg in recent_history:
                if msg['role'] in ['user', 'assistant']:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Generate response using GROQ
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=1024
        )
        
        response = chat_completion.choices[0].message.content
        
        return {
            'answer': response,
            'sources': list(set(sources))
        }
    
    def generate_chat_response(self, query, chat_history=None):
        """Generate response without RAG (normal chatbot mode)"""
        messages = [
            {
                "role": "system",
                "content": "You are TORQ, a friendly and knowledgeable mechanical engineering assistant. You can discuss mechanical engineering topics and have general conversations."
            }
        ]
        
        # Add recent chat history
        if chat_history:
            recent_history = chat_history[-10:]
            for msg in recent_history:
                if msg['role'] in ['user', 'assistant']:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
        
        messages.append({
            "role": "user",
            "content": query
        })
        
        # Generate response using GROQ
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=1024
        )
        
        return chat_completion.choices[0].message.content
