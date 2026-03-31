from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from torq_model import TORQModel
import json

app = Flask(__name__)
app.secret_key = 'torq_secret_key_2024'
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize TORQ
torq_model = TORQModel()
pdf_processor = PDFProcessor()
vector_store = VectorStore()

# Store conversations in memory (use database in production)
conversations = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process PDF and add to vector store
        text = pdf_processor.extract_text_from_pdf(filepath)
        chunks = pdf_processor.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                'content': chunk,
                'metadata': {
                    'source': filename,
                    'chunk_id': i,
                    'upload_date': datetime.now().isoformat()
                }
            })
        
        vector_store.add_documents(documents)
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {filename}',
            'chunks': len(chunks)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    conversation_id = data.get('conversation_id')
    use_rag = data.get('use_rag', True)
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Create new conversation if needed
    if not conversation_id or conversation_id not in conversations:
        conversation_id = str(uuid.uuid4())
        conversations[conversation_id] = {
            'id': conversation_id,
            'title': user_message[:50] + ('...' if len(user_message) > 50 else ''),
            'messages': [],
            'created_at': datetime.now().isoformat()
        }
    
    # Add user message to conversation
    conversations[conversation_id]['messages'].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    try:
        # Generate response
        if use_rag:
            result = torq_model.generate_response(
                user_message,
                conversations[conversation_id]['messages']
            )
            response = result['answer']
            sources = result.get('sources', [])
        else:
            response = torq_model.generate_chat_response(
                user_message,
                conversations[conversation_id]['messages']
            )
            sources = []
        
        # Add assistant message to conversation
        conversations[conversation_id]['messages'].append({
            'role': 'assistant',
            'content': response,
            'sources': sources,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'response': response,
            'sources': sources,
            'conversation_id': conversation_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/conversations', methods=['GET'])
def get_conversations():
    conv_list = [
        {
            'id': conv['id'],
            'title': conv['title'],
            'created_at': conv['created_at'],
            'message_count': len(conv['messages'])
        }
        for conv in conversations.values()
    ]
    # Sort by created_at descending
    conv_list.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(conv_list)

@app.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    if conversation_id not in conversations:
        return jsonify({'error': 'Conversation not found'}), 404
    return jsonify(conversations[conversation_id])

@app.route('/conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    if conversation_id in conversations:
        del conversations[conversation_id]
        return jsonify({'success': True})
    return jsonify({'error': 'Conversation not found'}), 404

@app.route('/new_conversation', methods=['POST'])
def new_conversation():
    conversation_id = str(uuid.uuid4())
    return jsonify({'conversation_id': conversation_id})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
