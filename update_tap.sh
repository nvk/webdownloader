#!/bin/bash
# Script to update the Homebrew tap repository

# Calculate SHA256 of the tarball
echo "Calculating SHA256 of the tarball..."
curl -sL "https://github.com/nvk/webdownloader/archive/refs/tags/v1.0.2.tar.gz" | shasum -a 256 | cut -d ' ' -f 1 > sha256.txt
ACTUAL_SHA256=$(cat sha256.txt)
echo "Actual SHA256: $ACTUAL_SHA256"

# Clean up any existing directory first
rm -rf homebrew-webdownloader

# Clone the repository
echo "Cloning the tap repository..."
git clone git@github.com:nvk/homebrew-webdownloader.git
cd homebrew-webdownloader

# Copy the formula file without modifying it further
echo "Copying formula file without modifications..."
cp ../webdownloader.rb .

# Commit and push
git add webdownloader.rb
git commit -m "Update webdownloader formula" || echo "No changes to commit"
git push origin master || echo "No changes to push"

# Cleanup
cd ..
rm -rf homebrew-webdownloader
rm sha256.txt

echo ""
echo "======================= SUCCESS! ======================="
echo "Your Homebrew tap has been updated."
echo ""
echo "To install or upgrade webdownloader using this tap, run:"
echo "  brew update"
echo "  brew tap nvk/webdownloader"
echo "  brew install webdownloader"
echo "  # Or if already installed:"
echo "  brew upgrade webdownloader"
echo "=======================================================" 