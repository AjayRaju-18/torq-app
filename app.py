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
        self.original_documents = []
        self.metadata = []
        self.vectorizer = TfidfVectorizer(
            max_features=1000, 
            stop_words='english',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95
        )
        self.document_vectors = None
    
    def clear_all(self):
        """Clear all stored documents and reset the vector store"""
        self.documents = []
        self.original_documents = []
        self.metadata = []
        self.document_vectors = None
        self.vectorizer = TfidfVectorizer(
            max_features=1000, 
            stop_words='english',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95
        )
        return True
    
    def add_documents(self, documents):
        for doc in documents:
            original_content = doc['content']
            self.original_documents.append(original_content)
            
            processed_content = re.sub(r'[^a-zA-Z0-9\s]', ' ', original_content.lower())
            processed_content = ' '.join(processed_content.split())
            
            self.documents.append(processed_content)
            self.metadata.append(doc.get('metadata', {}))
        
        if self.documents:
            self.document_vectors = self.vectorizer.fit_transform(self.documents)
    
    def search(self, query, top_k=5):
        if not self.documents or self.document_vectors is None:
            return [], []
        
        processed_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query.lower())
        processed_query = ' '.join(processed_query.split())
        
        query_vector = self.vectorizer.transform([processed_query])
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        sources = []
        # Lower threshold for more flexible matching
        for i in top_indices:
            if similarities[i] > 0.02:  # Lowered from 0.05 for better recall
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
st.set_page_config(
    page_title="TORQ", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🤖 TORQ - Mechanical Engineering Assistant")

# Add PWA meta tags for mobile optimization
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#ff6b6b">
<link rel="manifest" href="./manifest.json">
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = SimpleVectorStore()
    # Clear any existing chunks on fresh start
    st.session_state.vector_store.clear_all()
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("📄 Upload PDFs")
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    
    col1, col2 = st.columns(2)
    with col1:
        if uploaded_file and st.button("Process PDF", type="primary"):
            with st.spinner("Processing PDF..."):
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
                st.success(f"✅ Processed {len(chunks)} chunks from {uploaded_file.name}")
    
    with col2:
        if st.button("Clear All PDFs", type="secondary"):
            cleared = st.session_state.vector_store.clear_all()
            if cleared:
                st.success("🗑️ All PDF content and chunks cleared")
                st.rerun()
    
    st.divider()
    
    # RAG Mode Toggle
    use_rag = st.checkbox("🧠 Enable RAG Mode", value=True, help="Use uploaded PDF content to answer questions")
    
    # Show PDF status
    if len(st.session_state.vector_store.documents) > 0:
        st.success(f"📚 {len(st.session_state.vector_store.documents)} document chunks loaded")
        if use_rag:
            st.info("🧠 RAG Mode: Answers based on PDF content and meaning")
        else:
            st.info("💬 Normal Mode: ChatGPT-like general assistant")
    else:
        st.warning("⚠️ No PDFs uploaded")
        if use_rag:
            st.error("❌ RAG Mode requires PDF upload")
    
    st.divider()
    
    if st.button("Clear Chat History"):
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
                if use_rag and len(st.session_state.vector_store.documents) > 0:
                    # RAG Mode - Answer based on PDF content meaning and context
                    search_results = st.session_state.vector_store.search(prompt)
                    if isinstance(search_results, tuple) and len(search_results) == 2:
                        context_docs, sources = search_results
                    else:
                        context_docs = search_results
                        sources = []
                    
                    if context_docs:
                        context = "\n\n---RELEVANT CONTENT---\n\n".join(context_docs[:4])
                        
                        full_prompt = f"""You are TORQ, a mechanical engineering assistant. Based on the PDF content provided below, answer the user's question. 

IMPORTANT INSTRUCTIONS:
- Use the PDF content as your knowledge base and primary source
- Extract the core meaning and concepts from the PDF content
- You can explain, elaborate, and provide context beyond what's directly written
- Connect related concepts from the PDF to give comprehensive answers
- If the PDF content is relevant but doesn't fully answer the question, use it as a foundation and build upon it with engineering knowledge
- Always indicate that your answer is based on the uploaded PDF content
- If the PDF content is completely unrelated to the question, clearly state this

PDF CONTENT FROM UPLOADED DOCUMENT:
{context}

USER QUESTION: {prompt}

ANSWER (based on PDF content):"""
                        
                        unique_sources = list(set(sources)) if sources else []
                        st.info(f"📖 Analyzing content from: {', '.join(unique_sources)} | Found {len(context_docs)} relevant sections")
                        
                    else:
                        full_prompt = f"""The uploaded PDF doesn't contain information relevant to your question: "{prompt}". 

Please ask questions related to the content in your uploaded PDF document, or disable RAG mode to use me as a general mechanical engineering assistant."""
                        st.warning("🔍 No relevant content found in the uploaded PDF for this question.")
                
                elif use_rag and len(st.session_state.vector_store.documents) == 0:
                    # RAG Mode enabled but no PDFs
                    full_prompt = "Please upload a PDF document first to enable RAG mode, or disable RAG mode for general assistance."
                    st.error("📄 RAG Mode requires a PDF to be uploaded first.")
                
                else:
                    # Normal Mode - ChatGPT-like assistant
                    full_prompt = f"""You are TORQ, an intelligent and helpful AI assistant specializing in mechanical engineering. You have extensive knowledge across all areas of mechanical engineering including:

- Thermodynamics and heat transfer
- Fluid mechanics and dynamics  
- Materials science and engineering
- Machine design and mechanics
- Manufacturing processes
- Control systems and automation
- CAD/CAM and design software
- Project management and engineering economics
- Safety and regulatory standards

Respond naturally and conversationally like ChatGPT, providing detailed explanations, examples, and practical insights. Be helpful, engaging, and educational.

User Question: {prompt}

Response:"""
                    st.info("💬 Normal Mode: General mechanical engineering assistant")
                
                messages = [
                    {"role": "system", "content": "You are TORQ, a helpful AI assistant. Respond naturally and professionally."},
                    {"role": "user", "content": full_prompt}
                ]
                
                response = call_groq(messages, api_key)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})