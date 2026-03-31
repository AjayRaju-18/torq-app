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
    if not message or not message.strip():
        return history
    
    try:
        # Convert history to conversation format for the model
        conv_history = []
        if history:
            for item in history:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    conv_history.append({'role': 'user', 'content': item[0]})
                    conv_history.append({'role': 'assistant', 'content': item[1]})
        
        # Generate response
        if use_rag:
            result = torq_model.generate_response(message, conv_history)
            response = result['answer']
            if result.get('sources'):
                response += f"\n\n📚 Sources: {', '.join(result['sources'])}"
        else:
            response = torq_model.generate_chat_response(message, conv_history)
        
        # Return as list of [user, bot] pairs
        new_history = list(history) if history else []
        new_history.append([message, response])
        
        return new_history
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        new_history = list(history) if history else []
        new_history.append([message, error_msg])
        return new_history

# Custom CSS for ChatGPT-like dark theme
custom_css = """
.gradio-container {
    background: linear-gradient(to bottom, #202123, #343541) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
button.primary {
    background-color: #10a37f !important;
    border: none !important;
}
button.primary:hover {
    background-color: #0d8c6f !important;
}
"""

# Create Gradio interface
with gr.Blocks(css=custom_css, title="TORQ") as demo:
    
    gr.Markdown("""
    # 🤖 TORQ - Mechanical Engineering Assistant
    ### Powered by GROQ LLM with RAG
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
                info="Use uploaded PDFs for context"
            )
        
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat")
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(
                label="Your message",
                placeholder="Ask about mechanical engineering...",
                lines=2,
                show_label=False
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

if __name__ == "__main__":
    demo.launch()
