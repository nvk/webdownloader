#!/bin/bash
# Script to copy the formula into the main Homebrew tap repository
set -euo pipefail

# Configuration
GITHUB_USERNAME="nvk"
FORMULA_NAME="webdownloader"
TAP_REPO_NAME="homebrew-tap"
FORMULA_FILE="$FORMULA_NAME.rb"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Create a temporary directory
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
cd "$TMP_DIR"
echo "Working in temporary directory: $TMP_DIR"

# Step 2: Clone the tap repository (or create it if it doesn't exist)
echo "Checking if tap repository exists..."
if git clone "git@github.com:$GITHUB_USERNAME/$TAP_REPO_NAME.git" 2>/dev/null; then
    echo "Tap repository cloned successfully"
    cd "$TAP_REPO_NAME"
else
    echo "Tap repository does not exist. Creating..."
    mkdir "$TAP_REPO_NAME"
    cd "$TAP_REPO_NAME"
    git init
    echo "# nvk/homebrew-tap" > README.md
    git add README.md
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin "git@github.com:$GITHUB_USERNAME/$TAP_REPO_NAME.git"
    echo "You will need to create the GitHub repository before pushing!"
    echo "Create it at: https://github.com/new"
    read -p "Press enter when you've created the repository..."
    git push -u origin main
fi

# Step 3: Copy the formula file from the webdownloader repo
echo "Copying formula file..."
mkdir -p Formula
cp "$SCRIPT_DIR/$FORMULA_FILE" "Formula/$FORMULA_FILE"

# Step 4: Commit and push the formula
git add "Formula/$FORMULA_FILE"
git commit -m "Add $FORMULA_NAME formula" || echo "No changes to commit"
git push origin main

# Step 5: Instructions for installing
echo ""
echo "======================= SUCCESS! ======================="
echo "Your Homebrew tap has been created and the formula has been added."
echo ""
echo "To install $FORMULA_NAME using this tap, run:"
echo "  brew tap $GITHUB_USERNAME/tap"
echo "  brew install $GITHUB_USERNAME/tap/$FORMULA_NAME"
echo ""
echo "To submit to Homebrew Core (optional):"
echo "1. Fork https://github.com/Homebrew/homebrew-core"
echo "2. Add your formula to the Formula directory"
echo "3. Submit a pull request"
echo "======================================================="

# Clean up
cd "$SCRIPT_DIR"
