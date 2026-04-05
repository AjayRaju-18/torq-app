"""
TORQ Mobile - Android APK Version
Native Android app with dynamic UI that mirrors the Streamlit functionality
"""

import os
import json
import uuid
import pickle
import shutil
from datetime import datetime
from threading import Thread
import requests

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

# Import your existing classes (no changes needed)
import sys
sys.path.append('.')
from app import SimpleVectorStore, extract_text_from_pdf, split_text, call_groq

class ChatMessage(BoxLayout):
    """Individual chat message widget"""
    def __init__(self, message, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)
        
        # Message styling
        if is_user:
            self.add_widget(Label(size_hint_x=0.2))  # Spacer
            msg_label = Label(
                text=message,
                text_size=(None, None),
                halign='right',
                valign='middle',
                color=(1, 1, 1, 1),
                canvas_before_color=(0.2, 0.6, 1, 1)
            )
        else:
            msg_label = Label(
                text=message,
                text_size=(None, None),
                halign='left',
                valign='middle',
                color=(0, 0, 0, 1),
                canvas_before_color=(0.9, 0.9, 0.9, 1)
            )
            self.add_widget(Label(size_hint_x=0.2))  # Spacer for assistant
        
        self.add_widget(msg_label)

class ChatHistoryItem(Button):
    """Chat history item in sidebar"""
    def __init__(self, chat_data, callback, **kwargs):
        super().__init__(**kwargs)
        self.chat_data = chat_data
        self.callback = callback
        self.text = f"{'🤖' if chat_data['mode'] == 'personal' else '📚'} {chat_data['title']}"
        self.size_hint_y = None
        self.height = dp(50)
        self.halign = 'left'
        self.bind(on_press=self.on_chat_select)
    
    def on_chat_select(self, instance):
        self.callback(self.chat_data)

class TORQMobileApp(App):
    """Main TORQ Mobile Application"""
    
    def build(self):
        # Initialize data
        self.vector_store = SimpleVectorStore()
        self.messages = []
        self.current_mode = "personal"
        self.current_chat_id = str(uuid.uuid4())
        self.chat_histories = []
        self.api_key = "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"
        
        # Load persistent data
        self.load_persistent_data()
        
        # Main layout
        main_layout = BoxLayout(orientation='horizontal')
        
        # Sidebar (30% width)
        sidebar = self.create_sidebar()
        main_layout.add_widget(sidebar)
        
        # Main content area (70% width)
        content_area = self.create_content_area()
        main_layout.add_widget(content_area)
        
        return main_layout
    
    def create_sidebar(self):
        """Create sidebar with chat history and controls"""
        sidebar = BoxLayout(
            orientation='vertical',
            size_hint_x=0.3,
            padding=[dp(10), dp(10)],
            spacing=dp(10)
        )
        
        # New Chat button
        new_chat_btn = Button(
            text="+ New Chat",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.1, 0.7, 0.3, 1)
        )
        new_chat_btn.bind(on_press=self.new_chat)
        sidebar.add_widget(new_chat_btn)
        
        # Chat history label
        sidebar.add_widget(Label(
            text="Recent Chats",
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1)
        ))
        
        # Chat history scroll view
        self.chat_history_scroll = ScrollView()
        self.chat_history_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )
        self.chat_history_layout.bind(minimum_height=self.chat_history_layout.setter('height'))
        self.chat_history_scroll.add_widget(self.chat_history_layout)
        sidebar.add_widget(self.chat_history_scroll)
        
        # Clear conversations button
        clear_btn = Button(
            text="Clear All",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_all_chats)
        sidebar.add_widget(clear_btn)
        
        self.update_chat_history()
        return sidebar
    
    def create_content_area(self):
        """Create main content area with chat interface"""
        content = BoxLayout(
            orientation='vertical',
            size_hint_x=0.7,
            padding=[dp(10), dp(10)],
            spacing=dp(10)
        )
        
        # Header
        header = Label(
            text="TORQ - AI Assistant",
            size_hint_y=None,
            height=dp(50),
            font_size='20sp',
            color=(0, 0, 0, 1)
        )
        content.add_widget(header)
        
        # Mode selector
        mode_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        mode_layout.add_widget(Label(text="Mode:", size_hint_x=0.2, color=(0, 0, 0, 1)))
        
        self.mode_spinner = Spinner(
            text="🤖 Personal Assistant",
            values=["🤖 Personal Assistant", "📚 Educational Mode"],
            size_hint_x=0.8
        )
        self.mode_spinner.bind(text=self.on_mode_change)
        mode_layout.add_widget(self.mode_spinner)
        
        content.add_widget(mode_layout)
        
        # PDF upload section (initially hidden)
        self.pdf_section = self.create_pdf_section()
        content.add_widget(self.pdf_section)
        
        # Chat messages scroll view
        self.chat_scroll = ScrollView()
        self.chat_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=[dp(5), dp(5)]
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        content.add_widget(self.chat_scroll)
        
        # Input area
        input_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )
        
        self.message_input = TextInput(
            hint_text="Ask me anything about mechanical engineering...",
            multiline=False,
            size_hint_x=0.8
        )
        self.message_input.bind(on_text_validate=self.send_message)
        
        send_btn = Button(
            text="Send",
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 1, 1)
        )
        send_btn.bind(on_press=self.send_message)
        
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_btn)
        content.add_widget(input_layout)
        
        return content
    
    def create_pdf_section(self):
        """Create PDF upload section"""
        pdf_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(0),  # Initially hidden
            spacing=dp(5)
        )
        
        # PDF status label
        self.pdf_status_label = Label(
            text="No PDF uploaded",
            size_hint_y=None,
            height=dp(30),
            color=(0.6, 0.6, 0.6, 1)
        )
        pdf_layout.add_widget(self.pdf_status_label)
        
        # PDF buttons
        pdf_btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        upload_btn = Button(
            text="📄 Upload PDF",
            background_color=(0.1, 0.7, 0.3, 1)
        )
        upload_btn.bind(on_press=self.upload_pdf)
        
        self.clear_pdf_btn = Button(
            text="🗑️ Clear PDF",
            background_color=(0.8, 0.2, 0.2, 1),
            disabled=True
        )
        self.clear_pdf_btn.bind(on_press=self.clear_pdf)
        
        pdf_btn_layout.add_widget(upload_btn)
        pdf_btn_layout.add_widget(self.clear_pdf_btn)
        pdf_layout.add_widget(pdf_btn_layout)
        
        return pdf_layout
    
    def on_mode_change(self, spinner, text):
        """Handle mode change"""
        if "Personal" in text:
            self.current_mode = "personal"
            self.pdf_section.height = dp(0)
        else:
            self.current_mode = "educational"
            self.pdf_section.height = dp(80)
        
        self.update_pdf_status()
    
    def update_pdf_status(self):
        """Update PDF status display"""
        if len(self.vector_store.documents) > 0:
            pdf_info = self.get_pdf_info()
            if pdf_info:
                self.pdf_status_label.text = f"📚 PDF: {pdf_info['name']} ({pdf_info['chunk_count']} chunks)"
                self.pdf_status_label.color = (0, 0.7, 0, 1)
                self.clear_pdf_btn.disabled = False
            else:
                self.pdf_status_label.text = f"📚 {len(self.vector_store.documents)} chunks loaded"
                self.pdf_status_label.color = (0, 0.7, 0, 1)
                self.clear_pdf_btn.disabled = False
        else:
            self.pdf_status_label.text = "No PDF uploaded"
            self.pdf_status_label.color = (0.6, 0.6, 0.6, 1)
            self.clear_pdf_btn.disabled = True
    
    def upload_pdf(self, instance):
        """Handle PDF upload"""
        # Create file chooser popup
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        filechooser = FileChooserListView(
            filters=['*.pdf'],
            path='/'
        )
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        select_btn = Button(text="Select PDF")
        cancel_btn = Button(text="Cancel")
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title="Select PDF File",
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def select_file(instance):
            if filechooser.selection:
                self.process_pdf(filechooser.selection[0])
            popup.dismiss()
        
        def cancel_selection(instance):
            popup.dismiss()
        
        select_btn.bind(on_press=select_file)
        cancel_btn.bind(on_press=cancel_selection)
        
        popup.open()
    
    def process_pdf(self, file_path):
        """Process selected PDF file"""
        try:
            # Show processing popup
            processing_popup = Popup(
                title="Processing PDF",
                content=Label(text="Processing PDF, please wait..."),
                size_hint=(0.6, 0.3),
                auto_dismiss=False
            )
            processing_popup.open()
            
            # Process PDF in thread to avoid blocking UI
            def process_in_thread():
                try:
                    text = extract_text_from_pdf(file_path)
                    chunks = split_text(text)
                    
                    documents = []
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            'content': chunk,
                            'metadata': {'source': os.path.basename(file_path), 'chunk_id': i}
                        })
                    
                    self.vector_store.add_documents(documents)
                    self.save_vector_store()
                    self.save_pdf_info(os.path.basename(file_path), len(chunks))
                    
                    # Update UI on main thread
                    Clock.schedule_once(lambda dt: self.pdf_processed_callback(processing_popup, len(chunks), os.path.basename(file_path)))
                    
                except Exception as e:
                    Clock.schedule_once(lambda dt: self.pdf_error_callback(processing_popup, str(e)))
            
            Thread(target=process_in_thread).start()
            
        except Exception as e:
            self.show_error(f"Error selecting PDF: {str(e)}")
    
    def pdf_processed_callback(self, popup, chunk_count, filename):
        """Callback when PDF processing is complete"""
        popup.dismiss()
        self.update_pdf_status()
        self.show_success(f"✅ Processed {chunk_count} chunks from {filename}")
    
    def pdf_error_callback(self, popup, error_msg):
        """Callback when PDF processing fails"""
        popup.dismiss()
        self.show_error(f"Error processing PDF: {error_msg}")
    
    def clear_pdf(self, instance):
        """Clear loaded PDF"""
        self.vector_store.clear_all()
        self.clear_persistent_storage()
        self.update_pdf_status()
        self.show_success("PDF content cleared")
    
    def send_message(self, instance):
        """Send message and get AI response"""
        message = self.message_input.text.strip()
        if not message:
            return
        
        # Add user message
        self.add_message(message, is_user=True)
        self.messages.append({"role": "user", "content": message})
        self.message_input.text = ""
        
        # Auto-save chat if first message
        if len(self.messages) == 1:
            self.save_current_chat()
        
        # Get AI response in thread
        def get_response():
            try:
                response = self.get_ai_response(message)
                Clock.schedule_once(lambda dt: self.add_ai_response(response))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.add_ai_response(f"Error: {str(e)}"))
        
        Thread(target=get_response).start()
        
        # Show thinking indicator
        self.add_message("🤔 Thinking...", is_user=False)
    
    def get_ai_response(self, prompt):
        """Get AI response using existing logic"""
        if self.current_mode == "educational" and len(self.vector_store.documents) > 0:
            # Educational mode with PDF
            try:
                self.vector_store.validate_and_repair()
                search_results = self.vector_store.search(prompt)
                
                if isinstance(search_results, tuple) and len(search_results) == 2:
                    context_docs, sources = search_results
                else:
                    context_docs = search_results
                    sources = []
                
                if context_docs:
                    context = "\n\n---SECTION---\n\n".join(context_docs[:2])
                    if len(context) > 3000:
                        context = context[:3000] + "...[truncated for length]"
                    
                    conversation_context = self.get_conversation_context()
                    if len(conversation_context) > 500:
                        conversation_context = conversation_context[:500] + "...[truncated]"
                    
                    full_prompt = f"""You are TORQ, a mechanical engineering educational assistant. Based on the PDF content, answer the user's question concisely.

RECENT CONVERSATION:
{conversation_context}

PDF CONTENT:
{context}

QUESTION: {prompt}

CONCISE ANSWER (based on PDF):"""
                else:
                    full_prompt = f"The PDF doesn't contain relevant information for: '{prompt}'. Please ask about content in your uploaded PDF, or switch to Personal Assistant mode."
            
            except Exception as e:
                return f"Error searching PDF content: {str(e)}"
        
        elif self.current_mode == "educational" and len(self.vector_store.documents) == 0:
            return "Please upload a PDF document first to use Educational Mode, or switch to Personal Assistant mode."
        
        else:
            # Personal Assistant mode
            conversation_context = self.get_conversation_context()
            if len(conversation_context) > 400:
                conversation_context = conversation_context[:400] + "...[truncated]"
            
            full_prompt = f"""You are TORQ, an AI assistant specializing in mechanical engineering. Provide concise, helpful responses.

RECENT CONVERSATION:
{conversation_context}

QUESTION: {prompt}

RESPONSE:"""
        
        # Call GROQ API
        messages = [
            {"role": "system", "content": "You are TORQ, a helpful AI assistant. Respond naturally and professionally."},
            {"role": "user", "content": full_prompt}
        ]
        
        return call_groq(messages, self.api_key)
    
    def get_conversation_context(self):
        """Get recent conversation context"""
        if len(self.messages) <= 1:
            return ""
        
        recent_messages = self.messages[-3:]
        context_parts = []
        
        for msg in recent_messages:
            role = "Human" if msg["role"] == "user" else "Assistant"
            content = msg['content']
            if len(content) > 200:
                content = content[:200] + "..."
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def add_ai_response(self, response):
        """Add AI response to chat"""
        # Remove thinking indicator
        if self.chat_layout.children and "Thinking" in self.chat_layout.children[0].children[0].text:
            self.chat_layout.remove_widget(self.chat_layout.children[0])
        
        self.add_message(response, is_user=False)
        self.messages.append({"role": "assistant", "content": response})
        
        # Auto-save updated chat
        if len(self.messages) > 1:
            self.save_current_chat()
    
    def add_message(self, message, is_user=True):
        """Add message to chat display"""
        msg_widget = ChatMessage(message, is_user)
        self.chat_layout.add_widget(msg_widget)
        
        # Auto-scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)
    
    def new_chat(self, instance):
        """Start new chat"""
        if self.messages:
            self.save_current_chat()
        
        self.messages = []
        self.current_chat_id = str(uuid.uuid4())
        self.chat_layout.clear_widgets()
        self.update_chat_history()
    
    def save_current_chat(self):
        """Save current chat to history"""
        if not self.messages:
            return
        
        title = self.generate_chat_title(self.messages[0]["content"])
        chat_data = {
            'id': self.current_chat_id,
            'title': title,
            'messages': self.messages.copy(),
            'mode': self.current_mode,
            'timestamp': datetime.now().isoformat(),
            'created': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # Remove existing chat with same ID
        self.chat_histories = [
            chat for chat in self.chat_histories 
            if chat['id'] != self.current_chat_id
        ]
        
        # Add new chat at the beginning
        self.chat_histories.insert(0, chat_data)
        
        # Keep only last 20 chats
        self.chat_histories = self.chat_histories[:20]
        
        self.save_chat_histories()
        self.update_chat_history()
    
    def generate_chat_title(self, first_message):
        """Generate title from first message"""
        if len(first_message) > 50:
            return first_message[:47] + "..."
        return first_message
    
    def load_chat(self, chat_data):
        """Load selected chat"""
        if self.messages:
            self.save_current_chat()
        
        self.messages = chat_data['messages'].copy()
        self.current_mode = chat_data['mode']
        self.current_chat_id = chat_data['id']
        
        # Update UI
        if self.current_mode == "personal":
            self.mode_spinner.text = "🤖 Personal Assistant"
            self.pdf_section.height = dp(0)
        else:
            self.mode_spinner.text = "📚 Educational Mode"
            self.pdf_section.height = dp(80)
        
        # Reload chat messages
        self.chat_layout.clear_widgets()
        for msg in self.messages:
            self.add_message(msg["content"], msg["role"] == "user")
    
    def update_chat_history(self):
        """Update chat history display"""
        self.chat_history_layout.clear_widgets()
        
        for chat in self.chat_histories[:15]:
            chat_item = ChatHistoryItem(chat, self.load_chat)
            self.chat_history_layout.add_widget(chat_item)
        
        if not self.chat_histories:
            no_chats_label = Label(
                text="No conversations yet",
                size_hint_y=None,
                height=dp(40),
                color=(0.6, 0.6, 0.6, 1)
            )
            self.chat_history_layout.add_widget(no_chats_label)
    
    def clear_all_chats(self, instance):
        """Clear all chat history"""
        self.chat_histories = []
        self.messages = []
        self.chat_layout.clear_widgets()
        self.save_chat_histories()
        self.update_chat_history()
        self.show_success("All conversations cleared")
    
    def show_success(self, message):
        """Show success popup"""
        popup = Popup(
            title="Success",
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        popup.open()
    
    # Persistent storage methods (using existing logic)
    def get_storage_path(self):
        """Get storage path for mobile"""
        from kivy.utils import platform
        if platform == 'android':
            from android.storage import primary_external_storage_path
            storage_dir = os.path.join(primary_external_storage_path(), 'torq_storage')
        else:
            storage_dir = "torq_storage"
        
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        return storage_dir
    
    def save_vector_store(self):
        """Save vector store to disk"""
        storage_path = self.get_storage_path()
        file_path = os.path.join(storage_path, "vector_store.pkl")
        
        store_data = {
            'documents': self.vector_store.documents,
            'original_documents': self.vector_store.original_documents,
            'metadata': self.vector_store.metadata,
            'document_vectors': self.vector_store.document_vectors.toarray() if self.vector_store.document_vectors is not None else None,
            'vectorizer_vocabulary': self.vector_store.vectorizer.vocabulary_ if hasattr(self.vector_store.vectorizer, 'vocabulary_') else None,
            'vectorizer_params': {
                'max_features': self.vector_store.vectorizer.max_features,
                'stop_words': self.vector_store.vectorizer.stop_words,
                'ngram_range': self.vector_store.vectorizer.ngram_range,
                'min_df': self.vector_store.vectorizer.min_df,
                'max_df': self.vector_store.vectorizer.max_df
            }
        }
        
        with open(file_path, 'wb') as f:
            pickle.dump(store_data, f)
    
    def load_vector_store(self):
        """Load vector store from disk"""
        storage_path = self.get_storage_path()
        file_path = os.path.join(storage_path, "vector_store.pkl")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'rb') as f:
                store_data = pickle.load(f)
            
            vector_store = SimpleVectorStore()
            vector_store.documents = store_data['documents']
            vector_store.original_documents = store_data['original_documents']
            vector_store.metadata = store_data['metadata']
            
            if store_data['vectorizer_vocabulary'] and store_data['documents']:
                from sklearn.feature_extraction.text import TfidfVectorizer
                vector_store.vectorizer = TfidfVectorizer(
                    vocabulary=store_data['vectorizer_vocabulary'],
                    **store_data['vectorizer_params']
                )
                vector_store.vectorizer.fit(vector_store.documents)
                
                if store_data['document_vectors'] is not None:
                    from scipy.sparse import csr_matrix
                    vector_store.document_vectors = csr_matrix(store_data['document_vectors'])
                else:
                    vector_store.document_vectors = vector_store.vectorizer.transform(vector_store.documents)
            
            return vector_store
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return None
    
    def save_pdf_info(self, pdf_name, chunk_count):
        """Save PDF information"""
        storage_path = self.get_storage_path()
        info_file = os.path.join(storage_path, "pdf_info.json")
        
        pdf_info = {
            'name': pdf_name,
            'chunk_count': chunk_count,
            'upload_date': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat()
        }
        
        with open(info_file, 'w') as f:
            json.dump(pdf_info, f)
    
    def get_pdf_info(self):
        """Get PDF information"""
        storage_path = self.get_storage_path()
        info_file = os.path.join(storage_path, "pdf_info.json")
        
        if not os.path.exists(info_file):
            return None
        
        try:
            with open(info_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def save_chat_histories(self):
        """Save chat histories"""
        storage_path = self.get_storage_path()
        file_path = os.path.join(storage_path, "chat_histories.json")
        
        with open(file_path, 'w') as f:
            json.dump(self.chat_histories, f)
    
    def load_chat_histories(self):
        """Load chat histories"""
        storage_path = self.get_storage_path()
        file_path = os.path.join(storage_path, "chat_histories.json")
        
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def clear_persistent_storage(self):
        """Clear all persistent storage"""
        storage_path = self.get_storage_path()
        if os.path.exists(storage_path):
            shutil.rmtree(storage_path)
            os.makedirs(storage_path)
    
    def load_persistent_data(self):
        """Load all persistent data on startup"""
        # Load vector store
        loaded_store = self.load_vector_store()
        if loaded_store:
            self.vector_store = loaded_store
            self.vector_store.validate_and_repair()
        
        # Load chat histories
        self.chat_histories = self.load_chat_histories()

if __name__ == '__main__':
    TORQMobileApp().run()