# How to Get Free Google Gemini API Key

## 🎯 Overview
Google Gemini offers a generous free tier with 15 requests per minute and 1 million tokens per day - perfect for TORQ!

## 📝 Step-by-Step Guide

### Step 1: Go to Google AI Studio
1. Open your browser
2. Go to: **https://aistudio.google.com/app/apikey**
3. Sign in with your Google account (Gmail)

### Step 2: Create API Key
1. You'll see the "API keys" page
2. Click the **"Create API key"** button
3. You'll see two options:
   - **Create API key in new project** (recommended for new users)
   - **Create API key in existing project** (if you have a Google Cloud project)
4. Click **"Create API key in new project"**
5. Wait 5-10 seconds

### Step 3: Copy Your API Key
1. Your API key will appear (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
2. Click the **"Copy"** button
3. Save it somewhere safe (you'll need it in the next step)

### Step 4: Important - Restrict Your API Key (Optional but Recommended)
1. Click on the API key you just created
2. Click **"Edit API key"**
3. Under "API restrictions", select **"Restrict key"**
4. Select **"Generative Language API"**
5. Click **"Save"**

This prevents unauthorized use of your API key.

## ✅ Your API Key Format
Your Gemini API key will look like this:
```
AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## 🆓 Free Tier Limits
- **15 requests per minute**
- **1 million tokens per day**
- **1,500 requests per day**
- No credit card required!
- No expiration date

This is more than enough for personal use and testing!

## 🔗 Quick Links
- Get API Key: https://aistudio.google.com/app/apikey
- Gemini Documentation: https://ai.google.dev/docs
- Pricing: https://ai.google.dev/pricing

## 📋 What's Next?
After getting your API key:
1. Copy the API key
2. I'll update TORQ to use Gemini instead of GROQ
3. Add the key to your Streamlit secrets
4. Deploy and test!

## 🎁 Why Gemini?
- ✅ Completely free (no credit card)
- ✅ Higher rate limits than GROQ
- ✅ Better for long responses
- ✅ Supports longer context
- ✅ More reliable uptime
- ✅ Made by Google

## 🐛 Troubleshooting

### Can't access Google AI Studio?
- Make sure you're signed in with a Google account
- Try using an incognito/private browser window
- Clear your browser cache

### API key not working?
- Make sure you copied the entire key
- Check if API restrictions are too strict
- Verify the Generative Language API is enabled

### Rate limit errors?
- Free tier: 15 requests/minute
- Wait a minute and try again
- Consider upgrading to paid tier if needed (but free is usually enough)
