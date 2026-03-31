# TORQ - Mechanical Engineering RAG Model

TORQ is a specialized mechanical engineering assistant powered by GROQ's LLM and trained on mechanical engineering textbooks using RAG (Retrieval Augmented Generation).

## Features

- 🤖 ChatGPT-like web interface
- 📄 Upload PDFs directly through the UI
- 💬 Conversation history with memory
- 🔄 Toggle between RAG mode and normal chatbot mode
- 📚 Automatic PDF processing and training
- 💾 Persistent conversation storage

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the web application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage

### Web Interface

1. **Upload PDFs**: Click the "Upload PDF" button in the sidebar to upload mechanical engineering books
2. **Start Chatting**: Type your questions in the input box at the bottom
3. **RAG Mode Toggle**: Use the toggle switch to enable/disable RAG (retrieval from uploaded PDFs)
4. **Conversation History**: All conversations are saved in the sidebar - click to reload them
5. **New Chat**: Click "New Chat" to start a fresh conversation

### RAG Mode vs Normal Mode

- **RAG Mode ON**: TORQ retrieves relevant information from uploaded PDFs and uses it to answer questions
- **RAG Mode OFF**: TORQ acts as a normal chatbot using its general knowledge

## Architecture

- **Frontend**: Clean ChatGPT-like UI with dark theme
- **Backend**: Flask web server
- **PDF Processing**: Automatic text extraction and chunking
- **Vector Store**: ChromaDB with sentence-transformers for semantic search
- **LLM**: GROQ's llama-3.1-8b-instant for response generation
- **Memory**: Conversation history with context awareness

## Configuration

Edit `config.py` to adjust:
- GROQ API key and model
- Chunk size and overlap
- Number of retrieved documents
- Embedding model
- Vector database path
