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

def extract_image_ids(html_content, domain_patterns=None):
    """Extract image IDs from HTML content for gallery downloading."""
    if domain_patterns is None:
        # Default patterns for REA Global (realtor.com)
        domain_patterns = ['s1.rea.global']
    
    # Use BeautifulSoup to parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Image IDs we've found with their extensions
    image_ids = set()
    
    # Check for domain patterns in the HTML
    for domain in domain_patterns:
        if domain not in html_content:
            continue
            
        # Look for image URLs in img tags
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if domain in src:
                # Extract image ID from the URL
                match = re.search(r'/([a-zA-Z0-9]+)\.(jpg|jpeg|png|webp)', src)
                if match:
                    image_id = match.group(1)
                    ext = match.group(2)
                    image_ids.add((image_id, ext))
        
        # Look for image URLs in srcset attributes
        for tag in soup.find_all(['img', 'source']):
            srcset = tag.get('srcset', '')
            if domain in srcset:
                for src_str in srcset.split(','):
                    if domain in src_str:
                        # Extract URL from srcset
                        url_part = src_str.strip().split(' ')[0]
                        match = re.search(r'/([a-zA-Z0-9]+)\.(jpg|jpeg|png|webp)', url_part)
                        if match:
                            image_id = match.group(1)
                            ext = match.group(2)
                            image_ids.add((image_id, ext))
        
        # Look for image URLs in JavaScript/JSON
        script_pattern = fr'https?://{re.escape(domain)}/[^"\']+/([a-zA-Z0-9]+)\.(jpg|jpeg|png|webp)'
        for script in soup.find_all('script'):
            script_content = script.string
            if script_content and domain in script_content:
                matches = re.findall(script_pattern, script_content)
                for match in matches:
                    image_id = match[0]
                    ext = match[1]
                    image_ids.add((image_id, ext))
        
        # Also search the raw HTML for any missed IDs
        raw_pattern = fr'https?://{re.escape(domain)}/[^"\']+/([a-zA-Z0-9]+)\.(jpg|jpeg|png|webp)'
        matches = re.findall(raw_pattern, html_content)
        for match in matches:
            image_id = match[0]
            ext = match[1]
            image_ids.add((image_id, ext))
        
        # Search for specific image ID patterns in JSON data
        json_patterns = [
            r'"mediaUrl":"[^"]*/([\w\d]+)\.(jpg|jpeg|png|webp)[^"]*"',
            r'"url":"[^"]*/([\w\d]+)\.(jpg|jpeg|png|webp)[^"]*"',
            r'"src":"[^"]*/([\w\d]+)\.(jpg|jpeg|png|webp)[^"]*"',
            r'"originalUrl":"[^"]*/([\w\d]+)\.(jpg|jpeg|png|webp)[^"]*"',
            r'"hero":"[^"]*/([\w\d]+)\.(jpg|jpeg|png|webp)[^"]*"',
            r'"large":"[^"]*/([\w\d]+)\.(jpg|jpeg|png|webp)[^"]*"'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                image_id = match[0]
                ext = match[1]
                image_ids.add((image_id, ext))
    
    return list(image_ids)

def generate_gallery_urls(image_ids, domain, country_code="cr"):
    """Generate gallery image URLs from image IDs."""
    # Define all possible sizes and formats
    sizes = [
        "raw",          # Original/raw image
        "1200x888",     # Large
        "1080x799",     # Medium-large
        "828x612",      # Medium
        "750x555",      # Medium-small
        "640x473",      # Small
        "384x284",      # Smaller
        "256x189"       # Thumbnail
    ]
    
    # Generate URLs with different sizes/formats
    urls = []
    
    # Default pattern for REA Global (realtor.com)
    if domain == 's1.rea.global':
        base_url = f"https://{domain}/img/"
        for image_id, ext in image_ids:
            for size in sizes:
                if size == "raw":
                    # Raw format
                    url = f"{base_url}{size}/realtor_global/{country_code}/{image_id}.{ext}"
                else:
                    # Sized format with -prop suffix
                    url = f"{base_url}{size}-prop/realtor_global/{country_code}/{image_id}.{ext}"
                urls.append(url)
    
    return urls

def download_gallery_images(urls, output_dir, max_per_image=1):
    """
    Download gallery images from a list of URLs.
    Args:
        urls: List of image URLs to download
        output_dir: Directory to save images
        max_per_image: Maximum number of sizes to download per unique image ID
    """
    if not urls:
        return []
    
    # Create images directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Set user agent to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.realtor.com/'
    }
    
    # Group URLs by image ID to avoid downloading multiple sizes of the same image
    image_id_pattern = r'/([a-zA-Z0-9]+)\.(jpg|jpeg|png|webp)'
    image_id_to_urls = {}
    
    for url in urls:
        match = re.search(image_id_pattern, url)
        if match:
            image_id = match.group(1)
            if image_id not in image_id_to_urls:
                image_id_to_urls[image_id] = []
            image_id_to_urls[image_id].append(url)
    
    # Sort URLs for each image ID by preference (raw first, then by size)
    for image_id, image_urls in image_id_to_urls.items():
        image_urls.sort(key=lambda u: (0 if "/raw/" in u else 1, 
                                      0 if "1200x888" in u else 
                                      1 if "1080x799" in u else 
                                      2 if "828x612" in u else 
                                      3))
    
    # Download images
    downloaded_images = []
    downloaded_ids = set()
    
    for image_id, image_urls in image_id_to_urls.items():
        # Only download up to max_per_image sizes of each image
        for i, url in enumerate(image_urls[:max_per_image]):
            try:
                # Extract size/format from URL for filename
                size_match = re.search(r'/(?:raw|(\d+x\d+)-prop)/', url)
                size = size_match.group(1) if size_match and size_match.group(1) else "raw"
                
                # Create filename
                filename = f"gallery_{image_id}_{size}.{url.split('.')[-1]}"
                filepath = os.path.join(output_dir, filename)
                
                # Download the image
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded gallery image: {filename}")
                    downloaded_images.append(filepath)
                    downloaded_ids.add(image_id)
                else:
                    print(f"Failed to download: {url} (Status: {response.status_code})")
            except Exception as e:
                print(f"Error downloading {url}: {e}")
    
    print(f"Downloaded {len(downloaded_images)} gallery images ({len(downloaded_ids)} unique images)")
    return downloaded_images

def download_website(url, output_dir=None, delay=0.5, english_only=False, markdown_export=False, page_only=False, gallery_mode=False, country_code="cr"):
    """
    Download all URLs from a website.
    
    Args:
        url: The website URL to download
        output_dir: Directory to save the URLs (default: domain name)
        delay: Time to wait between requests (in seconds) to avoid overloading the server
        english_only: If True, skip non-English translations of pages
        markdown_export: If True, create a single markdown file instead of HTML files
        page_only: If True, download only the specified page and its resources without following links
        gallery_mode: If True, attempt to extract and download high-quality gallery images
        country_code: Country code for gallery image URLs (default: cr for Costa Rica)
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
    
    # Create gallery directory if in gallery mode
    gallery_dir = None
    if gallery_mode:
        gallery_dir = os.path.join(output_dir, 'gallery')
        os.makedirs(gallery_dir, exist_ok=True)
        print(f"Created gallery directory: {gallery_dir}")
    
    # Keep track of visited URLs to avoid duplicates
    visited_urls = set()
    urls_to_visit = [url]
    base_domain = url
    
    # Dictionary to keep track of URLs and their local file paths
    url_to_local_path = {}
    
    # For markdown export, keep track of content
    markdown_content = []
    
    # For gallery mode, keep track of image IDs
    gallery_image_ids = []
    
    # Statistics
    stats = {
        'downloaded': 0,
        'skipped_non_english': 0,
        'errors': 0,
        'images_downloaded': 0,
        'gallery_images': 0
    }
    
    print(f"Starting download of {url}")
    print(f"All files will be saved to: {output_dir}")
    if english_only:
        print("English-only mode enabled: Non-English pages will be skipped")
    if markdown_export:
        print("Markdown export mode enabled: Creating a single markdown file")
    if page_only:
        print("Page-only mode enabled: Only downloading the specified page and its resources")
    if gallery_mode:
        print("Gallery mode enabled: Attempting to extract and download gallery images")
    
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
                
                # If in gallery mode, extract image IDs
                if gallery_mode:
                    # Check if this is likely a gallery page (realtor.com or similar)
                    domain = urlparse(current_url).netloc
                    if 'realtor.com' in domain or any(pattern in response.text for pattern in ['s1.rea.global']):
                        print("Detected possible gallery page, extracting image IDs...")
                        ids = extract_image_ids(response.text)
                        if ids:
                            gallery_image_ids.extend(ids)
                            print(f"Found {len(ids)} gallery image IDs")
                
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
                
                # Extract all links in the page, unless we're in page-only mode
                if not page_only:
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        absolute_url = urljoin(current_url, href)
                        
                        # Only follow links that belong to the same domain
                        if is_valid_url(absolute_url, base_domain) and absolute_url not in visited_urls:
                            # If in english_only mode, do a preliminary check on the URL
                            if english_only and is_non_english_page(absolute_url):
                                continue
                            urls_to_visit.append(absolute_url)
                
                # Find and download resources like CSS, JavaScript, and images
                # even in page-only mode, we need to download these resources
                resource_urls = []
                for tag, attr in [('link', 'href'), ('script', 'src'), ('img', 'src')]:
                    for element in soup.find_all(tag, attrs={attr: True}):
                        resource_url = urljoin(current_url, element[attr])
                        if is_valid_url(resource_url, base_domain) and resource_url not in visited_urls:
                            resource_urls.append(resource_url)
                
                # Add resource URLs to visit, even in page-only mode
                for resource_url in resource_urls:
                    if resource_url not in visited_urls:
                        urls_to_visit.append(resource_url)
                
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
                file_path = os.path.join(output_dir, path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                print(f"Saved: {file_path} with updated links")
                stats['downloaded'] += 1
                
            except Exception as e:
                print(f"Error updating links in {file_path}: {e}")
                stats['errors'] += 1
    
    # Process gallery images if in gallery mode
    if gallery_mode and gallery_image_ids:
        print("\nDownloading gallery images...")
        # Generate gallery image URLs (currently only supports REA Global)
        gallery_urls = generate_gallery_urls(gallery_image_ids, 's1.rea.global', country_code)
        if gallery_urls:
            # Download gallery images
            downloaded_gallery_images = download_gallery_images(gallery_urls, gallery_dir)
            stats['gallery_images'] = len(downloaded_gallery_images)
    
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
    if gallery_mode:
        print(f"Gallery images downloaded: {stats['gallery_images']}")
    print(f"Errors encountered: {stats['errors']}")
    print(f"All URLs saved to: {urls_file}")
    if not markdown_export:
        print(f"All links have been updated to use relative paths for local browsing.")
        if page_only:
            print(f"Page-only mode: Only downloaded the specified page and its resources.")

def main():
    parser = argparse.ArgumentParser(description='Download all URLs from a website')
    parser.add_argument('-d', '--download', metavar='URL', help='URL to download')
    parser.add_argument('-o', '--output', metavar='DIR', help='Output directory')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('--english-only', action='store_true', help='Skip non-English translations of pages')
    parser.add_argument('--markdown', action='store_true', help='Create a single markdown file with inline images')
    parser.add_argument('-p', '--page-only', action='store_true', help='Download only the specified page and its resources')
    parser.add_argument('-g', '--gallery-mode', action='store_true', help='Extract and download gallery images (works with realtor.com)')
    parser.add_argument('-c', '--country-code', default='cr', help='Country code for gallery images (default: cr)')
    
    args = parser.parse_args()
    
    if args.download:
        # Remove @ symbol if present (as shown in example)
        url = args.download.lstrip('@')
        download_website(url, args.output, args.delay, args.english_only, args.markdown, args.page_only, args.gallery_mode, args.country_code)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 