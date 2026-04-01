# Fix 500 Server Error on Streamlit Cloud

## 🔴 Problem
Your TORQ app shows "500 Internal Server Error" when accessed via:
https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/

## 🔍 Common Causes

1. **Missing dependencies** in requirements.txt
2. **Import errors** from missing packages
3. **API key not configured** in Streamlit secrets
4. **Memory issues** from large files
5. **Syntax errors** in recent code changes

## ✅ Solution Steps

### Step 1: Check Streamlit Cloud Logs

1. Go to https://share.streamlit.io/
2. Find your TORQ app
3. Click "Manage app"
4. Check the logs for error messages

### Step 2: Verify requirements.txt

Make sure your `requirements.txt` has all dependencies:

```txt
streamlit
pypdf2
scikit-learn
numpy
requests
scipy
```

### Step 3: Check Streamlit Secrets

1. In Streamlit Cloud dashboard
2. Click your app → "Settings" → "Secrets"
3. Add:

```toml
GROQ_API_KEY = "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"
```

### Step 4: Replace app.py with Fixed Version

The current `app.py` might have issues. Replace it with `app_fixed.py`:

```bash
# In your local repository
copy app_fixed.py app.py

# Commit and push
git add app.py
git commit -m "Fix 500 error - simplified app"
git push
```

### Step 5: Reboot the App

1. Go to Streamlit Cloud dashboard
2. Click "Reboot app"
3. Wait 2-3 minutes for restart

### Step 6: Clear Browser Cache

1. Open browser in incognito/private mode
2. Try accessing the app again
3. Or clear browser cache and cookies

## 🚀 Quick Fix - Redeploy

If the above doesn't work, redeploy from scratch:

### Option A: Reboot from Streamlit Dashboard

1. Go to https://share.streamlit.io/
2. Find TORQ app
3. Click "⋮" menu → "Reboot app"
4. Wait for restart

### Option B: Delete and Redeploy

1. Delete the current app from Streamlit Cloud
2. Create new app:
   - Repository: `AjayRaju-18/torq-app`
   - Branch: `main`
   - Main file: `app.py`
3. Add secrets (GROQ_API_KEY)
4. Deploy

## 🔧 Alternative: Use Simplified Version

I've created `app_fixed.py` which is a simplified version without:
- Persistent storage (which might cause issues on Streamlit Cloud)
- Complex imports
- File system operations

To use it:

```bash
# Rename current app
mv app.py app_backup.py

# Use fixed version
cp app_fixed.py app.py

# Push to GitHub
git add .
git commit -m "Use simplified app version"
git push
```

## 📱 For Android APK

While fixing the Streamlit app, you can still use the APK with a different approach:

### Option 1: Use Local Server

1. Run TORQ locally:
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

2. Get your local IP (e.g., 10.152.55.149)

3. Create APK with local URL:
   - Use WebIntoApp.com
   - Enter URL: `http://10.152.55.149:8501`
   - This works on your local network

### Option 2: Wait for Streamlit Fix

1. Fix the Streamlit Cloud app first
2. Once it's working online
3. Then create APK with the working URL

### Option 3: Use Alternative Hosting

Deploy to:
- **Heroku** (free tier)
- **Railway** (free tier)
- **Render** (free tier)
- **PythonAnywhere** (free tier)

Then use that URL for the APK.

## 🐛 Debug Checklist

- [ ] Check Streamlit Cloud logs
- [ ] Verify requirements.txt has all packages
- [ ] Confirm GROQ_API_KEY in secrets
- [ ] Try app_fixed.py version
- [ ] Reboot app from dashboard
- [ ] Clear browser cache
- [ ] Test in incognito mode
- [ ] Check GitHub repository is up to date

## 💡 Most Likely Fix

The 500 error is usually caused by:

1. **Missing scipy** in requirements.txt
2. **API key not in secrets**
3. **Import error** from recent changes

**Quick fix:**
1. Add `scipy` to requirements.txt
2. Add API key to Streamlit secrets
3. Reboot app

Your app should be working again within 5 minutes! 🎉