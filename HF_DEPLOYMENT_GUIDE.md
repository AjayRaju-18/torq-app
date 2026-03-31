# Step-by-Step Guide: Deploy TORQ to Hugging Face Spaces

## Step 1: Delete Old Space (if exists)
1. Go to https://huggingface.co/spaces/ajay180805/torq-app
2. Click on "Settings" tab
3. Scroll down and click "Delete this Space"
4. Confirm deletion

## Step 2: Create New Hugging Face Space
1. Go to https://huggingface.co/new-space
2. Fill in the details:
   - **Owner**: Your username (ajay180805)
   - **Space name**: `torq-app`
   - **License**: Apache 2.0 (or your choice)
   - **Select the Space SDK**: Choose **Gradio**
   - **Space hardware**: CPU basic (free tier)
   - **Visibility**: Public or Private (your choice)
3. Click "Create Space"

## Step 3: Link GitHub Repository to Space
1. After creating the space, you'll see the space page
2. Click on "Settings" tab
3. Scroll to "Repository" section
4. Under "Linked repositories", click "Link a repository"
5. Select "GitHub"
6. Authorize Hugging Face to access your GitHub (if not already done)
7. Select your repository: `AjayRaju-18/torq-app`
8. Branch: `main`
9. Click "Link repository"

## Step 4: Add Environment Variable (GROQ API Key)
1. Still in Settings tab
2. Scroll to "Repository secrets" section
3. Click "New secret"
4. Name: `GROQ_API_KEY`
5. Value: `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`
6. Click "Add secret"

## Step 5: Verify Files in Space
The space should automatically sync from GitHub. Verify these files exist:
- `app.py` (main Gradio app)
- `requirements.txt` (dependencies)
- `config.py` (configuration)
- `pdf_processor.py` (PDF processing)
- `vector_store.py` (ChromaDB vector store)
- `torq_model.py` (GROQ LLM integration)
- `README.md` (documentation)

## Step 6: Wait for Build
1. Go to "App" tab
2. The space will automatically build and deploy
3. You'll see logs showing:
   - Installing dependencies
   - Loading models
   - Starting Gradio app
4. Wait 2-5 minutes for first build

## Step 7: Test the App
Once deployed:
1. You'll see the TORQ interface
2. Test PDF upload:
   - Click "Upload PDF"
   - Select a mechanical engineering PDF
   - Click "Process PDF"
   - Wait for success message
3. Test chat:
   - Enable "RAG Mode" checkbox
   - Type a question about the PDF
   - Click "Send"
   - Verify response includes sources
4. Test normal chat:
   - Disable "RAG Mode" checkbox
   - Ask a general question
   - Verify it responds without PDF context

## Troubleshooting

### If build fails with dependency errors:
1. Go to "Files" tab in your space
2. Click on `requirements.txt`
3. Verify it contains:
```
groq
pypdf2
chromadb<0.5.0
sentence-transformers<3.0.0
python-dotenv
numpy<2.0.0
```

### If app crashes on startup:
1. Check "Logs" tab for error messages
2. Verify `GROQ_API_KEY` is set in Settings > Repository secrets
3. Try restarting the space: Settings > "Factory reboot"

### If GitHub sync doesn't work:
1. Settings > Linked repositories > Unlink
2. Re-link the repository
3. Or manually upload files:
   - Go to "Files" tab
   - Click "Add file" > "Upload files"
   - Upload all Python files and requirements.txt

## Your Space URL
Once deployed, your app will be available at:
https://huggingface.co/spaces/ajay180805/torq-app

## Updating the App
After linking GitHub, any push to the `main` branch will automatically update the space:
```bash
git add .
git commit -m "Update message"
git push
```

The space will rebuild automatically within 1-2 minutes.
