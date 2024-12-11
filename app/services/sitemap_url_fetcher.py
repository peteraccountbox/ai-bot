import requests
import gzip
import xml.etree.ElementTree as ET

def get_robots_txt_sitemaps(robots_url):
    """
    Get all sitemap URLs from the robots.txt file.
    
    Args:
        robots_url (str): The URL of the robots.txt file.
    
    Returns:
        list: A list of sitemap URLs found in the robots.txt file.
    """
    try:
        response = requests.get(robots_url, timeout=10)
        response.raise_for_status()
        sitemaps = []
        for line in response.text.splitlines():
            if line.strip().lower().startswith("sitemap:"):
                sitemap_url = line.split(":", 1)[1].strip()
                sitemaps.append(sitemap_url)
        return sitemaps
    except requests.exceptions.RequestException as e:
        print(f"Error fetching robots.txt: {e}")
        return []

def fetch_sitemap_urls(sitemap_url):
    """
    Recursively fetch all URLs from the sitemap and nested sitemaps.
    
    Args:
        sitemap_url (str): The URL of the sitemap.
    
    Returns:
        list: A list of all URLs found in the sitemap, including URLs from nested sitemaps.
    """
    urls = []
    try:
        response = requests.get(sitemap_url, timeout=10, stream=True)
        response.raise_for_status()
        
        # Check if the sitemap is a .gz file
        if sitemap_url.endswith('.gz'):
            decompressed_data = gzip.decompress(response.content)
            xml_content = decompressed_data.decode('utf-8')
        else:
            xml_content = response.text
        
        root = ET.fromstring(xml_content)
        
        for elem in root:  # Loop over all child elements
            tag = elem.tag.split('}')[-1]  # Remove namespace if present
            if tag == 'sitemap':
                # Nested sitemap case
                sitemap_loc = elem.find(".//{*}loc")
                if sitemap_loc is not None:
                    nested_sitemap_url = sitemap_loc.text
                    urls.extend(fetch_sitemap_urls(nested_sitemap_url))  # Recursively fetch URLs from nested sitemap
            elif tag == 'url':
                # Regular URL in the sitemap
                url_loc = elem.find(".//{*}loc")
                if url_loc is not None:
                    urls.append(url_loc.text)
    except (requests.exceptions.RequestException, ET.ParseError) as e:
        print(f"Error fetching or parsing sitemap: {sitemap_url}, Error: {e}")
    return urls

def get_all_sitemap_urls(robots_url, excluded_paths, maximum_urls):
    """
    Get all URLs from the main sitemap and any nested sitemaps mentioned in the robots.txt file.
    
    Args:
        robots_url (str): The URL of the robots.txt file.
        excluded_paths (list): List of paths to exclude from the results
        maximum_urls (int): Maximum number of URLs to return
    
    Returns:
        list: A list of dictionaries, each containing a URL from the sitemaps in the format [{"url": "example.com"}]
    """
    if not robots_url.endswith('robots.txt'):
        if not robots_url.endswith('/'):
            robots_url += '/'
        robots_url += 'robots.txt'
    
    all_urls = []
    sitemap_urls = get_robots_txt_sitemaps(robots_url)
    
    for sitemap_url in sitemap_urls:
        print(f"Fetching URLs from sitemap: {sitemap_url}")
        urls_from_sitemap = fetch_sitemap_urls(sitemap_url)
        all_urls.extend(urls_from_sitemap)
        
        # Break if we've exceeded the maximum number of URLs
        if len(all_urls) >= maximum_urls:
            break
    
    # Convert comma-separated string to list and clean up whitespace
    excluded_path_list = [path.strip() for path in excluded_paths.split(',') if path.strip()]
    
    # Filter out excluded paths
    filtered_urls = []
    for url in set(all_urls):
        should_exclude = any(excluded_path in url for excluded_path in excluded_path_list)
        if not should_exclude:
            filtered_urls.append(url)
            if len(filtered_urls) >= maximum_urls:
                break
    
    # Convert the filtered list of URLs to the required format
    formatted_urls = [{"url": url, "wordCount": 0} for url in filtered_urls[:maximum_urls]]
    return formatted_urls
