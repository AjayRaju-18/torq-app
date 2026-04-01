import streamlit as st
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import PyPDF2
import json
from datetime import datetime
import uuid
import pickle
import shutil

# Simple PDF processor
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
    return text

def split_text(text, chunk_size=500, overlap=50):
    """Split text into smaller overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) > 30:
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
        """Clear all stored documents"""
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
    
    def validate_and_repair(self):
        """Validate vector store state"""
        if not self.documents:
            return True
        
        try:
            _ = self.vectorizer.vocabulary_
            test_vector = self.vectorizer.transform(["test"])
        except (AttributeError, ValueError):
            self.document_vectors = self.vectorizer.fit_transform(self.documents)
        
        if self.document_vectors is None or self.document_vectors.shape[0] != len(self.documents):
            self.document_vectors = self.vectorizer.fit_transform(self.documents)
        
        return True
    
    def search(self, query, top_k=3):
        if not self.documents or self.document_vectors is None:
            return [], []
        
        try:
            _ = self.vectorizer.vocabulary_
        except AttributeError:
            if self.documents:
                self.document_vectors = self.vectorizer.fit_transform(self.documents)
            else:
                return [], []
        
        processed_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query.lower())
        processed_query = ' '.join(processed_query.split())
        
        try:
            query_vector = self.vectorizer.transform([processed_query])
        except Exception:
            if self.documents:
                self.document_vectors = self.vectorizer.fit_transform(self.documents)
                query_vector = self.vectorizer.transform([processed_query])
            else:
                return [], []
        
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        sources = []
        for i in top_indices:
            if similarities[i] > 0.02:
                results.append(self.original_documents[i])
                sources.append(self.metadata[i].get('source', 'Unknown'))
        
        return results, sources

def estimate_tokens(text):
    """Rough estimation of tokens"""
    return len(text) // 4

def call_groq(messages, api_key):
    import requests
    
    if not api_key:
        return "Error: GROQ API key not found."
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'llama-3.1-8b-instant',
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 2048  # Increased from 800 to allow longer responses
    }
    
    try:
        total_text = " ".join([msg['content'] for msg in messages])
        estimated_tokens = estimate_tokens(total_text)
        
        # Be more conservative with token limits to allow longer responses
        if estimated_tokens > 4000:  # Reduced from 5000 to leave more room for response
            if len(messages) > 1 and len(messages[-1]['content']) > 1500:  # Reduced from 2000
                messages[-1]['content'] = messages[-1]['content'][:1500] + "...[truncated]"
        
        response = requests.post('https://api.groq.com/openai/v1/chat/completions', 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Check if response was truncated due to token limit
                finish_reason = result['choices'][0].get('finish_reason', '')
                if finish_reason == 'length':
                    content += "\n\n⚠️ *Response truncated due to length. Ask me to continue for more details.*"
                
                return content
            else:
                return f"Error: Unexpected API response"
        
        elif response.status_code == 401:
            return "Error: Invalid GROQ API key."
        
        elif response.status_code == 429:
            return "Error: Rate limit exceeded. Please try again."
        
        else:
            return f"Error: API returned status {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "Error: Request timed out."
    
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to API."
    
    except Exception as e:
        return f"Error: {str(e)}"

def generate_chat_title(first_message):
    """Generate title from first message"""
    if len(first_message) > 50:
        return first_message[:47] + "..."
    return first_message

def get_conversation_context(messages, max_context=3):
    """Get recent conversation context"""
    if len(messages) <= 1:
        return ""
    
    recent_messages = messages[-max_context:]
    context_parts = []
    
    for msg in recent_messages:
        role = "Human" if msg["role"] == "user" else "Assistant"
        content = msg['content']
        if len(content) > 200:
            content = content[:200] + "..."
        context_parts.append(f"{role}: {content}")
    
    return "\n".join(context_parts)

# Streamlit app
st.set_page_config(
    page_title="TORQ", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ChatGPT-like CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    .chat-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    .chat-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = SimpleVectorStore()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "personal"

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if 'chat_histories' not in st.session_state:
    st.session_state.chat_histories = []

# Header
st.markdown("""
<div class="chat-header">
    <h1 class="chat-title">TORQ</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    if st.button("+ New chat", key="new_chat"):
        st.session_state.messages = []
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("**Recent chats**")
    
    if st.session_state.chat_histories:
        for chat in st.session_state.chat_histories[:10]:
            mode_icon = "🤖" if chat.get('mode', 'personal') == "personal" else "📚"
            if st.button(f"{chat.get('title', 'Chat')}", key=f"chat_{chat.get('id', '')}"):
                st.session_state.messages = chat.get('messages', []).copy()
                st.session_state.current_mode = chat.get('mode', 'personal')
                st.session_state.current_chat_id = chat.get('id', str(uuid.uuid4()))
                st.rerun()
    else:
        st.info("No conversations yet")

# Main content
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Mode selector
mode_options = {
    "🤖 Personal Assistant": "personal",
    "📚 Educational Mode": "educational"
}

selected_mode = st.selectbox(
    "Choose mode:",
    options=list(mode_options.keys()),
    index=0 if st.session_state.current_mode == "personal" else 1,
    key="mode_selector",
    label_visibility="collapsed"
)

if mode_options[selected_mode] != st.session_state.current_mode:
    st.session_state.current_mode = mode_options[selected_mode]
    st.rerun()

# PDF Upload for Educational Mode
if st.session_state.current_mode == "educational":
    with st.expander("📄 Upload PDF", expanded=len(st.session_state.vector_store.documents) == 0):
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'], key="pdf_uploader")
        
        col1, col2 = st.columns([2, 1])
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
                    st.success(f"✅ Processed {len(chunks)} chunks")
                    st.rerun()
        
        with col2:
            if len(st.session_state.vector_store.documents) > 0 and st.button("Clear PDF"):
                st.session_state.vector_store.clear_all()
                st.success("PDF cleared")
                st.rerun()
        
        if len(st.session_state.vector_store.documents) > 0:
            st.info(f"📚 {len(st.session_state.vector_store.documents)} chunks loaded")

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Get API key
            api_key = None
            try:
                api_key = st.secrets.get("GROQ_API_KEY")
            except:
                pass
            
            if not api_key:
                api_key = os.getenv('GROQ_API_KEY')
            
            if not api_key:
                response = "⚠️ API key not configured. Please add GROQ_API_KEY to Streamlit secrets."
            else:
                conversation_context = get_conversation_context(st.session_state.messages[:-1])
                
                if st.session_state.current_mode == "educational" and len(st.session_state.vector_store.documents) > 0:
                    try:
                        st.session_state.vector_store.validate_and_repair()
                        search_results = st.session_state.vector_store.search(prompt)
                        
                        if isinstance(search_results, tuple):
                            context_docs, sources = search_results
                        else:
                            context_docs = search_results
                            sources = []
                        
                        if context_docs:
                            context = "\n\n".join(context_docs[:2])
                            if len(context) > 2500:  # Reduced from 3000 to leave more room for response
                                context = context[:2500] + "..."
                            
                            full_prompt = f"""Based on PDF content, answer the question.

PDF CONTENT:
{context}

QUESTION: {prompt}

DETAILED ANSWER:"""
                            st.info(f"📖 Found {len(context_docs)} relevant sections")
                        else:
                            full_prompt = f"The PDF doesn't contain relevant information for: '{prompt}'"
                            st.warning("No relevant content found")
                    
                    except Exception as e:
                        full_prompt = f"Error searching PDF: {str(e)}"
                
                elif st.session_state.current_mode == "educational":
                    full_prompt = "Please upload a PDF first."
                    st.error("PDF required for Educational Mode")
                
                else:
                    full_prompt = f"""You are TORQ, an AI assistant. Provide detailed, helpful responses.

QUESTION: {prompt}

DETAILED RESPONSE:"""
                    st.info("🤖 Personal Assistant Mode")
                
                messages = [
                    {"role": "system", "content": "You are TORQ, a helpful AI assistant."},
                    {"role": "user", "content": full_prompt}
                ]
                
                response = call_groq(messages, api_key)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown('</div>', unsafe_allow_html=True)