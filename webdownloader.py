#!/usr/bin/env python3
# Copyright (c) 2025 nvk
# Licensed under the MIT License

import argparse
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import time
import re
import base64
from pathlib import Path
import html2text

def is_valid_url(url, base_domain):
    """Check if URL belongs to the same domain."""
    parsed_url = urlparse(url)
    parsed_base = urlparse(base_domain)
    return parsed_url.netloc == parsed_base.netloc or not parsed_url.netloc

def is_non_english_page(url, html_content=None):
    """
    Detect if a URL points to a non-English page.
    Uses URL patterns and HTML content analysis if available.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Common language path patterns
    non_english_patterns = [
        r'/[a-z]{2}(?:-[a-z]{2})?/', # language codes like /fr/, /es/, /zh-cn/
        r'/[a-z]{2}(?:-[a-z]{2})?$', # language codes at the end of URL
        r'/(?:translations|intl|i18n)/',
        r'/(?:spanish|espanol|français|deutsch|italiano|português|pусский|日本語|中文|한국어)/'
    ]
    
    # Check URL path for language indicators
    for pattern in non_english_patterns:
        if re.search(pattern, path, re.IGNORECASE):
            return True
    
    # If we have HTML content, check for language attributes
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check html lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            lang = html_tag.get('lang').lower()
            if lang and not lang.startswith(('en', 'en-')):
                return True
        
        # Check hreflang and other language indicators
        lang_meta = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if lang_meta and lang_meta.get('content'):
            content_lang = lang_meta.get('content').lower()
            if content_lang and not content_lang.startswith(('en', 'en-')):
                return True
    
    return False

def convert_to_relative_url(current_path, target_url, base_domain, output_dir):
    """Convert an absolute URL to a relative path for local files."""
    # Remove URL fragments
    target_url, _ = urldefrag(target_url)
    
    # Skip non-HTTP URLs (mailto:, tel:, etc.)
    if not target_url.startswith(('http://', 'https://')):
        return target_url
    
    # If the URL is to an external domain, keep it as is
    parsed_url = urlparse(target_url)
    parsed_base = urlparse(base_domain)
    if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
        return target_url
    
    # Get the path of the target URL
    target_path = parsed_url.path
    if not target_path or target_path.endswith('/'):
        target_path += 'index.html'
    target_path = target_path.lstrip('/')
    if not target_path:
        target_path = 'index.html'
    
    # Get current file directory
    current_dir = os.path.dirname(current_path)
    
    # Calculate relative path
    # First, get paths relative to output directory
    target_abs_path = os.path.join(output_dir, target_path)
    current_abs_path = os.path.join(output_dir, current_path)
    
    # Then calculate relative path from current file to target file
    rel_path = os.path.relpath(target_abs_path, os.path.dirname(current_abs_path))
    
    # Add query params and fragments back if they exist
    if parsed_url.query:
        rel_path += f"?{parsed_url.query}"
    if parsed_url.fragment:
        rel_path += f"#{parsed_url.fragment}"
    
    return rel_path

def html_to_markdown(html_content, base_url, img_dir=None):
    """
    Convert HTML content to Markdown.
    If img_dir is provided, images will be downloaded and embedded.
    """
    # Configure the converter
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.body_width = 0  # No wrapping
    converter.unicode_snob = True
    converter.mark_code = True
    
    # Convert HTML to Markdown
    markdown = converter.handle(html_content)
    
    # If img_dir is provided, download and embed images
    if img_dir:
        # Find all image references in markdown
        img_pattern = r'!\[(.*?)\]\((.*?)\)'
        
        def download_and_update_image(match):
            alt_text = match.group(1)
            img_url = match.group(2)
            
            # Make URL absolute if it's relative
            if not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(base_url, img_url)
            
            try:
                # Download the image
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    # Get image file extension
                    content_type = response.headers.get('Content-Type', '')
                    ext = content_type.split('/')[-1].split(';')[0].strip()
                    if not ext or ext == 'jpeg':
                        ext = 'jpg'
                    
                    # Create a unique filename
                    img_filename = f"img_{hash(img_url) % 10000000}_{os.path.basename(urlparse(img_url).path)}"
                    img_filename = re.sub(r'[^\w.-]', '_', img_filename)
                    if not img_filename.endswith(f'.{ext}'):
                        img_filename += f'.{ext}'
                    
                    # Save the image
                    img_path = os.path.join(img_dir, img_filename)
                    os.makedirs(os.path.dirname(img_path), exist_ok=True)
                    
                    with open(img_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Return updated markdown
                    return f'![{alt_text}](images/{img_filename})'
                else:
                    # Return original if failed
                    return match.group(0)
            except Exception as e:
                # Return original on error
                return match.group(0)
        
        # Replace all image references
        markdown = re.sub(img_pattern, download_and_update_image, markdown)
    
    return markdown

def download_website(url, output_dir=None, delay=0.5, english_only=False, markdown_export=False):
    """
    Download all URLs from a website.
    
    Args:
        url: The website URL to download
        output_dir: Directory to save the URLs (default: domain name)
        delay: Time to wait between requests (in seconds) to avoid overloading the server
        english_only: If True, skip non-English translations of pages
        markdown_export: If True, create a single markdown file instead of HTML files
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Create output directory based on domain if not specified
    if not output_dir:
        domain = urlparse(url).netloc
        output_dir = domain
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Create images directory for markdown export
    img_dir = None
    if markdown_export:
        img_dir = os.path.join(output_dir, 'images')
        os.makedirs(img_dir, exist_ok=True)
        print(f"Created images directory: {img_dir}")
    
    # Keep track of visited URLs to avoid duplicates
    visited_urls = set()
    urls_to_visit = [url]
    base_domain = url
    
    # Dictionary to keep track of URLs and their local file paths
    url_to_local_path = {}
    
    # For markdown export, keep track of content
    markdown_content = []
    
    # Statistics
    stats = {
        'downloaded': 0,
        'skipped_non_english': 0,
        'errors': 0,
        'images_downloaded': 0
    }
    
    print(f"Starting download of {url}")
    print(f"All files will be saved to: {output_dir}")
    if english_only:
        print("English-only mode enabled: Non-English pages will be skipped")
    if markdown_export:
        print("Markdown export mode enabled: Creating a single markdown file")
    
    while urls_to_visit:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_urls:
            continue
        
        visited_urls.add(current_url)
        print(f"Processing: {current_url}")
        
        try:
            response = requests.get(current_url, timeout=10)
            
            # Skip if not HTML content
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type.lower():
                continue
            
            # Check if this is a non-English page and we're in english_only mode
            if english_only and is_non_english_page(current_url, response.text):
                print(f"Skipping non-English page: {current_url}")
                stats['skipped_non_english'] += 1
                continue
                
            if response.status_code == 200:
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title = soup.title.string if soup.title else os.path.basename(current_url)
                
                # Create a file path for this URL
                parsed_url = urlparse(current_url)
                path = parsed_url.path
                if not path or path.endswith('/'):
                    path += 'index.html'
                    
                # Clean up path for filename
                path = path.lstrip('/')
                if not path:
                    path = 'index.html'
                
                # Store URL to local path mapping
                url_to_local_path[current_url] = path
                
                # For markdown export, convert HTML to markdown and add to content
                if markdown_export:
                    # Extract main content area if possible, or use body
                    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body
                    
                    # Add a section header
                    md_section = f"# {title}\n\n"
                    
                    # Convert HTML to markdown
                    md_section += html_to_markdown(str(main_content), current_url, img_dir)
                    
                    # Add URL reference
                    md_section += f"\n\n---\n*Source: [{current_url}]({current_url})*\n\n"
                    
                    # Add to markdown content
                    markdown_content.append({
                        'url': current_url,
                        'title': title,
                        'content': md_section
                    })
                    
                    print(f"Added {title} to markdown content")
                else:
                    # Create directory structure if doesn't exist
                    file_path = os.path.join(output_dir, path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Extract all links in the page
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(current_url, href)
                    
                    # Only follow links that belong to the same domain
                    if is_valid_url(absolute_url, base_domain) and absolute_url not in visited_urls:
                        # If in english_only mode, do a preliminary check on the URL
                        if english_only and is_non_english_page(absolute_url):
                            continue
                        urls_to_visit.append(absolute_url)
                
                # Wait before next request to avoid overwhelming the server
                time.sleep(delay)
            else:
                print(f"Failed to retrieve {current_url}: Status code {response.status_code}")
                stats['errors'] += 1
                continue
                
        except Exception as e:
            print(f"Error processing {current_url}: {e}")
            stats['errors'] += 1
            continue
        
        # Save the HTML content with updated links (if not in markdown mode)
        if not markdown_export:
            try:
                # Create a new soup object for modifying links
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Update all links (a href)
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    if href.startswith('#'):  # Skip anchor links
                        continue
                    absolute_url = urljoin(current_url, href)
                    a_tag['href'] = convert_to_relative_url(path, absolute_url, base_domain, output_dir)
                
                # Update all image sources
                for img_tag in soup.find_all('img', src=True):
                    src = img_tag['src']
                    absolute_url = urljoin(current_url, src)
                    img_tag['src'] = convert_to_relative_url(path, absolute_url, base_domain, output_dir)
                
                # Update CSS links
                for link_tag in soup.find_all('link', href=True):
                    href = link_tag['href']
                    absolute_url = urljoin(current_url, href)
                    link_tag['href'] = convert_to_relative_url(path, absolute_url, base_domain, output_dir)
                
                # Update script sources
                for script_tag in soup.find_all('script', src=True):
                    src = script_tag['src']
                    absolute_url = urljoin(current_url, src)
                    script_tag['src'] = convert_to_relative_url(path, absolute_url, base_domain, output_dir)
                
                # Save the modified HTML content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                print(f"Saved: {file_path} with updated links")
                stats['downloaded'] += 1
                
            except Exception as e:
                print(f"Error updating links in {file_path}: {e}")
                stats['errors'] += 1
    
    # Save all discovered URLs to a text file
    urls_file = os.path.join(output_dir, 'all_urls.txt')
    with open(urls_file, 'w', encoding='utf-8') as f:
        for url in visited_urls:
            f.write(f"{url}\n")
    
    # If in markdown mode, save the markdown content
    if markdown_export:
        # Sort sections - put homepage first, then alphabetically by title
        markdown_content.sort(key=lambda x: (0 if x['url'] == url else 1, x['title']))
        
        # Create the markdown file
        domain = urlparse(url).netloc
        md_file = os.path.join(output_dir, f"{domain}.md")
        
        with open(md_file, 'w', encoding='utf-8') as f:
            # Write title
            f.write(f"# {domain} Website Content\n\n")
            
            # Write table of contents
            f.write("## Table of Contents\n\n")
            for i, section in enumerate(markdown_content):
                f.write(f"{i+1}. [{section['title']}](#{section['title'].lower().replace(' ', '-')})\n")
            
            f.write("\n---\n\n")
            
            # Write content
            for section in markdown_content:
                f.write(section['content'])
                f.write("\n\n---\n\n")
            
            # Write footer
            f.write(f"\n\n*This markdown file was generated from {url} on {time.strftime('%Y-%m-%d')}*\n")
        
        print(f"\nMarkdown export completed! Created {md_file}")
        print(f"Images saved to: {img_dir}")
        stats['downloaded'] = len(markdown_content)
    
    print(f"\nDownload completed! Found {len(visited_urls)} URLs.")
    print(f"Pages downloaded: {stats['downloaded']}")
    if english_only:
        print(f"Non-English pages skipped: {stats['skipped_non_english']}")
    print(f"Errors encountered: {stats['errors']}")
    print(f"All URLs saved to: {urls_file}")
    if not markdown_export:
        print(f"All links have been updated to use relative paths for local browsing.")

def main():
    parser = argparse.ArgumentParser(description='Download all URLs from a website')
    parser.add_argument('-d', '--download', metavar='URL', help='URL to download')
    parser.add_argument('-o', '--output', metavar='DIR', help='Output directory')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('--english-only', action='store_true', help='Skip non-English translations of pages')
    parser.add_argument('--markdown', action='store_true', help='Create a single markdown file with inline images')
    
    args = parser.parse_args()
    
    if args.download:
        # Remove @ symbol if present (as shown in example)
        url = args.download.lstrip('@')
        download_website(url, args.output, args.delay, args.english_only, args.markdown)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 