"""
TORQ - Vercel Deployment
Flask API for Vercel serverless functions
"""

from flask import Flask, render_template, request, jsonify, session
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import PyPDF2
import json
from datetime import datetime
import uuid
import io
import requests

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'torq-secret-key-change-in-production')

# Simple vector store (same as Streamlit version)
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
    
    def to_dict(self):
        """Serialize for session storage"""
        return {
            'documents': self.documents,
            'original_documents': self.original_documents,
            'metadata': self.metadata
        }
    
    def from_dict(self, data):
        """Deserialize from session storage"""
        self.documents = data.get('documents', [])
        self.original_documents = data.get('original_documents', [])
        self.metadata = data.get('metadata', [])
        
        if self.documents:
            self.document_vectors = self.vectorizer.fit_transform(self.documents)

def extract_text_from_pdf(file_stream):
    """Extract text from PDF file stream"""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        for page in pdf_reader.pages:
            text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def split_text(text, chunk_size=500, overlap=50):
    """Split text into chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) > 30:
            chunks.append(' '.join(chunk_words))
    
    return chunks

def call_gemini(messages, api_key):
    """Call Gemini API"""
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
                finish_reason = result['candidates'][0].get('finishReason', '')
                if finish_reason == 'MAX_TOKENS':
                    content += "\n\n⚠️ *Response truncated. Ask me to continue.*"
                return content
            else:
                return "Error: Unexpected API response"
        
        elif response.status_code == 400:
            error_msg = response.json().get('error', {}).get('message', 'Bad request')
            return f"Error: {error_msg}"
        
        elif response.status_code == 403:
            return "Error: Invalid Gemini API key or API not enabled."
        
        elif response.status_code == 429:
            return "Error: Rate limit exceeded. Please try again in a minute."
        
        else:
            return f"Error: API returned status {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize session data
def get_vector_store():
    """Get or create vector store from session"""
    if 'vector_store_data' not in session:
        return SimpleVectorStore()
    
    vector_store = SimpleVectorStore()
    vector_store.from_dict(session['vector_store_data'])
    return vector_store

def save_vector_store(vector_store):
    """Save vector store to session"""
    session['vector_store_data'] = vector_store.to_dict()

@app.route('/')
def index():
    """Main page"""
    if 'messages' not in session:
        session['messages'] = []
    if 'current_mode' not in session:
        session['current_mode'] = 'personal'
    if 'chat_histories' not in session:
        session['chat_histories'] = []
    
    return render_template('index_vercel.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    prompt = data.get('prompt', '')
    mode = data.get('mode', 'personal')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    # Get API key
    api_key = os.environ.get('GEMINI_API_KEY', '')
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Add user message to session
    if 'messages' not in session:
        session['messages'] = []
    session['messages'].append({'role': 'user', 'content': prompt})
    
    # Generate response based on mode
    if mode == 'educational' and len(vector_store.documents) > 0:
        try:
            vector_store.validate_and_repair()
            context_docs, sources = vector_store.search(prompt)
            
            if context_docs:
                context = "\n\n".join(context_docs[:2])
                if len(context) > 2500:
                    context = context[:2500] + "..."
                
                full_prompt = f"""Based on PDF content, answer the question.

PDF CONTENT:
{context}

QUESTION: {prompt}

DETAILED ANSWER:"""
            else:
                full_prompt = f"The PDF doesn't contain relevant information for: '{prompt}'"
        
        except Exception as e:
            full_prompt = f"Error searching PDF: {str(e)}"
    
    elif mode == 'educational':
        response_text = "Please upload a PDF first to use Educational Mode."
        session['messages'].append({'role': 'assistant', 'content': response_text})
        session.modified = True
        return jsonify({'response': response_text, 'mode': mode})
    
    else:
        full_prompt = f"""You are TORQ, an AI assistant. Provide detailed, helpful responses.

QUESTION: {prompt}

DETAILED RESPONSE:"""
    
    messages = [
        {"role": "system", "content": "You are TORQ, a helpful AI assistant."},
        {"role": "user", "content": full_prompt}
    ]
    
    response_text = call_gemini(messages, api_key)
    
    # Add assistant response to session
    session['messages'].append({'role': 'assistant', 'content': response_text})
    session.modified = True
    
    return jsonify({'response': response_text, 'mode': mode})

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF upload"""
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(io.BytesIO(file.read()))
        chunks = split_text(text)
        
        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                'content': chunk,
                'metadata': {'source': file.filename, 'chunk_id': i}
            })
        
        # Add to vector store
        vector_store = get_vector_store()
        vector_store.add_documents(documents)
        save_vector_store(vector_store)
        
        # Save PDF info to session
        session['pdf_name'] = file.filename
        session['pdf_chunks'] = len(chunks)
        session.modified = True
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'chunks': len(chunks)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-pdf', methods=['POST'])
def clear_pdf():
    """Clear PDF data"""
    vector_store = SimpleVectorStore()
    save_vector_store(vector_store)
    
    if 'pdf_name' in session:
        del session['pdf_name']
    if 'pdf_chunks' in session:
        del session['pdf_chunks']
    
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/pdf-status', methods=['GET'])
def pdf_status():
    """Get PDF status"""
    pdf_name = session.get('pdf_name', None)
    pdf_chunks = session.get('pdf_chunks', 0)
    
    return jsonify({
        'loaded': pdf_name is not None,
        'filename': pdf_name,
        'chunks': pdf_chunks
    })

@app.route('/api/new-chat', methods=['POST'])
def new_chat():
    """Start new chat"""
    session['messages'] = []
    session.modified = True
    return jsonify({'success': True})

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get chat messages"""
    return jsonify({'messages': session.get('messages', [])})

# For Vercel serverless
app = app