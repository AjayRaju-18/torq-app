# Fix APK for Streamlit Apps

## 🔴 Problem
WebIntoApp APK shows 500 error, but the web app works perfectly in browser.

## 🎯 Why This Happens
Streamlit apps use:
- **WebSockets** for real-time updates
- **Special HTTP headers** that some APK converters block
- **iframe restrictions** that prevent embedding

## ✅ Solutions (Best to Worst)

### Solution 1: PWA Builder (BEST - Works with Streamlit)

PWA Builder creates a proper Progressive Web App that handles Streamlit correctly.

**Steps:**
1. Go to **https://www.pwabuilder.com/**
2. Enter URL: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
3. Click **"Start"**
4. Wait for analysis (30 seconds)
5. Click **"Package For Stores"**
6. Select **"Android"**
7. Configure options:
   - **Package ID**: `com.torq.app`
   - **App name**: `TORQ`
   - **Display mode**: `Standalone`
   - **Orientation**: `Portrait`
8. Click **"Generate"**
9. Download the **APK** or **App Bundle**
10. Install on your phone

**Why this works:** PWA Builder creates a proper WebView that supports WebSockets and Streamlit's requirements.

### Solution 2: Trusted Web Activity (TWA)

Create a TWA using Bubblewrap (Google's official tool).

**Steps:**
```bash
# Install Node.js first, then:
npm install -g @bubblewrap/cli

# Initialize TWA
bubblewrap init --manifest https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/

# Build APK
bubblewrap build

# APK will be in: ./app-release-signed.apk
```

### Solution 3: Add to Home Screen (No APK Needed)

The simplest solution - use Android's built-in "Add to Home Screen":

**Steps:**
1. Open Chrome on your Android phone
2. Go to: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
3. Tap the **⋮** (three dots) menu
4. Select **"Add to Home screen"**
5. Name it: `TORQ`
6. Tap **"Add"**

**Result:** Creates an app icon that opens in full-screen mode (looks like a native app).

**Pros:**
- ✅ Works perfectly with Streamlit
- ✅ No APK needed
- ✅ Instant setup (30 seconds)
- ✅ Auto-updates when you update the web app
- ✅ Full Streamlit functionality

### Solution 4: Custom WebView APK (Advanced)

Use the `torq_webview.py` I created earlier with proper Streamlit support.

**Update torq_webview.py with Streamlit-specific settings:**

```python
# In the create_webview method, add these settings:
settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW)
settings.setMediaPlaybackRequiresUserGesture(False)
settings.setJavaScriptCanOpenWindowsAutomatically(True)

# Add custom headers for Streamlit
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
self.webview.loadUrl(TORQ_URL, headers)
```

Then build with Buildozer.

### Solution 5: Alternative APK Generators

Try these Streamlit-compatible generators:

#### A. Gonative.io
1. Go to: https://gonative.io/
2. Enter URL: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
3. Enable **"WebSocket Support"**
4. Enable **"JavaScript Bridge"**
5. Generate APK

#### B. AppMySite
1. Go to: https://www.appmysite.com/
2. Select "Website to App"
3. Enter URL
4. Enable advanced features
5. Download APK

## 🎯 Recommended Solution

**Use PWA Builder** - it's specifically designed to handle modern web apps like Streamlit.

**Alternative:** Just use "Add to Home Screen" - it works perfectly and requires no APK!

## 📱 Testing Your APK

After creating the APK, test these features:
- [ ] App opens without 500 error
- [ ] Can switch between Personal/Educational modes
- [ ] Can upload PDF files
- [ ] Chat messages appear correctly
- [ ] Conversation history works
- [ ] App doesn't crash on rotation

## 🔧 If PWA Builder APK Still Fails

The issue might be with Streamlit's iframe restrictions. Add this to your Streamlit app:

**Create `.streamlit/config.toml` in your repository:**

```toml
[server]
enableCORS = false
enableXsrfProtection = false

[browser]
serverAddress = "torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app"
gatherUsageStats = false
```

Then commit and push:
```bash
git add .streamlit/config.toml
git commit -m "Add Streamlit config for APK compatibility"
git push
```

Wait 2-3 minutes for Streamlit Cloud to redeploy, then try creating the APK again.

## 💡 Quick Comparison

| Method | Difficulty | Works with Streamlit | Time |
|--------|-----------|---------------------|------|
| Add to Home Screen | ⭐ Easy | ✅ Perfect | 30 sec |
| PWA Builder | ⭐⭐ Medium | ✅ Good | 5 min |
| Bubblewrap TWA | ⭐⭐⭐ Hard | ✅ Perfect | 15 min |
| WebIntoApp | ⭐ Easy | ❌ Fails | 5 min |
| Custom WebView | ⭐⭐⭐⭐ Expert | ✅ Good | 60 min |

## 🚀 Fastest Working Solution

**Right now, on your phone:**

1. Open Chrome
2. Go to: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
3. Menu → "Add to Home screen"
4. Done! You have a working TORQ app icon

This works exactly like a native app and supports all Streamlit features!

## 📝 Summary

- **WebIntoApp doesn't work** because it doesn't support Streamlit's WebSockets
- **PWA Builder is the best APK solution** for Streamlit apps
- **"Add to Home Screen" is the easiest** and works perfectly
- **Custom WebView requires advanced setup** but gives most control

Try PWA Builder first, or just use "Add to Home Screen" for instant results!