import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import json
import time

def normalize_url(url):
    """
    Normalize a URL by removing the trailing slash and enforcing HTTPS.
    """
    parsed_url = urlparse(url)
    normalized_url = f"https://{parsed_url.netloc}{parsed_url.path}".rstrip('/')
    return normalized_url

def find_links(url, visited, to_visit, base_domain, exclude_patterns, all_links, retries=2, timeout=15):
    """
    Fetch page content and collect internal links, retrying on timeout errors.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML to find links
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            full_url = urljoin(url, link)  # Resolve relative URLs
            normalized_url = normalize_url(full_url)

            # Only add if it's an internal link, not excluded
            if (urlparse(normalized_url).netloc == base_domain
                and normalized_url not in visited
                and normalized_url not in all_links
                and not any(pattern in normalized_url for pattern in exclude_patterns)):
                
                to_visit.append(normalized_url)
                all_links[normalized_url] = 100  # Store link with fixed count value

    except requests.exceptions.Timeout:
        if retries > 0:
            print(f"Timeout occurred for {url}. Retrying ({retries} attempts left)...")
            find_links(url, visited, to_visit, base_domain, exclude_patterns, all_links, retries - 1, timeout)
        else:
            print(f"Skipping {url} after multiple timeouts.")
    except Exception as e:
        print(f"Error crawling {url}: {e}")

def crawl_website(base_url, exclude_patterns):
    """
    Crawl the website starting from the base URL, collecting up to 50 unique internal links.
    """
    base_domain = urlparse(base_url).netloc
    visited = set()  # Track visited URLs
    to_visit = [normalize_url(base_url)]  # Start with the normalized base URL
    all_links = {normalize_url(base_url): 100}  # Initialize with the base URL
    index = 0  # Counter for visited URLs

    print(f"Starting crawl from base URL: {base_url}")
    start_time = time.time()

    # Process each URL until no URLs are left to visit or we reach the limit for visiting
    while to_visit and len(visited) < 50:
        url = to_visit.pop(0)  # Pop the first URL from the queue
        if url not in visited:
            visited.add(url)
            index += 1
            print(f"Visiting {url} - {index}")
            find_links(url, visited, to_visit, base_domain, exclude_patterns, all_links)
            time.sleep(0.5)  # Optional delay for server politeness

    end_time = time.time()
    print(f"\nCrawling completed in {end_time - start_time:.2f} seconds.")

    # Transform the all_links dictionary into the required array format
    formatted_links = [
        {
            "url": url,
            "wordCount": count
        }
        for url, count in all_links.items()
    ]
    
    return formatted_links

# Main execution
if __name__ == "__main__":
    website_url = input("Enter the website URL: ").strip()
    exclude_input = input("Enter paths to exclude (comma-separated, leave empty for no exclusions): ").strip()
    exclude_patterns = [pattern.strip() for pattern in exclude_input.split(",") if pattern.strip()]

    result = crawl_website(website_url, exclude_patterns)
    print("\nAll found links with fixed count values:")
    print(json.dumps(result, indent=4))