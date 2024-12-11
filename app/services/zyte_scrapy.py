from dotenv import load_dotenv
import os
from scrapinghub import ScrapinghubClient
import uuid
import requests
from typing import List, Set, Optional
from urllib.parse import urljoin
from xml.etree import ElementTree
import re
import gzip
import io
from lxml import etree

# Load environment variables
load_dotenv()

# Initialize client and project at module level
client = ScrapinghubClient(os.getenv('ZYTE_API_KEY'))
project = client.get_project(os.getenv('ZYTE_PROJECT_ID'))

def scrape(start_url, depth=2):
    # Generate a unique ID for this scraping job
    job_uuid = str(uuid.uuid4())
    print(f'uuid: {job_uuid}')
    # Start the job
    job = project.jobs.run(
        'website_scraper',
        job_args={
            'start_url': start_url,
            'depth': depth
        },
        webhook_url=f'https://9c520458e2d734e98ae79b088056eb19.m.pipedream.net?uuid={job_uuid}'
    )
    
    print(f"Job started with ID: {job.key}")
    return job.key, job_uuid

def get_job_items(job_key):
    try:
        # Get the job
        job = project.jobs.get(job_key)
        
        # Check if job exists
        if not job.metadata.get('state'):
            return None, f"Job {job_key} not found"
            
    except Exception as e:
        return None, f"Error retrieving job {job_key}: {str(e)}"
    
    # Get all items from the job
    items = []
    for item in job.items.iter():
        items.append(item)
    
    return items, None

def scrape_from_sitemap(website_url: str, maximum_urls: Optional[int] = None) -> dict:
    # Generate a unique ID for this scraping job
    job_uuid = str(uuid.uuid4())
    print(f'uuid: {job_uuid}')
    # Start the job
    job = project.jobs.run(
        'sitemap_spider',
        job_args={
            'website_url': website_url,
            'maximum_urls': maximum_urls
        },
        webhook_url=f'https://9c520458e2d734e98ae79b088056eb19.m.pipedream.net?uuid={job_uuid}'
    )
    
    print(f"Job started with ID: {job.key}")
    return job.key, job_uuid
