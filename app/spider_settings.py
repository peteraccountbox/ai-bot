# File: spider_settings.py
SCRAPY_SETTINGS = {
    "FEEDS": {"output.json": {"format": "json"}},  # Save output to JSON file
    "CONCURRENT_REQUESTS": 20,  # Number of concurrent requests
    "DOWNLOAD_DELAY": 0.25,  # Delay between requests
    "ROBOTSTXT_OBEY": True,  # Obey robots.txt by default
    "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "DEPTH_LIMIT": 10,  # Optional: Limit crawling depth to avoid excessive crawling,
    "COOKIES_ENABLED": True,
}

export_settings = SCRAPY_SETTINGS
