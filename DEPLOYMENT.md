# TORQ Deployment Guide

## Option 1: Deploy to Render (Recommended - Free)

1. **Create a GitHub Repository**
   - Go to https://github.com/new
   - Create a new repository (e.g., "torq-app")
   - Initialize with README

2. **Push Your Code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/torq-app.git
   git push -u origin main
   ```

3. **Deploy on Render**
   - Go to https://render.com and sign up (free)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the settings from render.yaml
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment

4. **Access Your App**
   - You'll get a URL like: https://torq-app.onrender.com
   - Share this URL to access from anywhere!

**Note**: Free tier sleeps after 15 minutes of inactivity. First request after sleep takes ~30 seconds.

---

## Option 2: Deploy to Railway (Easy - Free Tier)

1. **Push to GitHub** (same as above)

2. **Deploy on Railway**
   - Go to https://railway.app and sign up
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variable: `PORT=5000`
   - Railway will auto-deploy

3. **Get Your URL**
   - Click "Settings" → "Generate Domain"
   - You'll get a URL like: https://torq-app.up.railway.app

---

## Option 3: Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy**
   ```bash
   heroku login
   heroku create torq-app
   git push heroku main
   heroku open
   ```

---

## Option 4: Use Ngrok (Quick Testing - Temporary URL)

1. **Download Ngrok**
   - Go to https://ngrok.com/download
   - Sign up for free account

2. **Run Your App Locally**
   ```bash
   python app.py
   ```

3. **Expose with Ngrok**
   ```bash
   ngrok http 5000
   ```

4. **Share the URL**
   - Ngrok will give you a URL like: https://abc123.ngrok.io
   - This URL works from anywhere but expires when you close ngrok

---

## Option 5: Deploy to Google Cloud Run (Free Tier)

1. **Create Dockerfile** (already included)

2. **Deploy**
   ```bash
   gcloud run deploy torq --source . --platform managed --region us-central1 --allow-unauthenticated
   ```

---

## Important Notes

### Environment Variables
Make sure to set these on your deployment platform:
- `GROQ_API_KEY`: Your GROQ API key (if not hardcoded)
- `PORT`: Usually auto-set by the platform

### Persistent Storage
- Free tiers don't have persistent storage
- Uploaded PDFs and vector DB will reset on restart
- For production, use:
  - AWS S3 / Google Cloud Storage for PDFs
  - Pinecone / Weaviate for vector database

### Security
- Change `app.secret_key` in production
- Use environment variables for API keys
- Enable HTTPS (most platforms do this automatically)

---

## Recommended: Render Deployment

Render is the easiest and most reliable free option:
1. Push to GitHub
2. Connect to Render
3. Deploy automatically
4. Get a permanent URL

Your app will be live at: `https://your-app-name.onrender.com`
