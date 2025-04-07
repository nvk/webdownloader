#!/usr/bin/env python3

import argparse
import hashlib
import os
import requests
import re
import subprocess

def calculate_sha256(url):
    """Download file from URL and calculate its SHA256 hash."""
    print(f"Downloading {url} to calculate SHA256...")
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download {url}, status code: {response.status_code}")
    
    # Calculate hash
    sha256_hash = hashlib.sha256()
    for chunk in response.iter_content(chunk_size=4096):
        sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()

def update_formula(version, sha256=None):
    """Update the Homebrew formula with the new version and SHA256."""
    formula_path = "webdownloader.rb"
    if not os.path.exists(formula_path):
        raise FileNotFoundError(f"Formula file {formula_path} not found!")
    
    # Read the current formula
    with open(formula_path, 'r') as f:
        formula_content = f.read()
    
    # Update version
    formula_content = re.sub(
        r'(url\s+"https://github\.com/nvk/webdownloader/archive/refs/tags/v)[\d.]+(.tar.gz")',
        rf'\g<1>{version}\g<2>',
        formula_content
    )
    
    # Update SHA256 if provided
    if sha256:
        formula_content = re.sub(
            r'(sha256\s+")([a-f0-9]+)(")',
            rf'\g<1>{sha256}\g<3>',
            formula_content
        )
    
    # Write the updated formula
    with open(formula_path, 'w') as f:
        f.write(formula_content)
    
    print(f"Updated {formula_path} with version {version}" + (f" and SHA256 {sha256}" if sha256 else ""))

def main():
    parser = argparse.ArgumentParser(description='Prepare WebDownloader release for Homebrew')
    parser.add_argument('version', help='Version number (without v prefix)')
    parser.add_argument('--calculate-sha', action='store_true', help='Calculate SHA256 from GitHub release')
    
    args = parser.parse_args()
    version = args.version
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        raise ValueError("Version must be in format X.Y.Z")
    
    # Update setup.py version
    with open('setup.py', 'r') as f:
        setup_content = f.read()
    
    setup_content = re.sub(
        r'(version=")[\d.]+(")',
        rf'\g<1>{version}\g<2>',
        setup_content
    )
    
    with open('setup.py', 'w') as f:
        f.write(setup_content)
    
    print(f"Updated setup.py with version {version}")
    
    # Calculate SHA256 if requested
    sha256 = None
    if args.calculate_sha:
        url = f"https://github.com/nvk/webdownloader/archive/refs/tags/v{version}.tar.gz"
        try:
            sha256 = calculate_sha256(url)
            print(f"SHA256: {sha256}")
        except Exception as e:
            print(f"Warning: Failed to calculate SHA256: {e}")
            print("You will need to update the SHA256 manually after creating the GitHub release")
    
    # Update formula
    update_formula(version, sha256)
    
    print("\nNext steps:")
    print(f"1. Update setup.py and commit: git commit -am 'Bump version to {version}'")
    print(f"2. Create and push tag: git tag -a v{version} -m 'Release v{version}' && git push origin v{version}")
    print("3. Create a GitHub release with this tag")
    if not sha256:
        print("4. Calculate SHA256 of the release tarball and update the formula")
    print("5. Create a homebrew tap repository (github.com/nvk/homebrew-webdownloader)")
    print("6. Add the updated formula to the tap repository")

if __name__ == "__main__":
    main() 