import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
import json
import os
import time

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Load settings from JSON file
with open(os.path.join(current_dir, 'spider_settings.json')) as f:
    export_settings = json.load(f)

class TextSpider(scrapy.Spider):
    name = "text_spider"

    def __init__(self, base_url, max_urls=50, exclude_paths=None, *args, **kwargs):
        super(TextSpider, self).__init__(*args, **kwargs)
        self.base_url = base_url
        self.max_urls = max_urls
        self.exclude_paths = exclude_paths or []
        self.visited_urls = set()
        self.crawled_count = 0  # Track the number of crawled URLs

    def start_requests(self):
        yield scrapy.Request(self.base_url, callback=self.parse)

    def parse(self, response):
        # Extract text content, excluding <script>, <style>, and hidden elements
        text = ''.join(response.xpath(
            '//body//*[not(self::script) and not(self::style) and not(contains(@style, "display:none")) and not(contains(@style, "visibility:hidden"))]//text()'
        ).getall())

        # Clean the extracted text
        clean_text = ' '.join([t.strip() for t in text.splitlines() if t.strip()])

        # Yield result for the current page
        yield {
            "url": response.url,
            #"content": clean_text,
            "word_count": len(clean_text.split())
        }

        # Stop if max URLs limit is reached
        self.crawled_count += 1
        if self.crawled_count >= self.max_urls:
            return

        # Extract all links and recursively crawl
        link_extractor = LinkExtractor(allow_domains=response.url.split("//")[-1])
        for link in link_extractor.extract_links(response):
            absolute_url = link.url
            if absolute_url not in self.visited_urls and not any(path in absolute_url for path in self.exclude_paths):
                self.visited_urls.add(absolute_url)
                yield scrapy.Request(absolute_url, callback=self.parse)


# Main function to run the spider
def main():
    # Take input from the user
    base_url = input("Enter the website URL: ").strip()
    max_urls = int(input("Enter the maximum number of URLs to crawl (default 50): ") or 50)
    exclude_paths = input("Enter paths to exclude (comma-separated, e.g., /privacy,/terms): ").split(",")

    # Remove empty paths from exclude_paths
    exclude_paths = [path.strip() for path in exclude_paths if path.strip()]

    # Start timing
    start_time = time.time()

    # Run the Scrapy process with settings from settings.py
    process = CrawlerProcess(export_settings)
    process.crawl(TextSpider, base_url=base_url, max_urls=max_urls, exclude_paths=exclude_paths)
    process.start()

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Crawling completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":   
    main()