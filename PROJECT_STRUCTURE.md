# TORQ Project Structure

Clean, organized structure for Streamlit deployment.

## 📁 Core Files

```
torq-app/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── pdf_processor.py          # PDF text extraction
├── vector_store.py           # Vector storage and search
├── torq_model.py            # Model interaction (legacy)
├── main.py                   # CLI version (legacy)
└── requirements.txt          # Python dependencies
```

## 📚 Documentation

```
├── README.md                 # Main project documentation
└── GEMINI_SETUP.md          # Gemini API setup guide
```

## ⚙️ Configuration

```
├── .streamlit/
│   ├── config.toml          # Streamlit UI configuration
│   └── secrets.toml         # API keys (gitignored)
├── .gitignore               # Git ignore rules
└── .python-version          # Python version specification
```

## 🗂️ Data Directories (gitignored)

```
├── torq_storage/            # Persistent PDF storage
├── torq_vectordb/           # Vector database files
└── uploads/                 # Uploaded PDF files
```

## 🚀 Launch Scripts

```
├── TORQ_Launcher.bat        # Windows launcher
├── open_torq.bat            # Open in browser
└── start_torq_local.bat     # Start local server
```

## 📦 Total Files

- **Core Python**: 5 files
- **Documentation**: 2 files
- **Configuration**: 4 files
- **Scripts**: 3 files
- **Total**: 14 files (clean and minimal!)

## 🗑️ Removed Files

Cleaned up 40+ unnecessary files:
- ❌ Vercel deployment files (api/, templates/, vercel.json)
- ❌ Android APK files (buildozer, mobile apps)
- ❌ Old deployment guides (HuggingFace, PythonAnywhere, Render)
- ❌ Backup files (app_backup.py, app_fixed.py)
- ❌ Redundant documentation (10+ markdown files)
- ❌ Docker/container files (Dockerfile, Procfile)

## 🎯 Focus

Project is now focused exclusively on:
- ✅ Streamlit Cloud deployment
- ✅ Google Gemini API integration
- ✅ Clean, maintainable codebase
- ✅ Essential documentation only

## 📊 File Sizes

| File | Purpose | Size |
|------|---------|------|
| app.py | Main application | ~25 KB |
| vector_store.py | Vector operations | ~5 KB |
| pdf_processor.py | PDF processing | ~3 KB |
| config.py | Configuration | ~2 KB |
| requirements.txt | Dependencies | ~1 KB |

## 🔄 Workflow

1. **Development**: Edit `app.py`
2. **Testing**: Run `streamlit run app.py`
3. **Commit**: `git add . && git commit -m "message"`
4. **Deploy**: `git push origin main` (auto-deploys to Streamlit Cloud)

## 📝 Key Files Explained

### app.py
Main Streamlit application with:
- UI components
- Chat interface
- PDF upload handling
- Gemini API integration
- Session state management

### vector_store.py
Vector storage using:
- TF-IDF vectorization
- Cosine similarity search
- Document chunking
- Metadata tracking

### pdf_processor.py
PDF processing with:
- PyPDF2 for text extraction
- Multi-page support
- Error handling

### config.py
Configuration for:
- Model settings
- API endpoints
- Default parameters

### requirements.txt
Dependencies:
- streamlit
- google-generativeai
- PyPDF2
- scikit-learn
- numpy

## 🎨 Streamlit Config

### config.toml
- Dark theme (purple accent)
- Custom colors
- Upload size limits
- Server settings

### secrets.toml (local only)
- GEMINI_API_KEY
- Never committed to git

## 🚀 Deployment

### Streamlit Cloud
- Auto-deploys on git push
- Secrets managed in dashboard
- Free hosting
- Custom domain support

### Requirements
- Python 3.9+
- Gemini API key
- GitHub repository

## 📈 Future Enhancements

Possible additions:
- [ ] Multiple PDF support
- [ ] Export chat history
- [ ] Custom themes
- [ ] Advanced search filters
- [ ] User authentication
- [ ] Database integration

## 🔗 Links

- **Live App**: https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/
- **GitHub**: https://github.com/AjayRaju-18/torq-app
- **Documentation**: See README.md and GEMINI_SETUP.md

---

**Last Updated**: April 5, 2026
**Version**: 2.0 (Streamlit-only, Gemini-powered)
