# TORQ - Complete Vercel CLI Deployment Guide

## 📋 Overview

This guide will walk you through deploying TORQ to Vercel using the command line interface (CLI). Total time: ~15 minutes.

---

## PART 1: Install Node.js (5 minutes)

### What is Node.js?
Node.js is a JavaScript runtime that allows you to run JavaScript on your computer. Vercel CLI is built with Node.js, so you need it installed first.

### Step 1.1: Download Node.js

1. Open your web browser
2. Go to: **https://nodejs.org/**
3. You'll see two download buttons:
   - **LTS (Long Term Support)** - Recommended for most users
   - **Current** - Latest features
4. Click the **LTS** button (it will say something like "20.12.0 LTS")
5. The download will start automatically (file name: `node-v20.x.x-x64.msi`)

### Step 1.2: Install Node.js

1. Once downloaded, open the `.msi` file
2. Click **Next** on the welcome screen
3. Accept the license agreement, click **Next**
4. Choose installation location (default is fine: `C:\Program Files\nodejs\`)
5. Click **Next**
6. On "Custom Setup" screen, keep all defaults, click **Next**
7. On "Tools for Native Modules" screen, you can uncheck the box (not needed), click **Next**
8. Click **Install**
9. Wait for installation to complete (1-2 minutes)
10. Click **Finish**

### Step 1.3: Verify Node.js Installation

1. **IMPORTANT**: Close any open PowerShell/Command Prompt windows
2. Open a **NEW** PowerShell window:
   - Press `Windows Key + X`
   - Select "Windows PowerShell" or "Terminal"
3. Type this command and press Enter:
   ```bash
   node --version
   ```
4. You should see output like: `v20.12.0`
5. Now check npm (Node Package Manager):
   ```bash
   npm --version
   ```
6. You should see output like: `10.5.0`

✅ If you see version numbers, Node.js is installed correctly!

❌ If you see "command not found", restart your computer and try again.

---

## PART 2: Install Vercel CLI (2 minutes)

### What is Vercel CLI?
Vercel CLI is a command-line tool that lets you deploy your app to Vercel's servers directly from your terminal.

### Step 2.1: Install Vercel CLI Globally

1. In your PowerShell window, type:
   ```bash
   npm install -g vercel
   ```
2. Press Enter
3. You'll see installation progress (downloading packages, etc.)
4. Wait for it to complete (1-2 minutes)
5. You might see some warnings - that's normal, ignore them

### Step 2.2: Verify Vercel CLI Installation

1. Type this command:
   ```bash
   vercel --version
   ```
2. You should see output like: `Vercel CLI 33.5.0`

✅ If you see a version number, Vercel CLI is installed!

---

## PART 3: Login to Vercel (2 minutes)

### Step 3.1: Create Vercel Account (if you don't have one)

1. Go to: **https://vercel.com/signup**
2. Click **"Continue with GitHub"** (recommended)
3. Authorize Vercel to access your GitHub account
4. Your account is created!

### Step 3.2: Login via CLI

1. In PowerShell, type:
   ```bash
   vercel login
   ```
2. Press Enter
3. You'll see a prompt asking how you want to login:
   ```
   ? Log in to Vercel
   > Continue with GitHub
     Continue with GitLab
     Continue with Bitbucket
     Continue with Email
   ```
4. Use arrow keys to select **"Continue with GitHub"**
5. Press Enter
6. Your browser will open automatically
7. Click **"Authorize Vercel"** in the browser
8. You'll see: "You are now logged in!"
9. Go back to PowerShell - you should see:
   ```
   > Success! GitHub authentication complete
   ```

✅ You're now logged in to Vercel!

---

## PART 4: Deploy TORQ to Vercel (5 minutes)

### Step 4.1: Navigate to TORQ Directory

1. In PowerShell, type:
   ```bash
   cd D:\TORQ
   ```
2. Press Enter
3. Verify you're in the right place:
   ```bash
   ls
   ```
4. You should see files like: `app.py`, `vercel.json`, `api/`, etc.

### Step 4.2: First Deployment

1. Type this command:
   ```bash
   vercel
   ```
2. Press Enter
3. You'll see a series of questions. Here's what to answer:

**Question 1:**
```
? Set up and deploy "D:\TORQ"? [Y/n]
```
Type: `Y` and press Enter

**Question 2:**
```
? Which scope do you want to deploy to?
```
You'll see your username/account. Press Enter to select it.

**Question 3:**
```
? Link to existing project? [y/N]
```
Type: `N` and press Enter (we're creating a new project)

**Question 4:**
```
? What's your project's name? (torq)
```
Type: `torq-app` and press Enter

**Question 5:**
```
? In which directory is your code located? ./
```
Just press Enter (default is correct)

**Question 6:**
```
? Want to override the settings? [y/N]
```
Type: `N` and press Enter

4. Vercel will now start deploying:
   ```
   🔗  Linked to your-username/torq-app
   🔍  Inspect: https://vercel.com/...
   ✅  Preview: https://torq-app-xxxxx.vercel.app
   ```

5. Wait for deployment to complete (1-2 minutes)

### Step 4.3: Add GROQ API Key

Your app is deployed, but it needs the API key to work!

1. Type this command:
   ```bash
   vercel env add GROQ_API_KEY
   ```
2. Press Enter
3. You'll see:
   ```
   ? What's the value of GROQ_API_KEY?
   ```
4. Paste this API key:
   ```
   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
   ```
5. Press Enter
6. You'll see:
   ```
   ? Add GROQ_API_KEY to which Environments?
   ```
7. Use arrow keys and spacebar to select ALL THREE:
   ```
   ◉ Production
   ◉ Preview
   ◉ Development
   ```
8. Press Enter
9. You'll see: `✅ Added Environment Variable GROQ_API_KEY`

### Step 4.4: Deploy to Production with API Key

Now redeploy so the API key is included:

1. Type this command:
   ```bash
   vercel --prod
   ```
2. Press Enter
3. Wait for deployment (1-2 minutes)
4. You'll see:
   ```
   ✅  Production: https://torq-app-xxxxx.vercel.app
   ```

### Step 4.5: Test Your Deployment

1. Copy the production URL from the terminal
2. Open it in your browser
3. You should see TORQ's ChatGPT-style interface!
4. Test it:
   - Try Personal Assistant mode: "What is mechanical engineering?"
   - Upload a PDF and try Educational mode

---

## 🎉 SUCCESS! Your TORQ App is Live!

Your app is now deployed at: `https://torq-app-xxxxx.vercel.app`

---

## 📋 Useful Vercel CLI Commands

### View All Deployments
```bash
vercel ls
```
Shows all your deployments with URLs and status.

### View Deployment Logs
```bash
vercel logs
```
Shows real-time logs from your app (useful for debugging).

### Deploy to Preview (Testing)
```bash
vercel
```
Creates a preview deployment (not production).

### Deploy to Production
```bash
vercel --prod
```
Deploys to your main production URL.

### View Environment Variables
```bash
vercel env ls
```
Lists all environment variables.

### Remove a Deployment
```bash
vercel rm [deployment-url]
```
Deletes a specific deployment.

### Open Project in Browser
```bash
vercel open
```
Opens your Vercel dashboard for this project.

---

## 🔄 How to Update Your App

When you make changes to your code:

1. Commit changes to git:
   ```bash
   git add .
   git commit -m "Updated feature"
   git push origin main
   ```

2. Deploy the update:
   ```bash
   vercel --prod
   ```

That's it! Vercel will automatically build and deploy your changes.

---

## 🐛 Troubleshooting

### Problem: "node: command not found"
**Solution**: 
- Restart your computer after installing Node.js
- Make sure you closed and reopened PowerShell

### Problem: "vercel: command not found"
**Solution**:
- Run: `npm install -g vercel` again
- Restart PowerShell
- Try: `npx vercel` instead

### Problem: "Permission denied" during npm install
**Solution**:
- Run PowerShell as Administrator:
  - Right-click PowerShell
  - Select "Run as Administrator"
- Try installation again

### Problem: Deployment fails with "Build Error"
**Solution**:
- Check logs: `vercel logs`
- Verify `api/requirements.txt` exists
- Make sure you're in the TORQ directory: `cd D:\TORQ`

### Problem: App shows "500 Internal Server Error"
**Solution**:
- Check if GROQ_API_KEY is set: `vercel env ls`
- If missing, add it: `vercel env add GROQ_API_KEY`
- Redeploy: `vercel --prod`

### Problem: PDF upload doesn't work
**Solution**:
- This is normal - Vercel serverless functions have size limits
- For large PDFs, consider using a database or cloud storage

---

## 📊 Vercel Free Tier Limits

Your free account includes:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth per month
- ✅ Automatic HTTPS
- ✅ Global CDN (fast worldwide)
- ✅ Automatic Git integration
- ⚠️ 10-second function timeout
- ⚠️ 4.5MB request body limit

For most use cases, this is more than enough!

---

## 🔗 Important URLs

- **Your GitHub Repo**: https://github.com/AjayRaju-18/torq-app
- **Streamlit App**: https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Vercel Docs**: https://vercel.com/docs

---

## 💡 Pro Tips

1. **Custom Domain**: You can add a custom domain (like torq.yourdomain.com) for free in Vercel dashboard

2. **Automatic Deployments**: Connect your GitHub repo in Vercel dashboard for automatic deployments on every push

3. **Preview Deployments**: Every git branch gets its own preview URL automatically

4. **Analytics**: Enable Vercel Analytics in dashboard to see visitor stats

5. **Environment Variables**: You can edit environment variables in the Vercel dashboard without using CLI

---

## ✅ Checklist

- [ ] Node.js installed and verified
- [ ] Vercel CLI installed and verified
- [ ] Logged in to Vercel
- [ ] Deployed TORQ app
- [ ] Added GROQ_API_KEY environment variable
- [ ] Deployed to production
- [ ] Tested app in browser
- [ ] Tested Personal Assistant mode
- [ ] Tested Educational mode with PDF upload

---

## 🎓 What You've Learned

- How to install Node.js and npm
- How to use Vercel CLI
- How to deploy a Python Flask app to Vercel
- How to manage environment variables
- How to update and redeploy your app

Congratulations! You've successfully deployed TORQ to Vercel! 🚀
