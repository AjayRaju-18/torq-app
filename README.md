# TORQ - Mechanical Engineering RAG Chatbot

A RAG-based AI assistant powered by Google Gemini for mechanical engineering queries and PDF document analysis.

## 🚀 Features

- **Personal Assistant Mode**: General chatbot powered by Gemini 2.5 Flash
- **Educational Mode**: RAG-based Q&A from uploaded PDF documents
- **PDF Processing**: Upload and analyze technical documents
- **Chat History**: Persistent conversation memory
- **Dark Theme**: ChatGPT-style modern UI

## 🌐 Live Demo

**Streamlit Cloud**: https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.5 Flash
- **Vector Store**: TF-IDF with scikit-learn
- **PDF Processing**: PyPDF2
- **Deployment**: Streamlit Cloud

## 📦 Installation

### Prerequisites
- Python 3.9+
- Google Gemini API key (free from https://aistudio.google.com/app/apikey)

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/AjayRaju-18/torq-app.git
cd torq-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API key:
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your_api_key_here"
```

4. Run the app:
```bash
streamlit run app.py
```

5. Open browser at: http://localhost:8501

## 🔑 Get Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API key"
4. Copy your API key

### Free Tier Limits:
- 15 requests/minute
- 1 million tokens/day
- No credit card required

## 📁 Project Structure

```
torq-app/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── pdf_processor.py            # PDF text extraction
├── vector_store.py             # Vector storage and search
├── torq_model.py              # Model interaction logic
├── requirements.txt            # Python dependencies
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml           # API keys (local only)
├── torq_storage/              # Persistent storage
├── torq_vectordb/             # Vector database
└── uploads/                   # Uploaded PDFs
```

## 🚀 Deployment to Streamlit Cloud

1. Push code to GitHub
2. Go to: https://share.streamlit.io/
3. Click "New app"
4. Select your repository
5. Set main file: `app.py`
6. Add secret in dashboard:
```
GEMINI_API_KEY = "your_api_key_here"
```
7. Deploy!

## 💡 Usage

### Personal Assistant Mode
- Ask general questions
- Get detailed explanations
- Conversational AI assistance

### Educational Mode
1. Upload a PDF document
2. Wait for processing
3. Ask questions about the content
4. Get answers based on the document

## 🔧 Configuration

### Streamlit Config (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#8b5cf6"
backgroundColor = "#1a1a2e"
secondaryBackgroundColor = "#16213e"
textColor = "#ffffff"

[server]
maxUploadSize = 200
```

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key

## 📊 Features in Detail

### Vector Store
- TF-IDF vectorization
- Cosine similarity search
- Chunk-based document processing
- Persistent storage

### PDF Processing
- Multi-page support
- Text extraction
- Automatic chunking (500 words, 50 overlap)
- Metadata tracking

### Chat Memory
- Session-based storage
- Conversation history
- Context-aware responses

## 🐛 Troubleshooting

### "Invalid API key" error
- Verify API key in Streamlit secrets
- Check key at: https://aistudio.google.com/app/apikey

### "Rate limit exceeded"
- Free tier: 15 requests/minute
- Wait 60 seconds and retry

### PDF upload fails
- Max file size: 200MB
- Supported format: PDF only
- Check file isn't corrupted

## 📚 Documentation

- `GET_GEMINI_API_KEY.md` - How to get Gemini API key
- `SETUP_GEMINI_NOW.md` - Quick setup guide
- `FIX_STREAMLIT_SECRET.md` - Fix secret configuration issues
- `GEMINI_MIGRATION_COMPLETE.md` - Migration details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Links

- **Live App**: https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/
- **GitHub**: https://github.com/AjayRaju-18/torq-app
- **Gemini API**: https://aistudio.google.com/app/apikey
- **Streamlit**: https://streamlit.io/

## 👨‍💻 Author

Created by Ajay Raju

## 🙏 Acknowledgments

- Google Gemini for the AI model
- Streamlit for the framework
- scikit-learn for vector operations
