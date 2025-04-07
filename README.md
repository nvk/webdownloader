# WebDownloader

A simple command-line tool to download websites for offline use with multiple output options.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/nvk/webdownloader.git
   cd webdownloader
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Make the script executable (Unix/Linux/Mac):
   ```
   chmod +x webdownloader.py
   ```

## Usage

```
python webdownloader.py -d URL [-o OUTPUT_DIR] [--delay DELAY] [--english-only] [--markdown]
```

### Options:

- `-d, --download URL` : The URL of the website to download
- `-o, --output DIR` : Directory to save the downloaded content (default: domain name)
- `--delay DELAY` : Delay between requests in seconds (default: 0.5)
- `--english-only` : Skip non-English translations of pages
- `--markdown` : Create a single markdown file with inline images

### Examples:

Standard download with all files (HTML, CSS, JS, images):
```
python webdownloader.py -d example.com
```

English-only download (skip translations):
```
python webdownloader.py -d example.com --english-only
```

Export as a single markdown file with images:
```
python webdownloader.py -d example.com --markdown
```

Combine options:
```
python webdownloader.py -d example.com --english-only --markdown
```

## Features

- Downloads all HTML pages from a website
- Preserves directory structure
- Only follows links within the same domain
- Converts all internal links to relative paths for local browsing
- Updates links in HTML (a href), images (img src), stylesheets (link href), and scripts (script src)
- Option to skip non-English translations (great for multilingual sites)
- Option to export the entire website as a single markdown file with:
  - Table of contents
  - Section headers for each page
  - Downloaded images in a local images folder
  - Basic structure preserved
  - Source URL references
- Saves all discovered URLs to a text file
- Adds delay between requests to avoid overwhelming the server
- Creates a complete functional offline copy of the website

## Output Modes

### 1. Standard HTML Download
Creates a complete offline copy with HTML, CSS, JavaScript, and images. The directory structure mirrors the website, and all internal links are converted to relative paths for local browsing.

### 2. English-Only HTML Download
Same as standard download, but skips pages in other languages. This is useful for multilingual websites where you only want the English content.

### 3. Markdown Export
Generates a single markdown file with all content, along with an 'images' folder containing the downloaded images. This provides a clean, readable format for content-focused websites, stripping away complex styling and JavaScript.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Note

Please use this tool responsibly. Respect website terms of service and robots.txt rules. This tool is intended for personal archiving and offline reading of publicly available content. 