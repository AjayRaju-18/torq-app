# TORQ Android APK Build Guide

This guide will help you build the TORQ AI Assistant as a native Android APK with dynamic UI.

## 🚀 What's Included

### ✅ Native Android App Features:
- **Dynamic UI** - Native Android interface using Kivy
- **All TORQ functionality** - Personal Assistant & Educational Mode
- **Persistent storage** - PDFs and chat history saved locally
- **Offline capability** - Works without internet (except AI responses)
- **File picker** - Native Android file selection for PDFs
- **Chat history** - Sidebar with previous conversations
- **Mode switching** - Toggle between Personal and Educational modes

### ✅ Preserved Functionality:
- **Same AI responses** - Uses identical GROQ API integration
- **PDF processing** - Same text extraction and chunking
- **Vector search** - Identical TF-IDF search functionality
- **Conversation memory** - Chat history and context preservation
- **Token management** - Same optimizations for API limits

## 📱 Prerequisites

### 1. Install Python and Dependencies
```bash
# Install Python 3.8+
python -m pip install --upgrade pip

# Install Kivy and Buildozer
pip install kivy kivymd buildozer cython
```

### 2. Install Android Development Tools

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

#### On Windows:
1. Install **Android Studio** from https://developer.android.com/studio
2. Install **Git** from https://git-scm.com/
3. Install **Java JDK 8** from https://adoptopenjdk.net/

#### On macOS:
```bash
brew install autoconf automake libtool pkg-config
brew install --cask android-studio
```

## 🔧 Build Process

### Method 1: Using Buildozer (Recommended)

1. **Navigate to project directory:**
```bash
cd /path/to/torq-app
```

2. **Initialize buildozer (first time only):**
```bash
buildozer init
```

3. **Build the APK:**
```bash
# Debug APK (for testing)
buildozer android debug

# Release APK (for distribution)
buildozer android release
```

4. **Find your APK:**
```bash
# Debug APK location:
./bin/torq-1.0-arm64-v8a-debug.apk

# Release APK location:
./bin/torq-1.0-arm64-v8a-release.apk
```

### Method 2: Using Docker (Cross-platform)

1. **Create Dockerfile:**
```dockerfile
FROM kivy/buildozer:latest

WORKDIR /app
COPY . /app

RUN buildozer android debug
```

2. **Build with Docker:**
```bash
docker build -t torq-builder .
docker run --rm -v $(pwd):/app torq-builder
```

### Method 3: Using GitHub Actions (Automated)

Create `.github/workflows/build-apk.yml`:
```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install buildozer cython
    
    - name: Build APK
      run: |
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: torq-apk
        path: bin/*.apk
```

## 📱 Installation & Testing

### 1. Install APK on Android Device

#### Via ADB (Developer Mode):
```bash
# Enable Developer Options and USB Debugging on your phone
adb install bin/torq-1.0-arm64-v8a-debug.apk
```

#### Via File Transfer:
1. Copy APK to your phone
2. Enable "Install from Unknown Sources"
3. Tap the APK file to install

### 2. Test Functionality

1. **Launch TORQ** from app drawer
2. **Test Personal Assistant Mode:**
   - Ask general engineering questions
   - Verify conversation memory works
3. **Test Educational Mode:**
   - Upload a PDF file
   - Ask questions about the PDF content
   - Verify persistent storage (close/reopen app)
4. **Test Chat History:**
   - Create multiple conversations
   - Switch between chats
   - Verify persistence across app restarts

## 🎨 UI Features

### Dynamic Android Interface:
- **Native Android look and feel**
- **Responsive layout** for different screen sizes
- **Material Design elements** using KivyMD
- **Smooth animations** and transitions
- **Touch-optimized controls**

### Layout Structure:
```
┌─────────────────────────────────────┐
│ TORQ - AI Assistant                 │
├─────────────┬───────────────────────┤
│ Sidebar     │ Main Content          │
│ ┌─────────┐ │ ┌─────────────────────┤
│ │+ New    │ │ │ Mode Selector       │
│ │ Chat    │ │ │ [Personal/Educational]│
│ └─────────┘ │ ├─────────────────────┤
│             │ │ PDF Upload Section  │
│ Recent      │ │ (Educational Mode)  │
│ Chats:      │ ├─────────────────────┤
│ • Chat 1    │ │                     │
│ • Chat 2    │ │ Chat Messages       │
│ • Chat 3    │ │ (Scrollable)        │
│             │ │                     │
│ [Clear All] │ ├─────────────────────┤
│             │ │ [Input] [Send]      │
└─────────────┴─┴─────────────────────┘
```

## 🔧 Customization Options

### 1. App Icon and Branding
Edit `buildozer.spec`:
```ini
# Custom app icon (512x512 PNG)
icon.filename = %(source.dir)s/icon.png

# Custom splash screen
presplash.filename = %(source.dir)s/splash.png
```

### 2. App Permissions
Add to `buildozer.spec`:
```ini
# Required permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
```

### 3. UI Themes
Modify `torq_mobile.py` colors:
```python
# Primary colors
PRIMARY_COLOR = (0.2, 0.6, 1, 1)      # Blue
SECONDARY_COLOR = (0.1, 0.7, 0.3, 1)  # Green
ERROR_COLOR = (0.8, 0.2, 0.2, 1)      # Red
```

## 🚀 Distribution

### 1. Google Play Store
1. **Sign the APK:**
```bash
buildozer android release
# Sign with your keystore
```

2. **Upload to Play Console:**
   - Create developer account
   - Upload signed APK
   - Fill app details and screenshots

### 2. Direct Distribution
1. **Share APK file** directly
2. **Host on website** for download
3. **Use F-Droid** for open-source distribution

## 🐛 Troubleshooting

### Common Issues:

#### Build Errors:
```bash
# Clean build cache
buildozer android clean

# Update buildozer
pip install --upgrade buildozer

# Check Java version
java -version  # Should be Java 8
```

#### APK Installation Issues:
```bash
# Check device compatibility
adb shell getprop ro.product.cpu.abi

# Install with force
adb install -r bin/torq-*.apk
```

#### Runtime Errors:
```bash
# Check app logs
adb logcat | grep python
```

### Performance Optimization:
1. **Reduce APK size** by excluding unused libraries
2. **Optimize images** and assets
3. **Use ProGuard** for code obfuscation and size reduction

## 📋 File Structure

```
torq-app/
├── main.py                 # App entry point
├── torq_mobile.py         # Main mobile app code
├── buildozer.spec         # Build configuration
├── requirements_mobile.txt # Mobile dependencies
├── app.py                 # Original Streamlit app (imported)
├── BUILD_APK_GUIDE.md     # This guide
└── bin/                   # Generated APK files
    └── torq-*.apk
```

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Buildozer and dependencies installed
- [ ] Android SDK/NDK configured
- [ ] APK builds successfully
- [ ] APK installs on Android device
- [ ] Personal Assistant mode works
- [ ] Educational mode with PDF upload works
- [ ] Chat history persists across app restarts
- [ ] All UI elements responsive and functional

Your TORQ Android APK is now ready for distribution! 🎉