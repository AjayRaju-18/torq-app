import streamlit as st
import os
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from torq_model import TORQModel
from datetime import datetime

# Page config
st.set_page_config(
    page_title="TORQ - Mechanical Engineering Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize TORQ
@st.cache_resource
def init_torq():
    return TORQModel(), PDFProcessor(), VectorStore()

torq_model, pdf_processor, vector_store = init_torq()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Custom CSS for ChatGPT-like dark theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, #202123, #343541);
    }
    .stChatMessage {
        background-color: #444654;
        border-radius: 8px;
    }
    .stButton>button {
        background-color: #10a37f;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0d8c6f;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 TORQ - Mechanical Engineering Assistant")
st.caption("Powered by GROQ LLM with RAG")

# Sidebar
with st.sidebar:
    st.header("📄 Upload PDFs")
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    
    if uploaded_file and st.button("Process PDF", type="primary"):
        with st.spinner("Processing PDF..."):
            try:
                # Save uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process PDF
                text = pdf_processor.extract_text_from_pdf(temp_path)
                chunks = pdf_processor.split_text(text)
                
                documents = []
                for i, chunk in enumerate(chunks):
                    documents.append({
                        'content': chunk,
                        'metadata': {
                            'source': uploaded_file.name,
                            'chunk_id': i,
                            'upload_date': datetime.now().isoformat()
                        }
                    })
                
                vector_store.add_documents(documents)
                os.remove(temp_path)
                
                st.success(f"✅ Successfully processed {uploaded_file.name} - Added {len(chunks)} chunks")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    st.header("⚙️ Settings")
    use_rag = st.checkbox("Enable RAG Mode", value=True, help="Use uploaded PDFs for context")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about mechanical engineering..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Convert history
                conv_history = []
                for msg in st.session_state.messages[:-1]:  # Exclude current message
                    conv_history.append({'role': msg['role'], 'content': msg['content']})
                
                # Generate response
                if use_rag:
                    result = torq_model.generate_response(prompt, conv_history)
                    response = result['answer']
                    if result.get('sources'):
                        response += f"\n\n📚 Sources: {', '.join(result['sources'])}"
                else:
                    response = torq_model.generate_chat_response(prompt, conv_history)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
