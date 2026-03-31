import gradio as gr
import os
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from torq_model import TORQModel
from datetime import datetime

# Initialize TORQ
torq_model = TORQModel()
pdf_processor = PDFProcessor()
vector_store = VectorStore()

def upload_pdf(file):
    """Process uploaded PDF"""
    if file is None:
        return "No file uploaded"
    
    try:
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
        return f"✅ Successfully processed {filename} - Added {len(chunks)} chunks"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

def chat(message, history, use_rag):
    """Chat with TORQ"""
    if not message:
        yield history
        return
    
    try:
        conv_history = []
        if history:
            for human, assistant in history:
                conv_history.append({'role': 'user', 'content': human})
                conv_history.append({'role': 'assistant', 'content': assistant})
        
        if use_rag:
            result = torq_model.generate_response(message, conv_history)
            response = result['answer']
            if result.get('sources'):
                response += f"\n\n📚 Sources: {', '.join(result['sources'])}"
        else:
            response = torq_model.generate_chat_response(message, conv_history)
        
        history.append((message, response))
        yield history
    
    except Exception as e:
        history.append((message, f"Error: {str(e)}"))
        yield history

# Create Gradio interface
with gr.Blocks(title="TORQ") as demo:
    gr.Markdown("""
    # 🤖 TORQ - Mechanical Engineering Assistant
    ### Powered by GROQ LLM with RAG
    
    Upload mechanical engineering PDFs to train the model, then chat!
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📄 Upload PDFs")
            pdf_input = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
                type="filepath"
            )
            upload_btn = gr.Button("Process PDF", variant="primary")
            upload_status = gr.Textbox(label="Status", lines=3)
            
            gr.Markdown("### ⚙️ Settings")
            rag_toggle = gr.Checkbox(
                label="Enable RAG Mode",
                value=True,
                info="Use uploaded PDFs"
            )
        
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat")
            chatbot = gr.Chatbot(height=500, type="messages")
            msg = gr.Textbox(
                label="Your message",
                placeholder="Ask about mechanical engineering...",
                lines=2
            )
            with gr.Row():
                submit = gr.Button("Send", variant="primary")
                clear = gr.Button("Clear")
    
    # Event handlers
    upload_btn.click(
        fn=upload_pdf,
        inputs=[pdf_input],
        outputs=[upload_status]
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
    
    msg.submit(
        fn=chat,
        inputs=[msg, chatbot, rag_toggle],
        outputs=[chatbot]
    ).then(
        lambda: "",
        None,
        [msg]
    )
    
    clear.click(lambda: [], None, chatbot)

demo.launch()
