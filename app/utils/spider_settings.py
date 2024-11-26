# File: spider_settings.py
SCRAPY_SETTINGS = {
    "FEEDS": {"output.json": {"format": "json"}},  # Save output to JSON file
    "CONCURRENT_REQUESTS": 16,  # Number of concurrent requests
    "DOWNLOAD_DELAY": 0.25,  # Delay between requests
    "ROBOTSTXT_OBEY": True,  # Obey robots.txt by default
    "USER_AGENT": "Mozilla/5.0 (compatible; TextSpider/1.0; +http://example.com)",
    "DEPTH_LIMIT": 5,  # Optional: Limit crawling depth to avoid excessive crawling
}

export_settings = SCRAPY_SETTINGS
