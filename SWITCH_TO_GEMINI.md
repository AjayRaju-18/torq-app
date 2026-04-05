# ✅ TORQ Switched to Google Gemini API

## 🎉 What Changed?

TORQ now uses Google Gemini API instead of GROQ. Gemini offers:
- ✅ **Completely FREE** (no credit card required)
- ✅ **15 requests/minute** (better than GROQ)
- ✅ **1 million tokens/day** (very generous)
- ✅ **Better responses** (Gemini 1.5 Flash model)
- ✅ **More reliable** (Google infrastructure)

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Get Your Free Gemini API Key (2 minutes)

1. Go to: **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API key"**
4. Click **"Create API key in new project"**
5. Copy your API key (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

### Step 2: Add to Streamlit Cloud (1 minute)

1. Go to: **https://share.streamlit.io/**
2. Click your **torq-app**
3. Click **⋮** → **Settings**
4. In **Secrets** section, paste:
```
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```
5. Replace `YOUR_API_KEY_HERE` with your actual key
6. Click **Save**
7. Click **⋮** → **Reboot app**

### Step 3: Test Your App

1. Open: https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/
2. Try Personal Assistant mode
3. Upload a PDF and try Educational mode
4. Everything should work perfectly!

---

## 💻 For Local Development

If you want to run TORQ locally:

1. Open `.streamlit/secrets.toml`
2. Replace the content with:
```toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```
3. Save the file
4. Run: `streamlit run app.py`

---

## 🌐 For Vercel Deployment

If you're deploying to Vercel:

1. Go to Vercel dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add new variable:
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key
5. Redeploy: `vercel --prod`

---

## 📊 Gemini vs GROQ Comparison

| Feature | Gemini (NEW) | GROQ (OLD) |
|---------|--------------|------------|
| Cost | FREE forever | FREE with limits |
| Requests/min | 15 | 14 |
| Tokens/day | 1,000,000 | ~100,000 |
| Model | Gemini 1.5 Flash | Llama 3.1 8B |
| Response Quality | Excellent | Good |
| Reliability | Very High | Medium |
| Setup | Easy | Easy |

---

## 🔧 What Was Updated?

### Files Modified:
1. ✅ `app.py` - Main Streamlit app
2. ✅ `api/index.py` - Vercel API
3. ✅ `.streamlit/secrets.toml` - Local secrets
4. ✅ `vercel.json` - Vercel config

### Changes Made:
- Replaced `call_groq()` with `call_gemini()`
- Updated API endpoint to Gemini
- Changed message format to Gemini's structure
- Updated all API key references
- Improved error handling

---

## 🐛 Troubleshooting

### Error: "Invalid Gemini API key"
**Solution**: 
- Make sure you copied the entire API key
- Check for extra spaces or quotes
- Verify the key is from: https://aistudio.google.com/app/apikey

### Error: "API not enabled"
**Solution**:
- Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
- Click "Enable"
- Wait 1-2 minutes

### Error: "Rate limit exceeded"
**Solution**:
- Free tier: 15 requests/minute
- Wait 60 seconds and try again
- This is normal for heavy usage

### App still shows GROQ error
**Solution**:
- Make sure you rebooted the app after adding the secret
- Clear browser cache (Ctrl + Shift + R)
- Check Streamlit logs for errors

---

## 📝 API Key Security

### ✅ DO:
- Keep your API key secret
- Use environment variables/secrets
- Restrict API key to Generative Language API only
- Regenerate if exposed

### ❌ DON'T:
- Commit API keys to git
- Share API keys publicly
- Use the same key for multiple projects
- Leave keys unrestricted

---

## 🎓 About Gemini 1.5 Flash

The model TORQ now uses:
- **Name**: gemini-1.5-flash
- **Speed**: Very fast responses
- **Quality**: High-quality answers
- **Context**: 1 million token context window
- **Multimodal**: Supports text, images, audio (future feature)

---

## 🔗 Useful Links

- **Get API Key**: https://aistudio.google.com/app/apikey
- **Gemini Docs**: https://ai.google.dev/docs
- **Pricing**: https://ai.google.dev/pricing
- **API Reference**: https://ai.google.dev/api
- **Streamlit Cloud**: https://share.streamlit.io/

---

## ✅ Verification Checklist

- [ ] Got Gemini API key from Google AI Studio
- [ ] Added key to Streamlit Cloud secrets
- [ ] Rebooted Streamlit app
- [ ] Tested Personal Assistant mode
- [ ] Tested Educational mode with PDF
- [ ] No errors in app
- [ ] Responses are working

---

## 🎉 You're All Set!

TORQ is now powered by Google Gemini! Enjoy faster, more reliable responses with a generous free tier.

If you have any issues, check the troubleshooting section above or refer to `GET_GEMINI_API_KEY.md` for detailed instructions.
