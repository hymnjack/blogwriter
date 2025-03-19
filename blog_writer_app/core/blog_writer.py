from typing import List, Dict, Any, Optional
import os
import sys
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.search_utils import SearchHandler
from utils.ai_utils import AIHandler

class BlogWriter:
    """Manages the complete blog writing process."""
    
    def __init__(self):
        """Initialize the blog writer with required handlers."""
        self.search_handler = SearchHandler()
        self.ai_handler = AIHandler()
        self.state = {
            "topic": None,
            "search_queries": [],
            "search_results": [],
            "scraped_content": [],
            "primary_keyword": None,
            "secondary_keywords": [],
            "title": None,
            "outline": [],
            "article": None
        }
    
    def process_topic(self, topic: str) -> Dict[str, Any]:
        """
        Process the user's topic to generate search queries.
        
        Args:
            topic: User's input topic
            
        Returns:
            Dictionary containing processed topic data and search queries
        """
        # Store the topic in state
        self.state["topic"] = topic
        
        # Generate search queries using AI
        search_queries = self.ai_handler.generate_search_queries(topic)
        self.state["search_queries"] = search_queries
        
        return {
            "topic": topic,
            "search_queries": search_queries
        }
    
    def perform_research(self) -> List[Dict[str, Any]]:
        """
        Perform research by searching the web and scraping content.
        
        Returns:
            List of dictionaries containing search results and scraped content
        """
        if not self.state["search_queries"]:
            raise ValueError("Search queries must be generated first")
        
        all_search_results = []
        all_scraped_content = []
        
        # For each query, search and get the top results
        for query in self.state["search_queries"]:
            # Slight delay to avoid rate limiting
            time.sleep(0.5)
            
            # Get search results
            search_results = self.search_handler.search_web(query)
            if not search_results:  # Skip if no results
                continue
                
            all_search_results.extend(search_results)
            
            # Scrape the top 5 results for each query
            for result in search_results[:5]:
                if not result:  # Skip None results
                    continue
                    
                url = result.get("link", "")
                if not url:  # Skip if no URL
                    continue
                    
                scraped_data = self.search_handler.scrape_content(url)
                if not scraped_data:  # Skip if scraping failed
                    continue
                    
                content = scraped_data.get("content", "")
                if content and len(content) > 100:  # Only add if has meaningful content
                    all_scraped_content.append(scraped_data)
            
            # If we have enough content, stop
            if len(all_scraped_content) >= 25:
                break
        
        # Store in state
        self.state["search_results"] = all_search_results
        self.state["scraped_content"] = all_scraped_content
        
        return all_scraped_content
    
    def analyze_content(self) -> Dict[str, Any]:
        """
        Analyze the scraped content to extract keywords, title, and outline.
        
        Returns:
            Dictionary containing analysis results
        """
        if not self.state["scraped_content"]:
            raise ValueError("Scraped content must be available first")
        
        print("\n\nSTARTING CONTENT ANALYSIS...")
        
        # Analyze the content using AI
        analysis = self.ai_handler.analyze_content(
            self.state["topic"],
            self.state["scraped_content"]
        )
        
        # Print the parsed analysis for debugging
        print("\n\nPARSED ANALYSIS OUTPUT:")
        print(f"Primary Keyword: {analysis.get('primary_keyword')}")
        print(f"Secondary Keywords: {analysis.get('secondary_keywords', [])}")
        print(f"Title: {analysis.get('title')}")
        print(f"Outline: {analysis.get('outline', [])}")
        print("\n\nEND OF PARSED ANALYSIS")
        
        # Store in state
        self.state["primary_keyword"] = analysis.get("primary_keyword")
        self.state["secondary_keywords"] = analysis.get("secondary_keywords", [])
        self.state["title"] = analysis.get("title")
        self.state["outline"] = analysis.get("outline", [])
        
        return analysis
    
    def update_content_plan(self, 
                           primary_keyword: Optional[str] = None,
                           secondary_keywords: Optional[List[str]] = None,
                           title: Optional[str] = None,
                           outline: Optional[List[str]] = None) -> None:
        """
        Update the content plan based on user edits.
        
        Args:
            primary_keyword: Updated primary keyword
            secondary_keywords: Updated secondary keywords
            title: Updated title
            outline: Updated outline
        """
        if primary_keyword:
            self.state["primary_keyword"] = primary_keyword
        
        if secondary_keywords:
            self.state["secondary_keywords"] = secondary_keywords
        
        if title:
            self.state["title"] = title
        
        if outline:
            self.state["outline"] = outline
    
    def generate_article(self, word_count: int = 1500) -> str:
        """
        Generate the complete article.
        
        Args:
            word_count: Target word count
            
        Returns:
            Complete article text
        """
        if not all([
            self.state["primary_keyword"],
            self.state["secondary_keywords"],
            self.state["title"],
            self.state["outline"]
        ]):
            raise ValueError("Content plan must be complete before generating article")
        
        # Generate article using AI
        article = self.ai_handler.generate_article(
            self.state["topic"],
            self.state["primary_keyword"],
            self.state["secondary_keywords"],
            self.state["title"],
            self.state["outline"],
            word_count
        )
        
        # Store in state
        self.state["article"] = article
        
        return article
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the blog writer.
        
        Returns:
            Dictionary containing current state
        """
        return self.state
