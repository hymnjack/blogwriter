import requests
import json
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SearchHandler:
    """Handles web search and content scraping."""
    
    def __init__(self):
        """Initialize the search handler with Serper API key."""
        self.api_key = os.getenv("SERPER_API_KEY")
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        self.serper_url = "https://google.serper.dev/search"
    
    def search_web(
        self,
        query: str,
        country: str = "us",
        language: str = "en",
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform a web search using the Serper.dev API.
        
        Args:
            query: The search query
            country: Country code for localized results
            language: Language code
            num_results: Number of results to return
            
        Returns:
            List of dictionaries containing search results
        """
        payload = {
            "q": query,
            "gl": country,
            "hl": language,
            "num": num_results
        }
        
        try:
            response = requests.post(
                self.serper_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            search_results = response.json()
            
            # Extract organic results and add better error handling
            organic_results = search_results.get("organic", [])
            results = []
            
            if organic_results is None:
                print(f"Warning: No organic results found in search response: {search_results}")
                return []
                
            for result in organic_results:
                if result is None:
                    continue
                    
                link = result.get("link", "")
                if not link:  # Skip results without a link
                    continue
                    
                results.append({
                    "title": result.get("title", ""),
                    "link": link,
                    "snippet": result.get("snippet", "")
                })
            
            return results
        except requests.RequestException as e:
            print(f"Error performing search: {str(e)}")
            return []
    
    def scrape_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Check if response content exists
            if not response.content:
                return {
                    "url": url,
                    "error": "Empty response content",
                    "title": "",
                    "content": "",
                    "headings": []
                }
                
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract title with better error handling
            title = ""
            if soup and soup.title:
                title = soup.title.string if soup.title.string else ""
            
            # Extract main content
            content = ""
            
            # Try to find article or main content
            main_content = soup.find("article") or soup.find("main") or soup.find("div", class_=["content", "post", "entry", "article"])
            
            if main_content:
                # Extract paragraphs from main content
                for paragraph in main_content.find_all("p"):
                    content += paragraph.get_text() + "\n\n"
            else:
                # Fallback to all paragraphs
                for paragraph in soup.find_all("p"):
                    content += paragraph.get_text() + "\n\n"
            
            # Extract headings
            headings = []
            for heading in soup.find_all(["h1", "h2", "h3"]):
                # Skip empty headings or very short ones
                text = heading.get_text().strip()
                if text and len(text) > 3:
                    headings.append({
                        "level": heading.name,
                        "text": text
                    })
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "headings": headings
            }
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "title": "",
                "content": "",
                "headings": []
            }
            
    def batch_scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape content from multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of dictionaries containing scraped content
        """
        results = []
        for url in urls:
            results.append(self.scrape_content(url))
        return results
