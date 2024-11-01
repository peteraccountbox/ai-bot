import requests
from bs4 import BeautifulSoup
import re
class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.blacklist = {
            '[document]', 'noscript', 'header', 'html', 'meta', 
            'head', 'input', 'script', 'style', 'footer', 'nav',
            'iframe', 'link', 'aside', 'button', 'svg', 'img'
        }

    def scrape_url(self, url: str) -> str:
        """
        Scrape text content from a URL.
        
        Args:
            url (str): The URL to scrape
            
        Returns:
            str: Cleaned text content
            
        Raises:
            Exception: If scraping fails
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return self._extract_text(response.content)
        except requests.RequestException as e:
            raise Exception(f"Failed to scrape URL {url}: {str(e)}")

    def extract_text_from_html(self, html_content: str) -> str:
        """Extract text from raw HTML string."""
        if not self._is_html(html_content):
            return html_content
        
        soup = BeautifulSoup(html_content, 'html.parser')
        return self._extract_text(str(soup))
    
    def _extract_text(self, content: bytes) -> str:
        """Extract and clean text from HTML content."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove unwanted elements first
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
            element.decompose()
        
        # Get text with proper spacing
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        return cleaned_text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace and normalize spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters and maintain proper spacing
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Remove any non-text artifacts
        text = re.sub(r'([A-Z])\s+(?=[a-z])', r'\1', text)  # Fix split words
        
        return text.strip()

    def _is_html(self, text: str) -> bool:
        return bool(re.search(r'<[^>]+>', text))

    def _is_valid_element(self, element) -> bool:
        """Check if text element should be included."""
        parent = element.parent.name
        is_hidden = (element.parent.get('style') and 
                     'display:none' in element.parent.get('style'))
        
        stripped = element.strip()
        return (
            parent not in self.blacklist and
            not is_hidden and
            stripped and
            not stripped.isspace() and
            len(stripped) > 1
        )