# 🚀 DEPLOYMENT GUIDE - HUGGING FACE SPACES

**Project:** Email Triage OpenEnv Environment
**Status:** ✅ Ready for Deployment
**Estimated Time:** 10-15 minutes

---

## 📋 PRE-DEPLOYMENT CHECKLIST

✅ Git repository initialized
✅ All files committed to `main` branch
✅ .gitignore configured
✅ Dockerfile ready (port 7860)
✅ All tests passing (23/23)

**You're ready to deploy!** 🎉

---

## 🌐 STEP-BY-STEP DEPLOYMENT

### Step 1: Create Hugging Face Account (if needed)

1. Go to https://huggingface.co/join
2. Create an account (free)
3. Verify your email

---

### Step 2: Create a New Space

1. **Go to Hugging Face Spaces:**
   - Navigate to https://huggingface.co/spaces
   - Click **"Create new Space"** button

2. **Configure your Space:**
   - **Owner:** Select your username
   - **Space name:** `openenv-email-triage` (or your preferred name)
   - **License:** MIT (recommended)
   - **Select SDK:** Choose **Docker** (IMPORTANT!)
   - **Space hardware:** CPU basic (free tier is fine)
   - **Visibility:** Public (required for submission)

3. **Click "Create Space"**

---

### Step 3: Get Your Space Repository URL

After creating the Space, you'll see:
- A repository URL like: `https://huggingface.co/spaces/YOUR_USERNAME/openenv-email-triage`

Copy this URL - you'll need it in the next step.

---

### Step 4: Set Up Git Authentication

#### Option A: Using HTTPS with Token (Recommended)

1. **Create Access Token:**
   - Go to https://huggingface.co/settings/tokens
   - Click "New token"
   - Name: `openenv-deployment`
   - Type: Write access
   - Click "Generate a token"
   - **Copy the token** (you won't see it again!)

2. **Configure Git Credentials:**
   ```bash
   # You'll be prompted for username and password when pushing
   # Username: your HF username
   # Password: paste your HF token
   ```

#### Option B: Using SSH (Advanced)

1. **Add SSH Key to HF:**
   - Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
   - Copy public key: `cat ~/.ssh/id_ed25519.pub`
   - Add to HF: https://huggingface.co/settings/keys

2. **Use SSH URL:**
   ```bash
   git remote add origin git@hf.co:spaces/YOUR_USERNAME/openenv-email-triage
   ```

---

### Step 5: Push Your Code to Hugging Face

**From your project directory** (`/home/raghav/Hacathonnnn/openenv-email-triage`):

```bash
# Add the Hugging Face remote
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/openenv-email-triage

# Push to Hugging Face (use main branch)
git push -u origin main
```

**When prompted:**
- Username: Your Hugging Face username
- Password: Your Hugging Face token (from Step 4)

**Expected output:**
```
Enumerating objects: 25, done.
Counting objects: 100% (25/25), done.
Delta compression using up to 8 threads
Compressing objects: 100% (20/20), done.
Writing objects: 100% (25/25), 123.45 KiB | 12.34 MiB/s, done.
Total 25 (delta 5), reused 0 (delta 0)
To https://huggingface.co/spaces/YOUR_USERNAME/openenv-email-triage
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

### Step 6: Add OpenEnv Tag

1. **Go to your Space:**
   - Navigate to `https://huggingface.co/spaces/YOUR_USERNAME/openenv-email-triage`

2. **Edit Space Settings:**
   - Click the **"⚙️ Settings"** button
   - Find **"Space tags"** section
   - Add tag: `openenv`
   - Add other tags (optional): `email`, `triage`, `nlp`, `reinforcement-learning`

3. **Save Settings**

---

### Step 7: Monitor Build and Deployment

1. **Check Build Status:**
   - On your Space page, you'll see "Building..." status
   - Click "App" tab to see build logs
   - Build typically takes 3-5 minutes

2. **Build Process:**
   ```
   ⏳ Building Docker image...
   📦 Installing dependencies from requirements.txt...
   ✅ Build complete!
   🚀 Starting application on port 7860...
   ✅ Application running!
   ```

3. **Wait for "Running" status:**
   - The Space will show "Running" when ready
   - May take 5-10 minutes for first deployment

---

### Step 8: Verify Deployment

Once your Space shows "Running" status:

#### Test 1: Root Endpoint
```bash
curl https://YOUR_USERNAME-openenv-email-triage.hf.space/
```

**Expected response:**
```json
{
  "name": "email-triage",
  "version": "1.0.0",
  "description": "AI agent environment for email triage...",
  "status": "ok",
  "endpoints": { ... }
}
```

#### Test 2: Health Check
```bash
curl https://YOUR_USERNAME-openenv-email-triage.hf.space/health
```

**Expected response:**
```json
{
  "status": "ok",
  "message": "Email Triage Environment is running"
}
```

#### Test 3: Reset Environment
```bash
curl -X POST https://YOUR_USERNAME-openenv-email-triage.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy"}'
```

**Expected:** Valid observation with email and state info

---

### Step 9: Test All Endpoints

Visit your Space URL in a browser:
- **Space URL:** `https://huggingface.co/spaces/YOUR_USERNAME/openenv-email-triage`
- **API URL:** `https://YOUR_USERNAME-openenv-email-triage.hf.space`

**Quick Test Checklist:**
- ✅ GET `/` - Returns metadata
- ✅ GET `/health` - Returns OK
- ✅ GET `/tasks` - Returns 3 tasks
- ✅ POST `/reset` - Returns observation
- ✅ POST `/step` - Executes action
- ✅ GET `/state` - Returns state
- ✅ POST `/grader` - Returns score (after episode)
- ✅ GET `/baseline` - Returns baseline info

---

### Step 10: Update Space README (Optional but Recommended)

1. **Create README.md in Space:**
   - Your existing README.md will be shown automatically
   - HF will render it on your Space page

2. **Add Space Card Metadata (Optional):**
   - Edit your Space settings
   - Add description, tags, and categories

---

## 🎯 QUICK DEPLOYMENT (TL;DR)

If you already have HF account and token:

```bash
# 1. Add remote (replace YOUR_USERNAME)
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/openenv-email-triage

# 2. Push code
git push -u origin main
# Enter HF username and token when prompted

# 3. Add 'openenv' tag in Space settings

# 4. Wait for build (3-5 minutes)

# 5. Test endpoint
curl https://YOUR_USERNAME-openenv-email-triage.hf.space/health

# Done! ✅
```

---

## 🐛 TROUBLESHOOTING

### Build Fails

**Problem:** Build shows errors in logs

**Solutions:**
1. Check Dockerfile syntax
2. Verify requirements.txt has correct package versions
3. Check Space uses "Docker" SDK (not Gradio or Streamlit)
4. Review build logs for specific errors

### Application Not Starting

**Problem:** Build succeeds but app doesn't start

**Solutions:**
1. Verify port 7860 is exposed in Dockerfile
2. Check uvicorn command in Dockerfile CMD
3. Review application logs in Space

### 502 Bad Gateway

**Problem:** Space shows 502 error

**Solutions:**
1. Wait a few minutes (startup takes time)
2. Check application logs for errors
3. Verify all dependencies installed
4. Restart Space (Settings → Factory reboot)

### Can't Push to HF

**Problem:** Git push fails with authentication error

**Solutions:**
1. Verify you created a Write token (not Read)
2. Use token as password, not your HF password
3. Try HTTPS URL format: `https://huggingface.co/spaces/...`
4. Check you're using correct username

---

## 📝 POST-DEPLOYMENT CHECKLIST

After successful deployment:

- ✅ Space is public and visible
- ✅ Tagged with 'openenv'
- ✅ All endpoints return 200 OK
- ✅ Root endpoint returns metadata
- ✅ Health check works
- ✅ Reset endpoint works
- ✅ Step endpoint works
- ✅ Grader endpoint works

**Copy your Space URL for submission:**
```
https://huggingface.co/spaces/YOUR_USERNAME/openenv-email-triage
```

---

## 🔄 UPDATING YOUR DEPLOYMENT

To update your Space after changes:

```bash
# Make your changes
# ...

# Commit changes
git add .
git commit -m "Update: description of changes"

# Push to HF
git push origin main

# HF will automatically rebuild and redeploy
```

---

## 🎓 ADDITIONAL TIPS

### Make Your Space Stand Out

1. **Add a good description** in Space settings
2. **Include example API calls** in README
3. **Add screenshots** or diagrams
4. **Document expected baseline scores**
5. **Link to OpenEnv documentation**

### Performance Tips

1. Use **CPU basic** (free tier) - sufficient for this environment
2. Consider **persistent storage** if you add data persistence
3. Monitor **logs** for any warnings or errors

### Community Engagement

1. **Share your Space** on HF community forum
2. **Tag it properly** for discoverability
3. **Respond to issues** if users report bugs
4. **Document any limitations**

---

## 📞 GETTING HELP

**Hugging Face Support:**
- Documentation: https://huggingface.co/docs/hub/spaces
- Forum: https://discuss.huggingface.co/
- Discord: https://hf.co/join/discord

**OpenEnv Support:**
- GitHub: https://github.com/openenv
- Documentation: Check competition materials

---

## ✅ DEPLOYMENT COMPLETE!

Once your Space is deployed and all endpoints are working:

1. ✅ Copy your Space URL
2. ✅ Test all endpoints one final time
3. ✅ Take a screenshot of working endpoints (for records)
4. ✅ Submit your Space URL to the competition

**Your Email Triage OpenEnv is now live! 🎉**

---

**Deployment prepared:** 2026-03-27
**Status:** ✅ Ready to Deploy
**Confidence:** 🟢 High (all prerequisites met)
