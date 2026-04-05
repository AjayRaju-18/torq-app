# Fix Streamlit Cloud Secret Error

## ❌ Error You're Seeing
```
Environment Variable "GROQ_API_KEY" references Secret "groq_api_key", which does not exist.
Error: Invalid GROQ API key.
```

## 🔍 What's Wrong?
Your Streamlit Cloud app is looking for a secret called "groq_api_key" but it's not configured in the Streamlit Cloud dashboard.

## ✅ How to Fix (2 minutes)

### Step 1: Go to Streamlit Cloud Dashboard
1. Open your browser
2. Go to: **https://share.streamlit.io/**
3. Sign in with your GitHub account

### Step 2: Find Your TORQ App
1. You'll see your deployed apps
2. Find: **torq-app** (or the app showing the error)
3. Click on the app name

### Step 3: Open App Settings
1. Click the **⋮** (three dots) menu on the right side
2. Select **"Settings"**

### Step 4: Add the Secret
1. In the settings page, find the **"Secrets"** section
2. You'll see a text box for secrets
3. Delete any existing content in the box
4. Paste this EXACTLY:
```toml
GROQ_API_KEY = "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"
```
5. Click **"Save"** button

### Step 5: Reboot the App
1. After saving, click the **⋮** (three dots) menu again
2. Select **"Reboot app"**
3. Wait 30 seconds for the app to restart

### Step 6: Test the App
1. Open your app: https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/
2. Try asking a question in Personal Assistant mode
3. It should work now!

## 🎯 Visual Guide

```
Streamlit Cloud Dashboard
├── Your Apps
│   └── torq-app ← Click here
│       └── ⋮ (three dots) ← Click here
│           ├── Settings ← Click here
│           │   └── Secrets section
│           │       └── [Paste API key here]
│           │       └── Save ← Click here
│           └── Reboot app ← Click here after saving
```

## 📝 Important Notes

1. **Format Matters**: Make sure you paste the secret EXACTLY as shown above
2. **No Extra Spaces**: Don't add extra lines or spaces
3. **Quotes Required**: Keep the quotes around the API key
4. **Case Sensitive**: Use `GROQ_API_KEY` in all caps

## 🔄 Alternative: Redeploy from GitHub

If the above doesn't work:

1. Go to Streamlit Cloud dashboard
2. Click **⋮** → **Delete app**
3. Click **"New app"**
4. Select your repository: `AjayRaju-18/torq-app`
5. Main file path: `app.py`
6. Before deploying, click **"Advanced settings"**
7. In the Secrets box, paste:
```toml
GROQ_API_KEY = "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"
```
8. Click **"Deploy"**

## ✅ How to Verify It's Fixed

After rebooting, your app should:
- Load without errors
- Show the TORQ interface
- Respond to questions in Personal Assistant mode
- Allow PDF uploads in Educational mode

## 🐛 Still Not Working?

If you still see the error:

1. **Check the secret format**: Make sure there are no typos
2. **Wait a bit longer**: Sometimes it takes 1-2 minutes for changes to apply
3. **Clear browser cache**: Press `Ctrl + Shift + R` to hard refresh
4. **Check app logs**: In Streamlit dashboard, click "Manage app" → "Logs"

## 📞 Need More Help?

If the error persists:
1. Take a screenshot of the Secrets section in Streamlit dashboard
2. Take a screenshot of the error message
3. Check if the app is using the correct `app.py` file

---

## 🔐 About Streamlit Secrets

Streamlit Cloud uses a different secrets system than environment variables:
- Local development: Uses `.streamlit/secrets.toml` file
- Streamlit Cloud: Uses dashboard secrets configuration
- The dashboard secrets override the local file when deployed

This is why you need to add the secret in the dashboard even though it exists in your local file.
