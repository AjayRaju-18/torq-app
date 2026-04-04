# TORQ - Vercel CLI Deployment Setup

## ⚠️ Node.js Required

Vercel CLI requires Node.js and npm. You don't have them installed yet.

## 📥 Install Node.js

### Option 1: Download Installer (Recommended)
1. Go to: https://nodejs.org/
2. Download the LTS version (Long Term Support)
3. Run the installer
4. Follow the installation wizard
5. Restart your terminal/PowerShell

### Option 2: Using Chocolatey (Windows Package Manager)
```powershell
# If you have Chocolatey installed
choco install nodejs-lts
```

### Option 3: Using Winget (Windows 11)
```powershell
winget install OpenJS.NodeJS.LTS
```

## ✅ Verify Installation

After installing Node.js, restart your terminal and run:
```bash
node --version
npm --version
```

You should see version numbers like:
```
v20.x.x
10.x.x
```

## 🚀 Deploy with Vercel CLI

Once Node.js is installed:

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```
This will open your browser to authenticate with GitHub/Email.

### Step 3: Deploy TORQ
```bash
# Make sure you're in the TORQ directory
cd D:\TORQ

# Deploy to Vercel
vercel
```

### Step 4: Follow the Prompts
```
? Set up and deploy "D:\TORQ"? [Y/n] Y
? Which scope do you want to deploy to? [Your Account]
? Link to existing project? [y/N] N
? What's your project's name? torq-app
? In which directory is your code located? ./
? Want to override the settings? [y/N] N
```

### Step 5: Add Environment Variable
After first deployment, add your API key:
```bash
vercel env add GROQ_API_KEY
```
When prompted, paste: `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`

Select: `Production`, `Preview`, and `Development`

### Step 6: Redeploy with Environment Variable
```bash
vercel --prod
```

## 🎉 Deployment Complete!

After deployment, you'll see:
```
✅ Production: https://torq-app-[random].vercel.app
```

## 📋 Quick Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View deployment logs
vercel logs

# List all deployments
vercel ls

# Remove a deployment
vercel rm [deployment-url]
```

## 🔄 Alternative: Use Vercel Dashboard

If you prefer not to install Node.js, you can deploy via the web dashboard:

1. Go to: https://vercel.com
2. Sign in with GitHub
3. Click "Add New Project"
4. Import: `AjayRaju-18/torq-app`
5. Add environment variable: `GROQ_API_KEY`
6. Click "Deploy"

This method doesn't require any local installation!

## 🐛 Troubleshooting

### "vercel: command not found"
- Restart your terminal after installing Node.js
- Try: `npm install -g vercel` again

### "Permission denied"
- Run PowerShell as Administrator
- Or use: `npm install -g vercel --force`

### Deployment fails
- Check `vercel logs` for errors
- Verify `api/requirements.txt` is correct
- Ensure you're in the correct directory

## 📞 Need Help?

If you encounter issues:
1. Check Node.js is installed: `node --version`
2. Check Vercel CLI is installed: `vercel --version`
3. Try the web dashboard method instead
