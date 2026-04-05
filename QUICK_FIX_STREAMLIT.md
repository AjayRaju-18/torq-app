# 🚨 QUICK FIX: Streamlit Cloud API Key Error

## The Problem
Your Streamlit app shows: `Error: Invalid GROQ API key`

## The Solution (60 seconds)

### 1️⃣ Go to Streamlit Cloud
Open: **https://share.streamlit.io/**

### 2️⃣ Click Your App
Find **torq-app** and click on it

### 3️⃣ Open Settings
Click the **⋮** (three dots) → **Settings**

### 4️⃣ Add Secret
In the **Secrets** section, paste this:
```
GROQ_API_KEY = "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"
```

### 5️⃣ Save & Reboot
1. Click **Save**
2. Click **⋮** → **Reboot app**
3. Wait 30 seconds

### 6️⃣ Test
Open: https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/

✅ Should work now!

---

## 📸 Visual Steps

```
Step 1: https://share.streamlit.io/
        ↓
Step 2: Click "torq-app"
        ↓
Step 3: Click ⋮ → Settings
        ↓
Step 4: Scroll to "Secrets" section
        ↓
Step 5: Paste API key (see format above)
        ↓
Step 6: Click "Save"
        ↓
Step 7: Click ⋮ → Reboot app
        ↓
Step 8: Wait 30 seconds
        ↓
Step 9: Refresh your app URL
```

---

## ⚠️ Common Mistakes

❌ **Wrong Format**
```
GROQ_API_KEY = gsk_W9Qi...  (missing quotes)
```

✅ **Correct Format**
```
GROQ_API_KEY = "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"
```

❌ **Extra Spaces**
```
GROQ_API_KEY  =  "gsk_..."  (extra spaces)
```

✅ **No Extra Spaces**
```
GROQ_API_KEY = "gsk_..."
```

---

## 🔄 Still Not Working?

Try this:

1. **Delete and Redeploy**:
   - Streamlit Dashboard → ⋮ → Delete app
   - New app → Select `torq-app` repo
   - Advanced settings → Add secret
   - Deploy

2. **Check Logs**:
   - Streamlit Dashboard → Manage app → Logs
   - Look for any error messages

3. **Hard Refresh Browser**:
   - Press `Ctrl + Shift + R` (Windows)
   - Press `Cmd + Shift + R` (Mac)

---

## 📞 Quick Checklist

- [ ] Logged into https://share.streamlit.io/
- [ ] Found torq-app in dashboard
- [ ] Opened Settings
- [ ] Pasted secret in correct format
- [ ] Clicked Save
- [ ] Rebooted app
- [ ] Waited 30 seconds
- [ ] Tested app URL

If all checked and still not working, the issue might be with the GROQ API key itself (expired or invalid).
