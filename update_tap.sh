#!/bin/bash
# Script to update the Homebrew tap repository

# Clean up any existing directory first
rm -rf homebrew-webdownloader

# Clone the repository
echo "Cloning the tap repository..."
git clone git@github.com:nvk/homebrew-webdownloader.git
cd homebrew-webdownloader

# Copy the formula file
echo "Copying formula file..."
cp ../webdownloader.rb .

# Commit and push
git add webdownloader.rb
git commit -m "Update webdownloader formula with page-only mode feature"
git push origin master

# Cleanup
cd ..
rm -rf homebrew-webdownloader

echo ""
echo "======================= SUCCESS! ======================="
echo "Your Homebrew tap has been updated with the latest formula."
echo ""
echo "To install or upgrade webdownloader using this tap, run:"
echo "  brew update"
echo "  brew tap nvk/webdownloader"
echo "  brew install webdownloader"
echo "  # Or if already installed:"
echo "  brew upgrade webdownloader"
echo "=======================================================" 