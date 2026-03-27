#!/bin/bash

# ========================================================================
# HUGGING FACE SPACES DEPLOYMENT SCRIPT
# Email Triage OpenEnv Environment
# ========================================================================

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🚀 DEPLOYING EMAIL TRIAGE OPENENV TO HUGGING FACE SPACES   ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# ========================================================================
# STEP 1: Check prerequisites
# ========================================================================

echo "📋 Step 1/4: Checking prerequisites..."
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Error: Git repository not initialized"
    echo "   Run: git init"
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: Current branch is '$CURRENT_BRANCH', switching to 'main'"
    git checkout -b main 2>/dev/null || git checkout main
fi

# Check if files are committed
if ! git log -1 &>/dev/null; then
    echo "❌ Error: No commits found"
    echo "   Run: git add . && git commit -m 'Initial commit'"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# ========================================================================
# STEP 2: Get Hugging Face username
# ========================================================================

echo "📝 Step 2/4: Configure Hugging Face deployment..."
echo ""

# Prompt for HF username
read -p "Enter your Hugging Face username: " HF_USERNAME

if [ -z "$HF_USERNAME" ]; then
    echo "❌ Error: Username cannot be empty"
    exit 1
fi

# Prompt for Space name (with default)
read -p "Enter Space name [openenv-email-triage]: " SPACE_NAME
SPACE_NAME=${SPACE_NAME:-openenv-email-triage}

# Construct HF Space URL
HF_SPACE_URL="https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"
HF_GIT_URL="https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"

echo ""
echo "Configuration:"
echo "  Username: $HF_USERNAME"
echo "  Space name: $SPACE_NAME"
echo "  Space URL: $HF_SPACE_URL"
echo ""

# ========================================================================
# STEP 3: Add remote and push
# ========================================================================

echo "🔗 Step 3/4: Setting up git remote..."
echo ""

# Check if remote already exists
if git remote | grep -q "^origin$"; then
    echo "⚠️  Remote 'origin' already exists"
    read -p "Remove existing remote and continue? (y/n): " REMOVE_REMOTE
    if [ "$REMOVE_REMOTE" = "y" ]; then
        git remote remove origin
        echo "✅ Removed existing remote"
    else
        echo "❌ Cancelled"
        exit 1
    fi
fi

# Add HF remote
git remote add origin "$HF_GIT_URL"
echo "✅ Added Hugging Face remote"
echo ""

echo "🚀 Step 4/4: Pushing to Hugging Face..."
echo ""
echo "⚠️  You will be prompted for credentials:"
echo "   Username: $HF_USERNAME"
echo "   Password: Your Hugging Face Access Token"
echo ""
echo "   If you don't have a token, create one at:"
echo "   https://huggingface.co/settings/tokens"
echo "   (Choose 'Write' access)"
echo ""

read -p "Press Enter to continue..."

# Push to HF
if git push -u origin main; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║   ✅ DEPLOYMENT SUCCESSFUL!                                    ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📍 Your Space: $HF_SPACE_URL"
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. ✅ Go to your Space URL above"
    echo "2. ✅ Wait for build to complete (3-5 minutes)"
    echo "3. ✅ Add 'openenv' tag in Space settings"
    echo "4. ✅ Test endpoints:"
    echo "   curl https://${HF_USERNAME}-${SPACE_NAME}.hf.space/health"
    echo ""
    echo "5. ✅ Submit your Space URL to the competition!"
    echo ""
    echo "🎉 Congratulations! Your environment is deployed!"
    echo ""
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Common issues:"
    echo "1. Wrong credentials - Use HF token, not password"
    echo "2. Token needs 'Write' access"
    echo "3. Space doesn't exist - Create it first at huggingface.co/spaces"
    echo ""
    echo "See DEPLOYMENT_GUIDE.md for detailed troubleshooting"
    exit 1
fi

# ========================================================================
# STEP 5: Show testing commands
# ========================================================================

echo "🧪 Test your deployment:"
echo ""
echo "# Wait 3-5 minutes for build, then:"
echo "curl https://${HF_USERNAME}-${SPACE_NAME}.hf.space/health"
echo ""
echo "# Test reset:"
echo "curl -X POST https://${HF_USERNAME}-${SPACE_NAME}.hf.space/reset \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"task_id\": \"easy\"}'"
echo ""
echo "📖 Full documentation: DEPLOYMENT_GUIDE.md"
echo ""
