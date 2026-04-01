# Easy APK Creation for TORQ Web App

Your TORQ web app URL: **https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/**

## 🚀 Method 1: Online APK Generators (EASIEST - 5 Minutes)

### Option A: WebIntoApp.com (Recommended)
1. Go to https://webintoapp.com/
2. Enter your URL: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
3. Enter app name: `TORQ`
4. Click "Create App"
5. Download the APK file
6. Transfer to your phone and install

### Option B: AppsGeyser.com
1. Go to https://appsgeyser.com/
2. Click "Create App Now"
3. Select "Website"
4. Enter URL: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
5. Enter app name: `TORQ - AI Assistant`
6. Customize icon (optional)
7. Click "Create"
8. Download APK

### Option C: Appy Pie
1. Go to https://www.appypie.com/app-builder/website-to-app
2. Enter app name: `TORQ`
3. Select category: Education/Productivity
4. Enter URL: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
5. Customize design
6. Generate and download APK

### Option D: Gonative.io
1. Go to https://gonative.io/
2. Enter URL: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
3. Configure app settings
4. Download APK

## 🔧 Method 2: PWA Builder (Professional)

1. Go to https://www.pwabuilder.com/
2. Enter URL: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
3. Click "Start"
4. Click "Package For Stores"
5. Select "Android"
6. Click "Generate Package"
7. Download APK

## 🛠️ Method 3: Build Locally (Advanced)

If you want to build the APK yourself with custom features:

### Prerequisites:
```bash
# Install Python packages
pip install buildozer cython

# On Windows, you'll need WSL (Windows Subsystem for Linux)
# Or use a Linux VM/Docker
```

### Build Steps:
```bash
# Navigate to your project directory
cd D:\TORQ

# Copy the webview spec file
copy buildozer_webview.spec buildozer.spec

# Update main.py to use webview
copy torq_webview.py main.py

# Build APK (takes 30-60 minutes first time)
buildozer android debug

# APK will be in: bin/torq-1.0.0-arm64-v8a-debug.apk
```

## 📱 APK Location After Building

### If using online generators:
- **Downloads folder** on your computer
- Usually named: `TORQ.apk` or `torq-app.apk`

### If building locally:
- **Location**: `D:\TORQ\bin\`
- **Filename**: `torq-1.0.0-arm64-v8a-debug.apk`
- **Full path**: `D:\TORQ\bin\torq-1.0.0-arm64-v8a-debug.apk`

## 📲 Installing the APK

### On Your Phone:
1. **Transfer APK** to your phone via:
   - USB cable
   - Email attachment
   - Cloud storage (Google Drive, Dropbox)
   - Direct download from generator website

2. **Enable Unknown Sources**:
   - Go to Settings → Security
   - Enable "Install from Unknown Sources" or "Install Unknown Apps"

3. **Install APK**:
   - Open file manager
   - Navigate to Downloads folder
   - Tap the APK file
   - Click "Install"

4. **Launch TORQ**:
   - Find TORQ icon in app drawer
   - Tap to open

## ✅ Recommended Approach

**For quickest results, use WebIntoApp.com:**

1. Visit: https://webintoapp.com/
2. Paste URL: `https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/`
3. Name: `TORQ`
4. Click "Create App"
5. Download APK (usually takes 2-3 minutes)
6. Install on your phone

**Total time: ~5 minutes** ⚡

## 🎯 What You Get

The APK will:
- ✅ Open your TORQ web app in a native Android container
- ✅ Work exactly like the web version
- ✅ Have its own app icon
- ✅ Appear in your app drawer
- ✅ Support all TORQ features (Personal Assistant, Educational Mode, PDF upload)
- ✅ Remember your session and data
- ✅ Work on any Android device

## 🔍 Troubleshooting

### APK won't install:
- Make sure "Unknown Sources" is enabled
- Check if you have enough storage space
- Try uninstalling any previous version first

### App won't open:
- Check your internet connection
- Make sure the Streamlit app is running
- Try clearing app cache

### Features not working:
- The app is just a wrapper for the web app
- All features depend on the Streamlit app being online
- PDF upload and all functionality work through the web interface

## 💡 Pro Tips

1. **Bookmark the URL** in the app for quick access
2. **Add to home screen** for even faster access (without APK)
3. **Use PWA Builder** for a more professional APK with offline support
4. **Customize the icon** before generating for better branding

Your TORQ app will be ready to use on Android in just a few minutes! 🎉