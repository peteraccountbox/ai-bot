import requests
import app.utils.crawl as crawl
from app.models.schemas import CrawlRequest

def crawl_website(crawl_request: CrawlRequest):
    # Handle null, empty string, or whitespace cases for excluded_paths
    excluded_paths = []
    if crawl_request.excluded_paths and crawl_request.excluded_paths.strip():
        excluded_paths = [path.strip() for path in crawl_request.excluded_paths.split(',')]
    
    # Call crawl function with converted excluded_paths
    content = crawl.crawl_website(crawl_request.website_url, excluded_paths)
    return content