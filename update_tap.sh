#!/bin/bash
# Script to update the Homebrew tap repository
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(
python3 - "$SCRIPT_DIR/setup.py" <<'PY'
import re
import sys
from pathlib import Path

match = re.search(r'version="([^"]+)"', Path(sys.argv[1]).read_text(encoding="utf-8"))
if not match:
    raise SystemExit("Could not find version in setup.py")
print(match.group(1))
PY
)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

# Calculate SHA256 of the tarball
echo "Calculating SHA256 of the tarball..."
ACTUAL_SHA256=$(curl -fsSL "https://github.com/nvk/webdownloader/archive/refs/tags/v${VERSION}.tar.gz" | shasum -a 256 | cut -d ' ' -f 1)
echo "Actual SHA256: $ACTUAL_SHA256"

# Clone the repository
echo "Cloning the tap repository..."
git clone git@github.com:nvk/homebrew-tap.git "$TMP_DIR/homebrew-tap"
cd "$TMP_DIR/homebrew-tap"

# Copy the prepared formula file
echo "Copying prepared formula file..."
mkdir -p Formula
cp "$SCRIPT_DIR/webdownloader.rb" Formula/webdownloader.rb

FORMULA_SHA="$(
python3 - Formula/webdownloader.rb <<'PY'
import re
import sys
from pathlib import Path

content = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(
    r'url "https://github\.com/nvk/webdownloader/archive/refs/tags/v[^"]+"\n\s*sha256 "([a-f0-9]+)"',
    content,
)
if not match:
    raise SystemExit("Could not find top-level formula SHA256")
print(match.group(1))
PY
)"

if [[ "$FORMULA_SHA" != "$ACTUAL_SHA256" ]]; then
    echo "Formula SHA256 does not match the release tarball."
    echo "Formula: $FORMULA_SHA"
    echo "Actual:  $ACTUAL_SHA256"
    echo "Run: python prepare_homebrew_release.py $VERSION --calculate-sha"
    exit 1
fi

# Commit and push
git add Formula/webdownloader.rb
git commit -m "Update webdownloader formula" || echo "No changes to commit"
git push origin HEAD || echo "No changes to push"

echo ""
echo "======================= SUCCESS! ======================="
echo "Your Homebrew tap has been updated."
echo ""
echo "To install or upgrade webdownloader using this tap, run:"
echo "  brew update"
echo "  brew install nvk/tap/webdownloader"
echo "  # Or if already installed:"
echo "  brew upgrade nvk/tap/webdownloader"
echo "======================================================="
