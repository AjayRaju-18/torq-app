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

# Custom CSS for Perplexity-like UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Mode Selection Cards */
    .mode-card {
        background: white;
        border: 2px solid #e1e5e9;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .mode-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }
    
    .mode-card.active {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8edff 100%);
    }
    
    .mode-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .mode-description {
        color: #718096;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .mode-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Chat Interface */
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    /* Sidebar Styles */
    .sidebar-section {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .sidebar-title {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    /* Chat History Styles */
    .chat-history-item {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .chat-history-item:hover {
        border-color: #667eea;
        background: #f8f9ff;
    }
    
    .chat-history-title {
        font-weight: 500;
        color: #2d3748;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }
    
    .chat-history-time {
        color: #718096;
        font-size: 0.75rem;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem 0;
    }
    
    .status-personal {
        background: #e6fffa;
        color: #234e52;
        border: 1px solid #81e6d9;
    }
    
    .status-educational {
        background: #fef5e7;
        color: #744210;
        border: 1px solid #f6e05e;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styles */
    .stButton > button {
        border-radius: 8px;
        border: none;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_store' not in st.session_state:
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

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🤖 TORQ</h1>
    <p class="main-subtitle">Advanced Mechanical Engineering AI Assistant</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📄 Document Management</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload PDF for Educational Mode", type=['pdf'])
    
    col1, col2 = st.columns(2)
    with col1:
        if uploaded_file and st.button("📚 Process PDF", type="primary"):
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
        if st.button("🗑️ Clear PDFs", type="secondary"):
            cleared = st.session_state.vector_store.clear_all()
            if cleared:
                st.success("🗑️ All PDF content cleared")
                st.rerun()
    
    # PDF Status
    if len(st.session_state.vector_store.documents) > 0:
        st.success(f"📚 {len(st.session_state.vector_store.documents)} document chunks loaded")
    else:
        st.warning("⚠️ No PDFs uploaded for Educational Mode")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat History Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">💬 Chat History</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat", type="primary"):
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
    
    with col2:
        if st.button("🗑️ Clear All", type="secondary"):
            st.session_state.chat_histories = []
            st.session_state.messages = []
            st.success("All chat history cleared")
            st.rerun()
    
    # Display chat history
    if st.session_state.chat_histories:
        for chat in st.session_state.chat_histories[:10]:  # Show last 10 chats
            mode_emoji = "🤖" if chat['mode'] == "personal" else "📚"
            if st.button(f"{mode_emoji} {chat['title']}", key=f"chat_{chat['id']}", help=f"Created: {chat['created']}"):
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
        st.info("No previous chats")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Mode Selection
col1, col2 = st.columns(2)

with col1:
    personal_active = "active" if st.session_state.current_mode == "personal" else ""
    if st.button("🤖 Personal Assistant", key="personal_mode", help="General AI assistant for any questions"):
        st.session_state.current_mode = "personal"
        st.rerun()
    
    st.markdown(f"""
    <div class="mode-card {personal_active}">
        <div class="mode-icon">🤖</div>
        <div class="mode-title">Personal Assistant</div>
        <div class="mode-description">
            General AI assistant powered by advanced language models. 
            Ask anything about mechanical engineering, get explanations, 
            solve problems, and have natural conversations.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    educational_active = "active" if st.session_state.current_mode == "educational" else ""
    if st.button("📚 Educational Mode", key="educational_mode", help="Learn from your uploaded PDF documents"):
        st.session_state.current_mode = "educational"
        st.rerun()
    
    st.markdown(f"""
    <div class="mode-card {educational_active}">
        <div class="mode-icon">📚</div>
        <div class="mode-title">Educational Mode</div>
        <div class="mode-description">
            Learn from your uploaded PDF documents. Get detailed explanations 
            based on your study materials, textbooks, and reference documents 
            with contextual understanding.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Current Mode Status
if st.session_state.current_mode == "personal":
    st.markdown('<div class="status-indicator status-personal">🤖 Personal Assistant Mode Active</div>', unsafe_allow_html=True)
else:
    if len(st.session_state.vector_store.documents) > 0:
        st.markdown('<div class="status-indicator status-educational">📚 Educational Mode Active - PDF Loaded</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator status-educational">📚 Educational Mode Active - Upload PDF to Start</div>', unsafe_allow_html=True)

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
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                response = "Please set GROQ_API_KEY in Streamlit secrets"
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