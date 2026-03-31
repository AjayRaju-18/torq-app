import streamlit as st
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import PyPDF2

# Simple PDF processor
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def split_text(text, chunk_size=800, overlap=100):
    """Split text into overlapping chunks for better context preservation"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) > 50:  # Only keep substantial chunks
            chunks.append(' '.join(chunk_words))
    
    return chunks

# Simple vector store
class SimpleVectorStore:
    def __init__(self):
        self.documents = []
        self.original_documents = []  # Store original text for better context
        self.metadata = []
        self.vectorizer = TfidfVectorizer(
            max_features=1000, 
            stop_words='english',
            ngram_range=(1, 3),  # Include 1-3 word phrases
            min_df=1,
            max_df=0.95
        )
        self.document_vectors = None
    
    def add_documents(self, documents):
        for doc in documents:
            # Store original content for context
            original_content = doc['content']
            self.original_documents.append(original_content)
            
            # Process for search
            processed_content = re.sub(r'[^a-zA-Z0-9\s]', ' ', original_content.lower())
            processed_content = ' '.join(processed_content.split())  # Clean whitespace
            
            self.documents.append(processed_content)
            self.metadata.append(doc.get('metadata', {}))
        
        if self.documents:
            self.document_vectors = self.vectorizer.fit_transform(self.documents)
    
    def search(self, query, top_k=5):
        if not self.documents or self.document_vectors is None:
            return [], []
        
        # Process query similar to documents
        processed_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query.lower())
        processed_query = ' '.join(processed_query.split())
        
        query_vector = self.vectorizer.transform([processed_query])
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]
        
        # Get top k indices sorted by similarity
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Filter results with similarity > 0.05 (higher threshold for better relevance)
        results = []
        sources = []
        for i in top_indices:
            if similarities[i] > 0.05:
                # Return original content (not processed)
                results.append(self.original_documents[i])
                sources.append(self.metadata[i].get('source', 'Unknown'))
        
        return results, sources

# Simple GROQ client
def call_groq(messages, api_key):
    import requests
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'llama-3.1-8b-instant',
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 1024
    }
    
    try:
        response = requests.post('https://api.groq.com/openai/v1/chat/completions', 
                               headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Error: Could not connect to GROQ API"

# Streamlit app
st.set_page_config(page_title="TORQ", page_icon="🤖")
st.title("🤖 TORQ - Mechanical Engineering Assistant")

# Initialize
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = SimpleVectorStore()
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("📄 Upload PDFs")
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    
    if uploaded_file and st.button("Process PDF"):
        with st.spinner("Processing..."):
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            text = extract_text_from_pdf(temp_path)
            chunks = split_text(text)
            
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    'content': chunk,
                    'metadata': {'source': uploaded_file.name, 'chunk_id': i}
                })
            
            st.session_state.vector_store.add_documents(documents)
            os.remove(temp_path)
            st.success(f"Processed {len(chunks)} chunks")
    
    use_rag = st.checkbox("Enable RAG Mode", value=True)
    
    # Show PDF status
    if len(st.session_state.vector_store.documents) > 0:
        st.success(f"✅ {len(st.session_state.vector_store.documents)} document chunks loaded")
    else:
        st.warning("⚠️ No PDFs uploaded. RAG mode will use general knowledge only.")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about mechanical engineering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                response = "Please set GROQ_API_KEY in Streamlit secrets"
            else:
                if use_rag:
                    search_results = st.session_state.vector_store.search(prompt)
                    if isinstance(search_results, tuple) and len(search_results) == 2:
                        context_docs, sources = search_results
                    else:
                        context_docs = search_results
                        sources = []
                    
                    if context_docs:
                        # Use top 3 most relevant chunks
                        context = "\n\n---\n\n".join(context_docs[:3])
                        
                        full_prompt = f"""You are TORQ, a mechanical engineering assistant. Answer the question STRICTLY based on the provided context from the uploaded PDF document. 

IMPORTANT INSTRUCTIONS:
- Use ONLY the information provided in the context below
- If the context doesn't contain enough information to answer the question, clearly state "The uploaded PDF doesn't contain sufficient information about this topic"
- Do NOT use general knowledge unless the context is insufficient
- Quote relevant parts from the context when possible
- Be specific and detailed in your answer

CONTEXT FROM UPLOADED PDF:
{context}

QUESTION: {prompt}

ANSWER (based strictly on the PDF context):"""
                        
                        # Show which documents are being used
                        if sources:
                            unique_sources = list(set(sources))
                            st.info(f"📚 Searching in: {', '.join(unique_sources)} | Found {len(context_docs)} relevant sections")
                    else:
                        full_prompt = f"The uploaded PDF doesn't contain any relevant information about: '{prompt}'. Please upload a PDF that covers this topic, or disable RAG mode for general mechanical engineering knowledge."
                        st.warning("⚠️ No relevant content found in uploaded PDFs for this question.")
                else:
                    full_prompt = f"Answer this mechanical engineering question using your general knowledge: {prompt}"
                
                messages = [
                    {"role": "system", "content": "You are TORQ, a mechanical engineering assistant. When RAG mode is enabled, you MUST prioritize and use ONLY the provided PDF context. Be precise and cite the source material."},
                    {"role": "user", "content": full_prompt}
                ]
                
                response = call_groq(messages, api_key)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})