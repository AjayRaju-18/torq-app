import gradio as gr
import os
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from torq_model import TORQModel
from datetime import datetime
import uuid

# Initialize TORQ
torq_model = TORQModel()
pdf_processor = PDFProcessor()
vector_store = VectorStore()

# Store conversations
conversations = {}

def upload_pdf(file):
    """Process uploaded PDF"""
    if file is None:
        return "No file uploaded"
    
    try:
        # Process PDF
        text = pdf_processor.extract_text_from_pdf(file.name)
        chunks = pdf_processor.split_text(text)
        
        documents = []
        filename = os.path.basename(file.name)
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
        return f"✅ Successfully processed {filename} - Added {len(chunks)} chunks to knowledge base"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

def chat(message, history, use_rag):
    """Chat with TORQ"""
    if not message:
        return history
    
    try:
        # Create conversation history format
        conv_history = []
        for human, assistant in history:
            conv_history.append({'role': 'user', 'content': human})
            conv_history.append({'role': 'assistant', 'content': assistant})
        
        # Generate response
        if use_rag:
            result = torq_model.generate_response(message, conv_history)
            response = result['answer']
            if result.get('sources'):
                response += f"\n\n📚 Sources: {', '.join(result['sources'])}"
        else:
            response = torq_model.generate_chat_response(message, conv_history)
        
        return response
    
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="TORQ - Mechanical Engineering Assistant") as demo:
    gr.Markdown("""
    # 🤖 TORQ - Mechanical Engineering Assistant
    ### Powered by GROQ LLM with RAG
    
    Upload mechanical engineering PDFs to train the model, then chat with TORQ!
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📄 Upload PDFs")
            pdf_input = gr.File(
                label="Upload Mechanical Engineering PDF",
                file_types=[".pdf"],
                type="filepath"
            )
            upload_btn = gr.Button("Process PDF", variant="primary")
            upload_status = gr.Textbox(label="Status", lines=3)
            
            gr.Markdown("### ⚙️ Settings")
            rag_toggle = gr.Checkbox(
                label="Enable RAG Mode",
                value=True,
                info="Use uploaded PDFs for answers"
            )
        
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat with TORQ")
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(
                label="Your message",
                placeholder="Ask me anything about mechanical engineering...",
                lines=2
            )
            with gr.Row():
                submit = gr.Button("Send", variant="primary")
                clear = gr.Button("Clear Chat")
    
    gr.Markdown("""
    ---
    **Tips:**
    - Upload PDFs first to enable RAG mode
    - Toggle RAG off for general mechanical engineering questions
    - TORQ remembers conversation context
    """)
    
    # Event handlers
    upload_btn.click(
        fn=upload_pdf,
        inputs=[pdf_input],
        outputs=[upload_status]
    )
    
    msg.submit(
        fn=chat,
        inputs=[msg, chatbot, rag_toggle],
        outputs=[chatbot]
    ).then(
        lambda: "",
        None,
        [msg]
    )
    
    submit.click(
        fn=chat,
        inputs=[msg, chatbot, rag_toggle],
        outputs=[chatbot]
    ).then(
        lambda: "",
        None,
        [msg]
    )
    
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
