import scrapy
import re

class BusinessSpider(scrapy.Spider):
    name = "business_spider"

    # Start with the homepage of the website
    start_urls = ["https://example.com"]

    def parse(self, response):
        # Extract business name from the title or meta tags
        business_name = response.xpath('//title/text()').get() or response.xpath('//meta[@property="og:site_name"]/@content').get()

        # Extract contact info (email, phone, address) from the page
        contact_info = {
            "emails": re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text),
            "phone_numbers": re.findall(r"\+?\d[\d\s\-().]{7,}\d", response.text),
        }

        # Extract social media links
        social_links = response.xpath('//a[contains(@href, "facebook.com") or contains(@href, "twitter.com") or contains(@href, "linkedin.com")]/@href').getall()

        # Extract services or products (optional - customize based on website structure)
        services = response.xpath('//section[contains(@class, "services") or contains(@class, "products")]//text()').getall()
        services = [service.strip() for service in services if service.strip()]

        # Follow links to "About Us" or "Contact Us" pages
        for link in response.xpath('//a[contains(@href, "about") or contains(@href, "contact")]/@href').getall():
            yield response.follow(link, self.parse)

        # Yield extracted data
        yield {
            "business_name": business_name,
            "contact_info": contact_info,
            "social_links": social_links,
            "services": services,
            "page_url": response.url,
        }
