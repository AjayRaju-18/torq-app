# TORQ - Vercel Deployment Guide

## ✅ Files Committed to GitHub

All Vercel deployment files have been successfully committed and pushed to your GitHub repository:
- `api/index.py` - Flask API for serverless functions
- `api/requirements.txt` - Python dependencies
- `templates/index_vercel.html` - ChatGPT-style frontend
- `vercel.json` - Vercel configuration

## 🚀 Deploy to Vercel

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New Project"
3. Import your repository: `AjayRaju-18/torq-app`
4. Vercel will auto-detect the configuration from `vercel.json`
5. Add environment variable:
   - Key: `GROQ_API_KEY`
   - Value: `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`
6. Click "Deploy"
7. Wait 2-3 minutes for deployment to complete
8. Your app will be live at: `https://torq-app-[random].vercel.app`

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts and add GROQ_API_KEY when asked
```

## 🎯 Features Included

- ✅ Personal Assistant Mode (ChatGPT-like chatbot)
- ✅ Educational Mode (RAG with PDF upload)
- ✅ PDF Upload & Processing
- ✅ Chat History (localStorage)
- ✅ Conversation Memory
- ✅ Dark Theme UI (ChatGPT-style)
- ✅ Mobile Responsive
- ✅ Session-based PDF persistence

## 🔧 Post-Deployment

After deployment:
1. Test Personal Assistant mode
2. Upload a PDF and test Educational mode
3. Verify chat history works
4. Test on mobile devices

## 📝 Important Notes

- Vercel serverless functions have a 10-second timeout on free tier
- PDF data is stored in session (not persistent across deployments)
- For persistent storage, consider adding a database (MongoDB, PostgreSQL)
- GROQ API key is stored as environment variable (secure)

## 🆓 Free Forever Hosting

Vercel free tier includes:
- Unlimited deployments
- 100GB bandwidth/month
- Automatic HTTPS
- Global CDN
- No credit card required

## 🔗 Your URLs

- GitHub Repo: https://github.com/AjayRaju-18/torq-app
- Streamlit App: https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/
- Vercel App: (will be generated after deployment)

## 🐛 Troubleshooting

If deployment fails:
1. Check build logs in Vercel dashboard
2. Verify `api/requirements.txt` has all dependencies
3. Ensure GROQ_API_KEY is set correctly
4. Check that Python version is compatible (3.9+)

## 📞 Support

If you encounter issues:
- Check Vercel deployment logs
- Verify environment variables are set
- Test API endpoints individually
- Check browser console for frontend errors
