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
import base64

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

def call_gemini(messages, api_key):
    import requests
    
    if not api_key:
        return "Error: Gemini API key not found."
    
    # Convert OpenAI-style messages to Gemini format
    gemini_contents = []
    system_instruction = ""
    
    for msg in messages:
        if msg['role'] == 'system':
            system_instruction = msg['content']
        elif msg['role'] == 'user':
            gemini_contents.append({
                "role": "user",
                "parts": [{"text": msg['content']}]
            })
        elif msg['role'] == 'assistant':
            gemini_contents.append({
                "role": "model",
                "parts": [{"text": msg['content']}]
            })
    
    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    data = {
        "contents": gemini_contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
            "topP": 0.95,
            "topK": 40
        }
    }
    
    # Add system instruction if present
    if system_instruction:
        data["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Check if response was truncated
                finish_reason = result['candidates'][0].get('finishReason', '')
                if finish_reason == 'MAX_TOKENS':
                    content += "\n\n⚠️ *Response truncated due to length. Ask me to continue for more details.*"
                
                return content
            else:
                return f"Error: Unexpected API response"
        
        elif response.status_code == 400:
            error_msg = response.json().get('error', {}).get('message', 'Bad request')
            return f"Error: {error_msg}"
        
        elif response.status_code == 403:
            return "Error: Invalid Gemini API key or API not enabled."
        
        elif response.status_code == 429:
            return "Error: Rate limit exceeded. Please try again in a minute."
        
        else:
            return f"Error: API returned status {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "Error: Request timed out."
    
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Gemini API."
    
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

# Persistent storage functions using pickle files
def save_pdf_data(vector_store, pdf_name, pdf_content):
    """Save PDF data to persistent storage"""
    import pickle
    import os
    
    # Create storage directory if it doesn't exist
    storage_dir = "torq_storage"
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    
    if len(vector_store.documents) > 0:
        pdf_data = {
            'documents': vector_store.documents,
            'original_documents': vector_store.original_documents,
            'metadata': vector_store.metadata,
            'pdf_name': pdf_name,
            'pdf_content': pdf_content,  # Store actual PDF bytes
            'timestamp': datetime.now().isoformat(),
            'chunk_count': len(vector_store.documents)
        }
        
        # Save to file
        storage_path = os.path.join(storage_dir, "pdf_data.pkl")
        with open(storage_path, 'wb') as f:
            pickle.dump(pdf_data, f)
        
        # Also store in session state
        st.session_state['saved_pdf_data'] = pdf_data
        return True
    return False

def load_pdf_data(vector_store):
    """Load PDF data from persistent storage"""
    import pickle
    import os
    
    storage_path = os.path.join("torq_storage", "pdf_data.pkl")
    
    # Try loading from file first
    if os.path.exists(storage_path):
        try:
            with open(storage_path, 'rb') as f:
                pdf_data = pickle.load(f)
            
            vector_store.documents = pdf_data['documents']
            vector_store.original_documents = pdf_data['original_documents']
            vector_store.metadata = pdf_data['metadata']
            
            # Rebuild vectorizer and document vectors
            if vector_store.documents:
                vector_store.document_vectors = vector_store.vectorizer.fit_transform(vector_store.documents)
            
            # Store in session state
            st.session_state['saved_pdf_data'] = pdf_data
            
            return pdf_data
        except Exception as e:
            print(f"Error loading PDF data from file: {e}")
    
    # Fallback to session state
    if 'saved_pdf_data' in st.session_state:
        try:
            pdf_data = st.session_state['saved_pdf_data']
            vector_store.documents = pdf_data['documents']
            vector_store.original_documents = pdf_data['original_documents']
            vector_store.metadata = pdf_data['metadata']
            
            if vector_store.documents:
                vector_store.document_vectors = vector_store.vectorizer.fit_transform(vector_store.documents)
            
            return pdf_data
        except Exception as e:
            print(f"Error loading PDF data from session: {e}")
    
    return None

def clear_pdf_data():
    """Clear all PDF data"""
    import os
    
    storage_path = os.path.join("torq_storage", "pdf_data.pkl")
    if os.path.exists(storage_path):
        os.remove(storage_path)
    
    if 'saved_pdf_data' in st.session_state:
        del st.session_state['saved_pdf_data']
    
    if 'pdf_loaded_name' in st.session_state:
        del st.session_state['pdf_loaded_name']

def save_chat_history(chat_id, title, mode, messages):
    """Save chat to session state (works on Streamlit Cloud)."""
    from datetime import datetime
    
    histories = st.session_state.get('chat_histories', [])
    
    entry = {
        'id': chat_id,
        'title': title,
        'mode': mode,
        'messages': messages,
        'timestamp': datetime.now().isoformat()
    }

    # Update existing or insert at top
    for i, chat in enumerate(histories):
        if chat.get('id') == chat_id:
            histories[i] = entry
            return histories

    histories.insert(0, entry)
    return histories

def load_chat_histories():
    """Load from session state (always empty on first load — expected)."""
    return st.session_state.get('chat_histories', [])

# Streamlit app
st.set_page_config(
    page_title="TORQ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ChatGPT-like CSS with responsive design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background-color: transparent !important;
        padding: 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Header - Premium Glassmorphism */
    .chat-header {
        text-align: center;
        padding: 2rem 1rem;
        margin-bottom: 2rem;
        background: rgba(22, 33, 62, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        position: sticky;
        top: 0;
        z-index: 99;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    
    .chat-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a78bfa 0%, #fbcfe8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .chat-subtitle {
        color: rgba(255,255,255,0.7);
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    

    
    /* Chat messages - Glass bubbles */
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 0.75rem;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.3);
        color: #e5e7eb;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(139, 92, 246, 0.2);
        background: rgba(139, 92, 246, 0.2);
        border-color: rgba(139, 92, 246, 0.5);
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed rgba(139, 92, 246, 0.4);
        border-radius: 1rem;
        padding: 1.5rem;
        background: rgba(0, 0, 0, 0.2);
        transition: all 0.3s;
    }
    
    .stFileUploader:hover {
        border-color: #8b5cf6;
        background: rgba(139, 92, 246, 0.05);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #f3f4f6;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.5rem;
    }
    
    /* MOBILE RESPONSIVE constraints */
    @media (max-width: 768px) {
        .chat-header {
            padding: 1rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .chat-title { font-size: 1.8rem; }
        .chat-subtitle { font-size: 0.85rem; }
        
        /* Mobile sidebar */
        section[data-testid="stSidebar"] {
            width: 85% !important;
            max-width: 320px !important;
            background: rgba(22, 33, 62, 0.98);
        }
        
        /* Sidebar toggle button highly visible */
        button[kind="header"] {
            background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
            color: white !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
        }
        
        /* Fixed Chat input on mobile */
        .stChatInput {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            z-index: 1000 !important;
            background: rgba(26, 26, 46, 0.95) !important;
            padding: 1rem !important;
            border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px);
        }
        
        /* Padding to prevent chat hidden behind fixed input */
        .main .block-container {
            padding: 1rem 0.5rem 80px 0.5rem !important;
        }
    }
    
    /* TABLET & DESKTOP container sizing */
    @media (min-width: 769px) {
        .main .block-container {
            max-width: 1000px;
            padding: 0 2rem 5rem 2rem;
        }
    }
    
    /* Mode selector */
    .stSelectbox {
        margin-bottom: 1.5rem;
    }
    
    /* Smooth global animations */
    * {
        transition: background-color 0.3s ease, border-color 0.3s ease, transform 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = SimpleVectorStore()
    # Try to load saved PDF data
    loaded_pdf_data = load_pdf_data(st.session_state.vector_store)
    if loaded_pdf_data:
        st.session_state['pdf_loaded_name'] = loaded_pdf_data.get('pdf_name', 'Unknown PDF')
        st.session_state['pdf_chunk_count'] = loaded_pdf_data.get('chunk_count', 0)

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "personal"

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if 'chat_histories' not in st.session_state:
    st.session_state.chat_histories = load_chat_histories()

# Header
st.markdown("""
<div class="chat-header">
    <h1 class="chat-title">🤖 TORQ</h1>
    <p class="chat-subtitle">Your AI-Powered Assistant</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem; margin-bottom: 0.5rem;">
        <h2 style="color: #a78bfa; font-size: 1.4rem; font-weight: 700; margin: 0;">🤖 TORQ</h2>
        <p style="color: #9ca3af; font-size: 0.78rem; margin: 0.3rem 0 0 0;">AI Assistant History</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕ New Chat", key="new_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    if st.session_state.chat_histories:
        for chat in st.session_state.chat_histories[:15]:
            mode_icon = "🤖" if chat.get('mode', 'personal') == "personal" else "📚"
            label = f"{mode_icon} {chat.get('title', 'Chat')}"
            if st.button(label, key=f"chat_{chat.get('id', '')}", use_container_width=True):
                st.session_state.messages = chat.get('messages', []).copy()
                st.session_state.current_mode = chat.get('mode', 'personal')
                st.session_state.current_chat_id = chat.get('id', str(uuid.uuid4()))
                st.rerun()
    else:
        st.markdown("<p style='color:#9ca3af; font-size:0.85rem; padding: 0.5rem;'>No conversations yet. Start chatting!</p>", unsafe_allow_html=True)

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
    # Save current chat before switching mode
    if st.session_state.messages:
        title = generate_chat_title(st.session_state.messages[0]["content"])
        st.session_state.chat_histories = save_chat_history(
            st.session_state.current_chat_id,
            title,
            st.session_state.current_mode,
            st.session_state.messages
        )
    # Start a fresh chat in the new mode
    st.session_state.current_mode = mode_options[selected_mode]
    st.session_state.messages = []
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.rerun()

# PDF Upload for Educational Mode
if st.session_state.current_mode == "educational":
    # Show loaded PDF status if exists
    if 'pdf_loaded_name' in st.session_state and len(st.session_state.vector_store.documents) > 0:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"📚 **{st.session_state['pdf_loaded_name']}** is loaded and ready")
        with col2:
            if st.button("🗑️ Clear PDF", type="secondary"):
                st.session_state.vector_store.clear_all()
                clear_pdf_data()
                if 'pdf_loaded_name' in st.session_state:
                    del st.session_state['pdf_loaded_name']
                if 'pdf_chunk_count' in st.session_state:
                    del st.session_state['pdf_chunk_count']
                st.success("PDF cleared!")
                st.rerun()
    
    with st.expander("📄 Upload PDF", expanded=len(st.session_state.vector_store.documents) == 0):
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'], key="pdf_uploader", label_visibility="collapsed")
        
        if uploaded_file:
            if st.button("📤 Process PDF", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing PDF..."):
                    # Save PDF content
                    pdf_content = uploaded_file.getbuffer()
                    
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(pdf_content)
                    
                    text = extract_text_from_pdf(temp_path)
                    chunks = split_text(text)
                    
                    documents = []
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            'content': chunk,
                            'metadata': {'source': uploaded_file.name, 'chunk_id': i}
                        })
                    
                    st.session_state.vector_store.add_documents(documents)
                    
                    # Save PDF data for persistence with actual content
                    save_pdf_data(st.session_state.vector_store, uploaded_file.name, bytes(pdf_content))
                    st.session_state['pdf_loaded_name'] = uploaded_file.name
                    st.session_state['pdf_chunk_count'] = len(chunks)
                    
                    os.remove(temp_path)
                    
                    # Show success popup
                    st.balloons()
                    st.success(f"✅ **{uploaded_file.name}** processed successfully!")
                    st.info("� PDF saved permanently - will persist across sessions")
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
                api_key = st.secrets.get("GEMINI_API_KEY")
            except:
                pass
            
            if not api_key:
                api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                response = "⚠️ API key not configured. Please add GEMINI_API_KEY to Streamlit secrets."
            else:
                # Build conversation history for context
                messages = [{"role": "system", "content": "You are TORQ, a helpful AI assistant."}]
                
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
                            if len(context) > 2500:
                                context = context[:2500] + "..."
                            
                            # Get PDF name for reference
                            pdf_name = st.session_state.get('pdf_loaded_name', 'the uploaded PDF')
                            
                            # Add conversation history with PDF context
                            system_msg = f"""You are TORQ, an AI assistant. Answer questions based on the PDF content provided.

PDF CONTENT:
{context}

IMPORTANT: At the end of your answer, always add a reference line:
📚 Source: {pdf_name}

Use this content to answer questions. Maintain conversation continuity by remembering previous exchanges."""
                            
                            messages = [{"role": "system", "content": system_msg}]
                            
                            # Add recent conversation history (last 4 exchanges)
                            recent_messages = st.session_state.messages[-8:] if len(st.session_state.messages) > 8 else st.session_state.messages[:-1]
                            for msg in recent_messages:
                                messages.append({"role": msg["role"], "content": msg["content"]})
                            
                            # Add current question
                            messages.append({"role": "user", "content": prompt})
                        else:
                            pdf_name = st.session_state.get('pdf_loaded_name', 'the PDF')
                            messages.append({"role": "user", "content": f"The PDF '{pdf_name}' doesn't contain relevant information for: '{prompt}'"})
                            st.warning("⚠️ No relevant content found in PDF")
                    
                    except Exception as e:
                        messages.append({"role": "user", "content": f"Error searching PDF: {str(e)}"})
                
                elif st.session_state.current_mode == "educational":
                    messages.append({"role": "user", "content": "Please upload a PDF first to use Educational Mode."})
                    st.error("PDF required for Educational Mode")
                
                else:
                    # Personal Assistant Mode - include full conversation history
                    st.info("🤖 Personal Assistant Mode")
                    
                    # Add recent conversation history (last 6 exchanges = 12 messages)
                    recent_messages = st.session_state.messages[-12:] if len(st.session_state.messages) > 12 else st.session_state.messages[:-1]
                    for msg in recent_messages:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    # Add current question
                    messages.append({"role": "user", "content": prompt})
                
                response = call_gemini(messages, api_key)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Save history dynamically
            if len(st.session_state.messages) > 0:
                title = generate_chat_title(st.session_state.messages[0]["content"])
                st.session_state.chat_histories = save_chat_history(
                    st.session_state.current_chat_id,
                    title,
                    st.session_state.current_mode,
                    st.session_state.messages
                )

st.markdown('</div>', unsafe_allow_html=True)