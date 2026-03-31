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

# Persistent storage functions
def get_storage_path():
    """Get the path for persistent storage"""
    storage_dir = "torq_storage"
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    return storage_dir

def save_vector_store(vector_store, filename="vector_store.pkl"):
    """Save vector store to disk"""
    storage_path = get_storage_path()
    file_path = os.path.join(storage_path, filename)
    
    # Create a serializable version of the vector store
    store_data = {
        'documents': vector_store.documents,
        'original_documents': vector_store.original_documents,
        'metadata': vector_store.metadata,
        'document_vectors': vector_store.document_vectors.toarray() if vector_store.document_vectors is not None else None,
        'vectorizer_vocabulary': vector_store.vectorizer.vocabulary_ if hasattr(vector_store.vectorizer, 'vocabulary_') else None,
        'vectorizer_params': {
            'max_features': vector_store.vectorizer.max_features,
            'stop_words': vector_store.vectorizer.stop_words,
            'ngram_range': vector_store.vectorizer.ngram_range,
            'min_df': vector_store.vectorizer.min_df,
            'max_df': vector_store.vectorizer.max_df
        }
    }
    
    with open(file_path, 'wb') as f:
        pickle.dump(store_data, f)
    
    return True

def load_vector_store(filename="vector_store.pkl"):
    """Load vector store from disk"""
    storage_path = get_storage_path()
    file_path = os.path.join(storage_path, filename)
    
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'rb') as f:
            store_data = pickle.load(f)
        
        # Recreate vector store
        vector_store = SimpleVectorStore()
        vector_store.documents = store_data['documents']
        vector_store.original_documents = store_data['original_documents']
        vector_store.metadata = store_data['metadata']
        
        # Recreate vectorizer with saved vocabulary
        if store_data['vectorizer_vocabulary']:
            vector_store.vectorizer = TfidfVectorizer(
                vocabulary=store_data['vectorizer_vocabulary'],
                **store_data['vectorizer_params']
            )
            
            # Recreate document vectors
            if store_data['document_vectors'] is not None:
                from scipy.sparse import csr_matrix
                vector_store.document_vectors = csr_matrix(store_data['document_vectors'])
        
        return vector_store
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None

def save_pdf_info(pdf_name, chunk_count):
    """Save PDF information"""
    storage_path = get_storage_path()
    info_file = os.path.join(storage_path, "pdf_info.json")
    
    pdf_info = {
        'name': pdf_name,
        'chunk_count': chunk_count,
        'upload_date': datetime.now().isoformat(),
        'last_accessed': datetime.now().isoformat()
    }
    
    with open(info_file, 'w') as f:
        json.dump(pdf_info, f)

def get_pdf_info():
    """Get PDF information"""
    storage_path = get_storage_path()
    info_file = os.path.join(storage_path, "pdf_info.json")
    
    if not os.path.exists(info_file):
        return None
    
    try:
        with open(info_file, 'r') as f:
            return json.load(f)
    except:
        return None

def clear_persistent_storage():
    """Clear all persistent storage"""
    storage_path = get_storage_path()
    if os.path.exists(storage_path):
        shutil.rmtree(storage_path)
        os.makedirs(storage_path)
    return True
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
        # Also clear persistent storage
        clear_persistent_storage()
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

# Chat History Management
def save_chat_history(session_id, title, messages, mode):
    """Save chat history to session state"""
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = []
    
    chat_data = {
        'id': session_id,
        'title': title,
        'messages': messages.copy(),
        'mode': mode,
        'timestamp': datetime.now().isoformat(),
        'created': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # Remove existing chat with same ID
    st.session_state.chat_histories = [
        chat for chat in st.session_state.chat_histories 
        if chat['id'] != session_id
    ]
    
    # Add new chat at the beginning
    st.session_state.chat_histories.insert(0, chat_data)
    
    # Keep only last 20 chats
    st.session_state.chat_histories = st.session_state.chat_histories[:20]

def load_chat_history(chat_id):
    """Load a specific chat history"""
    if 'chat_histories' not in st.session_state:
        return None
    
    for chat in st.session_state.chat_histories:
        if chat['id'] == chat_id:
            return chat
    return None

def generate_chat_title(first_message):
    """Generate a title from the first message"""
    if len(first_message) > 50:
        return first_message[:47] + "..."
    return first_message

def get_conversation_context(messages, max_context=5):
    """Get recent conversation context for better responses"""
    if len(messages) <= 1:
        return ""
    
    recent_messages = messages[-max_context:]
    context_parts = []
    
    for msg in recent_messages:
        role = "Human" if msg["role"] == "user" else "Assistant"
        context_parts.append(f"{role}: {msg['content']}")
    
    return "\n".join(context_parts)
def call_groq(messages, api_key):
    import requests
    
    if not api_key:
        return "Error: GROQ API key not found. Please check your Streamlit secrets configuration."
    
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
                               headers=headers, json=data, timeout=30)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return f"Error: Unexpected API response format: {result}"
        
        elif response.status_code == 401:
            return "Error: Invalid GROQ API key. Please check your API key in Streamlit secrets."
        
        elif response.status_code == 429:
            return "Error: GROQ API rate limit exceeded. Please try again in a moment."
        
        elif response.status_code == 500:
            return "Error: GROQ API server error. Please try again later."
        
        else:
            return f"Error: GROQ API returned status {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return "Error: Request to GROQ API timed out. Please check your internet connection."
    
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to GROQ API. Please check your internet connection."
    
    except requests.exceptions.RequestException as e:
        return f"Error: Network request failed: {str(e)}"
    
    except KeyError as e:
        return f"Error: Missing key in API response: {str(e)}"
    
    except Exception as e:
        return f"Error: Unexpected error calling GROQ API: {str(e)}"

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
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Main header */
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
    
    /* Mode selector (like ChatGPT model selector) */
    .mode-selector {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 1rem 0;
        gap: 0.5rem;
    }
    
    .mode-dropdown {
        background: #f9fafb;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        color: #374151;
        cursor: pointer;
        min-width: 200px;
        text-align: center;
    }
    
    .mode-dropdown:hover {
        background: #f3f4f6;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #e5e7eb;
        padding: 1rem;
        z-index: 1000;
    }
    
    .input-wrapper {
        max-width: 800px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Sidebar styles */
    .sidebar-header {
        padding: 1rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .new-chat-btn {
        width: 100%;
        background: #10b981;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem;
        font-weight: 500;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .new-chat-btn:hover {
        background: #059669;
    }
    
    /* Chat history items */
    .chat-item {
        padding: 0.75rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        cursor: pointer;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    
    .chat-item:hover {
        background: #f9fafb;
        border-color: #d1d5db;
    }
    
    .chat-item-title {
        font-size: 0.9rem;
        color: #374151;
        font-weight: 500;
        margin-bottom: 0.25rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .chat-item-meta {
        font-size: 0.75rem;
        color: #6b7280;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* PDF upload section */
    .pdf-section {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .pdf-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .status-personal {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .status-educational {
        background: #fef3c7;
        color: #92400e;
    }
    
    /* Message styling */
    .stChatMessage {
        max-width: 100%;
    }
    
    /* Bottom padding for fixed input */
    .main-content {
        padding-bottom: 120px;
    }
    
    /* Custom buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        border: 1px solid #d1d5db;
        background: white;
        color: #374151;
    }
    
    .stButton > button:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }
    
    /* File uploader styling */
    .stFileUploader {
        border: 1px dashed #d1d5db;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: #f9fafb;
        border: 1px solid #d1d5db;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_store' not in st.session_state:
    # Try to load existing vector store first
    loaded_store = load_vector_store()
    if loaded_store:
        st.session_state.vector_store = loaded_store
    else:
        st.session_state.vector_store = SimpleVectorStore()
        st.session_state.vector_store.clear_all()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "personal"

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if 'chat_histories' not in st.session_state:
    st.session_state.chat_histories = []

if 'pdf_loaded' not in st.session_state:
    # Check if there's a saved PDF
    pdf_info = get_pdf_info()
    st.session_state.pdf_loaded = pdf_info is not None

# Header
st.markdown("""
<div class="chat-header">
    <h1 class="chat-title">TORQ</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar - ChatGPT style
with st.sidebar:
    # New Chat Button
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    if st.button("+ New chat", key="new_chat", help="Start a new conversation"):
        # Save current chat if it has messages
        if st.session_state.messages:
            title = generate_chat_title(st.session_state.messages[0]["content"])
            save_chat_history(
                st.session_state.current_chat_id,
                title,
                st.session_state.messages,
                st.session_state.current_mode
            )
        
        # Start new chat
        st.session_state.messages = []
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat History
    st.markdown('<div class="sidebar-title">Recent chats</div>', unsafe_allow_html=True)
    
    if st.session_state.chat_histories:
        for chat in st.session_state.chat_histories[:15]:  # Show last 15 chats
            mode_icon = "🤖" if chat['mode'] == "personal" else "📚"
            
            # Create clickable chat item
            if st.button(f"{chat['title']}", key=f"chat_{chat['id']}", help=f"{mode_icon} {chat['created']}"):
                # Save current chat before switching
                if st.session_state.messages:
                    current_title = generate_chat_title(st.session_state.messages[0]["content"])
                    save_chat_history(
                        st.session_state.current_chat_id,
                        current_title,
                        st.session_state.messages,
                        st.session_state.current_mode
                    )
                
                # Load selected chat
                st.session_state.messages = chat['messages'].copy()
                st.session_state.current_mode = chat['mode']
                st.session_state.current_chat_id = chat['id']
                st.rerun()
    else:
        st.markdown('<div style="color: #6b7280; font-size: 0.9rem; padding: 1rem; text-align: center;">No conversations yet</div>', unsafe_allow_html=True)
    
    # Clear all chats
    if st.session_state.chat_histories:
        st.markdown("---")
        if st.button("Clear conversations", type="secondary"):
            st.session_state.chat_histories = []
            st.success("All conversations cleared")
            st.rerun()

# Main content area
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Mode selector (like ChatGPT model dropdown)
mode_options = {
    "🤖 Personal Assistant": "personal",
    "📚 Educational Mode": "educational"
}

current_mode_display = "🤖 Personal Assistant" if st.session_state.current_mode == "personal" else "📚 Educational Mode"

selected_mode = st.selectbox(
    "Choose mode:",
    options=list(mode_options.keys()),
    index=0 if st.session_state.current_mode == "personal" else 1,
    key="mode_selector",
    label_visibility="collapsed"
)

# Update mode if changed
if mode_options[selected_mode] != st.session_state.current_mode:
    st.session_state.current_mode = mode_options[selected_mode]
    st.rerun()

# Status indicator
if st.session_state.current_mode == "personal":
    st.markdown('<div class="status-badge status-personal">🤖 Personal Assistant Active</div>', unsafe_allow_html=True)
else:
    if len(st.session_state.vector_store.documents) > 0:
        st.markdown('<div class="status-badge status-educational">📚 Educational Mode - PDF Loaded</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-educational">📚 Educational Mode - No PDF Loaded</div>', unsafe_allow_html=True)

# PDF Upload for Educational Mode (near search area)
if st.session_state.current_mode == "educational":
    # Check for existing PDF
    pdf_info = get_pdf_info()
    
    if pdf_info:
        # Show existing PDF info
        st.success(f"📚 PDF Loaded: **{pdf_info['name']}** ({pdf_info['chunk_count']} chunks)")
        st.info(f"📅 Uploaded: {datetime.fromisoformat(pdf_info['upload_date']).strftime('%Y-%m-%d %H:%M')}")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ Remove PDF", type="secondary", help="Clear the current PDF and upload a new one"):
                cleared = st.session_state.vector_store.clear_all()
                if cleared:
                    st.success("PDF removed successfully")
                    st.rerun()
    else:
        # Show upload interface
        with st.expander("📄 Upload PDF for Educational Mode", expanded=True):
            uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'], key="pdf_uploader")
            
            if uploaded_file and st.button("Process PDF", type="primary"):
                with st.spinner("Processing and saving PDF..."):
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
                    
                    # Add documents to vector store
                    st.session_state.vector_store.add_documents(documents)
                    
                    # Save vector store and PDF info persistently
                    save_vector_store(st.session_state.vector_store)
                    save_pdf_info(uploaded_file.name, len(chunks))
                    
                    os.remove(temp_path)
                    st.success(f"✅ Processed and saved {len(chunks)} chunks from {uploaded_file.name}")
                    st.info("📱 PDF will be available across all devices and app restarts!")
                    st.rerun()

# Chat Interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about mechanical engineering..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Auto-save chat if this is the first message
    if len(st.session_state.messages) == 1:
        title = generate_chat_title(prompt)
        save_chat_history(
            st.session_state.current_chat_id,
            title,
            st.session_state.messages,
            st.session_state.current_mode
        )
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Get API key from Streamlit secrets or environment
            api_key = None
            try:
                # First try Streamlit secrets (for cloud deployment)
                api_key = st.secrets.get("GROQ_API_KEY")
            except:
                pass
            
            if not api_key:
                # Fallback to environment variable (for local development)
                api_key = os.getenv('GROQ_API_KEY')
            
            if not api_key:
                response = """
**API Key Missing** 🔑

For local development, set the API key as an environment variable:
```bash
export GROQ_API_KEY="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"
```

Or create a `.streamlit/secrets.toml` file with:
```toml
GROQ_API_KEY = "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"
```
"""
            else:
                # Get conversation context
                conversation_context = get_conversation_context(st.session_state.messages[:-1])
                
                if st.session_state.current_mode == "educational" and len(st.session_state.vector_store.documents) > 0:
                    # Educational Mode - Use PDF content with conversation context
                    search_results = st.session_state.vector_store.search(prompt)
                    if isinstance(search_results, tuple) and len(search_results) == 2:
                        context_docs, sources = search_results
                    else:
                        context_docs = search_results
                        sources = []
                    
                    if context_docs:
                        context = "\n\n---RELEVANT CONTENT---\n\n".join(context_docs[:4])
                        
                        full_prompt = f"""You are TORQ, a mechanical engineering educational assistant. Based on the PDF content and conversation history, answer the user's question.

CONVERSATION HISTORY:
{conversation_context}

INSTRUCTIONS:
- Use the PDF content as your primary knowledge source
- Consider the conversation history for context and continuity
- Extract core meaning and concepts from the PDF content
- Provide educational explanations with step-by-step reasoning
- Connect concepts from the PDF to give comprehensive answers
- Reference previous parts of our conversation when relevant
- Always indicate that your answer is based on the uploaded educational material

PDF CONTENT FROM UPLOADED DOCUMENT:
{context}

CURRENT QUESTION: {prompt}

EDUCATIONAL RESPONSE (based on PDF content and conversation):"""
                        
                        unique_sources = list(set(sources)) if sources else []
                        st.info(f"📖 Analyzing content from: {', '.join(unique_sources)} | Found {len(context_docs)} relevant sections")
                        
                    else:
                        full_prompt = f"""Based on our conversation history:
{conversation_context}

The uploaded PDF doesn't contain information relevant to your question: "{prompt}". 

Please ask questions related to the content in your uploaded educational material, or switch to Personal Assistant mode for general questions."""
                        st.warning("🔍 No relevant content found in the uploaded PDF for this question.")
                
                elif st.session_state.current_mode == "educational" and len(st.session_state.vector_store.documents) == 0:
                    # Educational Mode but no PDFs
                    full_prompt = "Please upload a PDF document first to use Educational Mode, or switch to Personal Assistant mode for general assistance."
                    st.error("� Educational Mode requires a PDF to be uploaded first.")
                
                else:
                    # Personal Assistant Mode - ChatGPT-like with conversation memory
                    full_prompt = f"""You are TORQ, an intelligent and helpful AI assistant specializing in mechanical engineering. You have extensive knowledge and maintain conversation continuity.

CONVERSATION HISTORY:
{conversation_context}

INSTRUCTIONS:
- Consider our previous conversation for context and continuity
- Reference earlier parts of our discussion when relevant
- Provide detailed, educational explanations
- Be conversational and engaging like ChatGPT
- Cover all areas of mechanical engineering comprehensively
- Build upon previous topics we've discussed

CURRENT QUESTION: {prompt}

RESPONSE (considering our conversation history):"""
                    
                    mode_emoji = "🤖" if st.session_state.current_mode == "personal" else "📚"
                    st.info(f"{mode_emoji} Personal Assistant Mode - Answering with conversation memory")
                
                # Prepare messages for API call
                system_message = "You are TORQ, a helpful AI assistant specializing in mechanical engineering. Maintain conversation continuity and provide educational, detailed responses."
                
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": full_prompt}
                ]
                
                response = call_groq(messages, api_key)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Auto-save updated chat
            if len(st.session_state.messages) > 1:
                title = generate_chat_title(st.session_state.messages[0]["content"])
                save_chat_history(
                    st.session_state.current_chat_id,
                    title,
                    st.session_state.messages,
                    st.session_state.current_mode
                )

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)  # Close main-content