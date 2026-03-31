# Convert TORQ Streamlit App to Android APK

## Method 1: PWA Builder (Recommended - Free & Easy)

### Step 1: Deploy your Streamlit app
Your app is already deployed on Streamlit Community Cloud. Get the URL.

### Step 2: Use PWA Builder
1. Go to https://www.pwabuilder.com/
2. Enter your Streamlit app URL
3. Click "Start" to analyze your app
4. Click "Package For Stores" 
5. Select "Android" 
6. Click "Generate Package"
7. Download the APK file

### Step 3: Install APK
- Transfer the APK to your Android device
- Enable "Install from Unknown Sources" in Settings
- Install the APK

## Method 2: Capacitor (More Control)

### Prerequisites
```bash
npm install -g @capacitor/cli
```

### Steps
1. Create a new Capacitor project:
```bash
npx @capacitor/create-app torq-app com.yourname.torq --web-dir=dist
cd torq-app
```

2. Add Android platform:
```bash
npx cap add android
```

3. Copy your Streamlit app files to the web directory

4. Build the app:
```bash
npx cap copy android
npx cap open android
```

5. Build APK in Android Studio

## Method 3: Online APK Generators (Quick & Free)

### Option A: AppsGeyser
1. Go to https://appsgeyser.com/
2. Select "Website" 
3. Enter your Streamlit app URL
4. Customize app name, icon, etc.
5. Generate and download APK

### Option B: Appy Pie
1. Go to https://www.appypie.com/app-builder/website-to-app
2. Enter your Streamlit app URL
3. Follow the wizard to create APK

### Option C: WebIntoApp
1. Go to https://webintoapp.com/
2. Enter your Streamlit app URL
3. Configure settings and generate APK

## Method 4: Cordova (Traditional)

### Prerequisites
```bash
npm install -g cordova
```

### Steps
1. Create Cordova project:
```bash
cordova create torq-app com.yourname.torq TORQ
cd torq-app
```

2. Add Android platform:
```bash
cordova platform add android
```

3. Replace www/index.html with a redirect to your Streamlit app

4. Build APK:
```bash
cordova build android
```

## Recommended Approach

**For your use case, I recommend Method 1 (PWA Builder)** because:
- ✅ No code changes needed
- ✅ Completely free
- ✅ Works with your existing Streamlit deployment
- ✅ Maintains all functionality
- ✅ Easy to update (just redeploy Streamlit app)
- ✅ Professional-looking APK

## Important Notes

1. **Your Streamlit app must be publicly accessible** (which it already is on Streamlit Community Cloud)

2. **The APK will essentially be a web wrapper** - it loads your web app in a native container

3. **All functionality will work exactly the same** as the web version

4. **Updates are automatic** - when you update your Streamlit app, the APK automatically gets the updates

5. **File uploads work** - PDF upload functionality will work in the APK

## Next Steps

1. Get your Streamlit app URL from Streamlit Community Cloud
2. Go to https://www.pwabuilder.com/
3. Follow the PWA Builder steps above
4. Test the APK on your Android device

The APK will work exactly like your web app but as a native Android application!