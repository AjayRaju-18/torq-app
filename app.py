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

def split_text(text, chunk_size=1000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1
        
        if current_size >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

# Simple vector store
class SimpleVectorStore:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.document_vectors = None
    
    def add_documents(self, documents):
        for doc in documents:
            content = re.sub(r'[^a-zA-Z0-9\s]', ' ', doc['content'].lower())
            self.documents.append(content)
            self.metadata.append(doc.get('metadata', {}))
        
        if self.documents:
            self.document_vectors = self.vectorizer.fit_transform(self.documents)
    
    def search(self, query, top_k=3):
        if not self.documents or self.document_vectors is None:
            return [], []
        
        query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query.lower())
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Filter results with similarity > 0.01 and return both content and metadata
        results = []
        sources = []
        for i in top_indices:
            if similarities[i] > 0.01:
                results.append(self.documents[i])
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
                    context_docs, sources = st.session_state.vector_store.search(prompt)
                    if context_docs:
                        context = "\n\n".join(context_docs[:3])
                        full_prompt = f"""Based on the following context from uploaded documents, answer the question. If the context doesn't contain enough information, say so and provide general knowledge.

Context from uploaded PDF:
{context}

Question: {prompt}

Answer based on the context above:"""
                        
                        # Show which documents are being used
                        if sources:
                            st.info(f"📚 Using content from: {', '.join(set(sources))}")
                    else:
                        full_prompt = f"No relevant content found in uploaded PDFs. Please answer based on general mechanical engineering knowledge: {prompt}"
                        st.warning("⚠️ No relevant content found in uploaded PDFs. Answering from general knowledge.")
                else:
                    full_prompt = prompt
                
                messages = [
                    {"role": "system", "content": "You are TORQ, a mechanical engineering assistant. When provided with context from documents, prioritize that information in your response. Always be clear about whether you're using uploaded document content or general knowledge."},
                    {"role": "user", "content": full_prompt}
                ]
                
                response = call_groq(messages, api_key)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})