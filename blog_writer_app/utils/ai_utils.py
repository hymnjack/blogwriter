import openai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIHandler:
    """Handles interactions with OpenAI language models."""
    
    def __init__(self, model="o3-mini"):
        """
        Initialize the AI handler.
        
        Args:
            model: The model to use for generation (default: o3-mini)
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
    
    def generate_search_queries(self, topic: str, num_queries: int = 5) -> List[str]:
        """
        Generate search queries based on the topic.
        
        Args:
            topic: The user's input topic
            num_queries: Number of search queries to generate
            
        Returns:
            List of search queries
        """
        system_prompt = """
        You are an expert SEO researcher who understands search patterns and high-volume keywords.
        Deeplpy udnerstand the topic even if vague to make sure we only search for relevant information and get extremely relevant articles for this.
        Your task is to convert a blog topic into search queries that will return popular, information-rich articles.
        Think step-by-step about what most people would search for when looking for information on this topic.
        
        Return ONLY a JSON array of strings with no additional explanations or text.
        """
        
        user_prompt = f"""
        Generate {num_queries} high-volume search queries for a blog about: "{topic}"
        
        Follow these steps:
        1. Identify the main subject and likely audience intent
        2. Focus on broader, popular search terms (avoid niche, long-tail queries)
        3. Include "how to", "best", "guide", or "examples" variations that typically have high search volume
        4. Consider what beginners would search for to learn about this topic
        5. Add queries that would surface comprehensive, informative articles rather than specific answers
        
        Return the queries as a JSON array of strings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract and return the search queries
            content = response.choices[0].message.content
            try:
                queries = eval(content).get("queries", [])
                if not queries:
                    try:
                        # Try to interpret as a direct array
                        queries = eval(content)
                    except:
                        # Fall back to a simple array
                        return [f"{topic} guide", 
                                f"{topic} best practices", 
                                f"how to {topic}", 
                                f"{topic} tips", 
                                f"{topic} examples"]
                
                return queries[:num_queries]
            except:
                # Fallback to a simple search query if JSON parsing fails
                return [f"{topic} guide", 
                        f"{topic} best practices", 
                        f"how to {topic}", 
                        f"{topic} tips", 
                        f"{topic} examples"]
        except Exception as e:
            # Provide fallback search queries
            print(f"Error generating search queries: {e}")
            return [f"{topic} guide", 
                    f"{topic} best practices", 
                    f"how to {topic}", 
                    f"{topic} tips", 
                    f"{topic} examples"]
    
    def analyze_content(self, 
                        topic: str, 
                        scraped_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze scraped content to extract primary keyword, secondary keywords,
        title, and outline.
        
        Args:
            topic: The original topic
            scraped_content: List of dictionaries containing scraped content
            
        Returns:
            Dictionary with primary keyword, secondary keywords, title, and outline
        """
        # Prepare content for analysis
        combined_content = ""
        for i, article in enumerate(scraped_content, 1):
            if 'content' in article and article['content']:
                # Add article number and content with separator
                combined_content += f"--- Article {i} ---\n\n"
                combined_content += article['content']  # Include full content
                combined_content += "\n\n"
                
                # Add headings
                if 'headings' in article and article['headings']:
                    combined_content += "Headings:\n"
                    for heading in article['headings'][:10]:
                        combined_content += f"- {heading.get('text', '')}\n"
                    combined_content += "\n\n"
        
        # # Truncate if too long
        # if len(combined_content) > 15000:
        #     combined_content = combined_content[:15000] + "... [content truncated]"
        
        # Print the combined content length for debugging
        print(f"\n\nCOMBINED CONTENT LENGTH: {len(combined_content)} characters")
        
        system_prompt = """
        You will be given 25 articles, and content for the topic; that rank highly for content about a topic similar to what we are ranking for.
        Your task is to analyse each article one by one; and then find what is the primary keyword for the article. this is the keyword that appears mostly in the title and early phrase of the article.
        further also distinct keywords which appear throughout the article.
        further; also find the outline of the artilce how are headings and subheadings and the pargraphs in it structured.

        based on this analysis from the above article provided to you; 
        you ened to draft the primary keyword, secondary keywords, title, and outline for our article on the given topic.

        make sure your analysis and output is best based on the content provided.


        You are a professional content analyzer and SEO expert. Your task is to analyze the 
        provided content and extract key information for creating a comprehensive blog post.
        
        Provide your analysis in the following JSON format:
        {
            "primary_keyword": "the main keyword that appears most frequently across all articles",
            "secondary_keywords": ["list of 5-10 distinct keywords that appear across articles"],
            "title": "a compelling title that includes the primary keyword",
            "outline": ["list of 5-10 hierarchical section headings for a blog post"]
        }
        
        Secondary keywords should be distinct and complementary to the primary keyword.
        The title should be engaging and SEO-friendly, incorporating the primary keyword.
        The outline should provide a clear structure for a 1000-1500 word blog post.
        """
        
        # Print the system prompt for debugging
        print("\n\nSYSTEM PROMPT:")
        print(system_prompt)
        
        user_prompt = f"""
        Original topic: {topic}
        
        Analyze the following scraped content from multiple articles to create the primary keyword, 
        secondary keywords, a compelling title, and a detailed outline for a blog post:
        
        {combined_content}
        
        Return your analysis in the requested JSON format.
        """
        
        # Print the user prompt for debugging
        print("\n\nUSER PROMPT:")
        print(f"Original topic: {topic}")
        print("[Content truncated for readability]")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract and print the raw response for debugging
            content = response.choices[0].message.content
            print("\n\nRAW MODEL OUTPUT:")
            print(content)
            print("\n\nEND OF RAW MODEL OUTPUT")
            
            # Print the token usage for debugging
            print(f"\n\nTOKEN USAGE:")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Completion tokens: {response.usage.completion_tokens}")
            print(f"Total tokens: {response.usage.total_tokens}")
            
            # Advanced parsing with multiple fallback methods
            import json
            import re
            
            # Method 1: Try direct JSON parsing
            try:
                analysis = json.loads(content)
                print("Successfully parsed with direct json.loads")
                return analysis
            except json.JSONDecodeError as e:
                print(f"Direct JSON parsing failed: {e}")
            
            # Method 2: Try to extract JSON from markdown code blocks
            try:
                if "```json" in content and "```" in content.split("```json")[1]:
                    json_content = content.split("```json")[1].split("```")[0].strip()
                    analysis = json.loads(json_content)
                    print("Successfully parsed JSON from markdown code block")
                    return analysis
            except Exception as e:
                print(f"Markdown code block extraction failed: {e}")
                
            # Method 3: Use regex to find JSON object
            try:
                # Find anything that looks like a JSON object
                json_pattern = r'\{[^\{\}]*((\{[^\{\}]*\})[^\{\}]*)*\}'
                matches = re.findall(json_pattern, content)
                if matches:
                    # Take the longest match as it's likely the complete JSON
                    json_str = max(re.findall(json_pattern, content), key=len)
                    analysis = json.loads(json_str)
                    print("Successfully parsed with regex extraction")
                    return analysis
            except Exception as e:
                print(f"Regex extraction failed: {e}")
            
            # Method 4: Manual extraction of key components
            try:
                # Try to extract components individually
                primary_keyword = re.search(r'"primary_keyword"\s*:\s*"([^"]+)"', content)
                primary_keyword = primary_keyword.group(1) if primary_keyword else topic
                
                # Extract secondary keywords array
                secondary_keywords_match = re.search(r'"secondary_keywords"\s*:\s*\[(.*?)\]', content, re.DOTALL)
                if secondary_keywords_match:
                    keywords_str = secondary_keywords_match.group(1)
                    # Extract quoted strings
                    secondary_keywords = re.findall(r'"([^"]+)"', keywords_str)
                else:
                    secondary_keywords = [topic + " guide", topic + " tips", "how to " + topic]
                
                # Extract title
                title_match = re.search(r'"title"\s*:\s*"([^"]+)"', content)
                title = title_match.group(1) if title_match else f"Complete Guide to {topic.title()}"
                
                # Extract outline array
                outline_match = re.search(r'"outline"\s*:\s*\[(.*?)\]', content, re.DOTALL)
                if outline_match:
                    outline_str = outline_match.group(1)
                    outline = re.findall(r'"([^"]+)"', outline_str)
                else:
                    outline = [
                        f"Introduction to {topic}",
                        f"Why {topic} is Important",
                        f"Key Benefits of {topic}",
                        f"How to Get Started with {topic}",
                        f"Best Practices for {topic}",
                        f"Common Challenges and Solutions",
                        f"Conclusion"
                    ]
                
                analysis = {
                    "primary_keyword": primary_keyword,
                    "secondary_keywords": secondary_keywords,
                    "title": title,
                    "outline": outline
                }
                print("Successfully extracted components with regex")
                return analysis
            except Exception as e:
                print(f"Manual extraction failed: {e}")
            
            # Final fallback
            print("All parsing methods failed, using default values")
            return {
                "primary_keyword": topic,
                "secondary_keywords": [topic + " guide", topic + " tips", "how to " + topic],
                "title": f"Complete Guide to {topic.title()}: Everything You Need to Know",
                "outline": [
                    f"Introduction to {topic}",
                    f"Why {topic} is Important",
                    f"Key Benefits of {topic}",
                    f"How to Get Started with {topic}",
                    f"Best Practices for {topic}",
                    f"Common Challenges and Solutions",
                    f"Conclusion"
                ]
            }
        except Exception as e:
            # Provide fallback analysis
            print(f"Error analyzing content: {e}")
            return {
                "primary_keyword": topic,
                "secondary_keywords": [topic + " guide", topic + " tips", "how to " + topic],
                "title": f"Complete Guide to {topic.title()}: Everything You Need to Know",
                "outline": [
                    f"Introduction to {topic}",
                    f"Why {topic} is Important",
                    f"Key Benefits of {topic}",
                    f"How to Get Started with {topic}",
                    f"Best Practices for {topic}",
                    f"Common Challenges and Solutions",
                    f"Conclusion"
                ]
            }
    
    def generate_article(self, 
                         topic: str,
                         primary_keyword: str, 
                         secondary_keywords: List[str],
                         title: str,
                         outline: List[str],
                         word_count: int = 1500) -> str:
        """
        Generate a complete article based on the provided parameters.
        
        Args:
            topic: The original topic
            primary_keyword: The main keyword for the article
            secondary_keywords: List of secondary keywords
            title: The article title
            outline: The article outline
            word_count: Target word count (default: 1500)
            
        Returns:
            Complete article text
        """
        system_prompt = """
        You are a professional content writer skilled at creating comprehensive, engaging, and 
        SEO-optimized blog posts. Your task is to write a complete article based on the provided 
        parameters.
        
        Follow these guidelines:
        1. Use the primary keyword naturally throughout the article
        2. Incorporate secondary keywords where relevant
        3. Follow the provided outline structure
        4. Write in a professional, informative, and engaging style
        5. Include an introduction that hooks the reader
        6. Provide practical, actionable information
        7. End with a conclusion that summarizes key points
        8. Format with appropriate headings, subheadings, and paragraphs
        9. Aim for the specified word count
        
        Return only the complete article with proper formatting.
        """
        
        user_prompt = f"""
        Write a comprehensive blog post with the following parameters:
        
        Topic: {topic}
        Title: {title}
        Primary Keyword: {primary_keyword}
        Secondary Keywords: {', '.join(secondary_keywords)}
        Target Word Count: {word_count} words
        
        Outline:
        {chr(10).join('- ' + item for item in outline)}
        
        Create a well-structured, informative article that follows this outline and naturally 
        incorporates the keywords. The article should be engaging, valuable to readers, and 
        optimized for SEO.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Return the generated article
            return response.choices[0].message.content
        except Exception as e:
            # Provide a fallback message
            print(f"Error generating article: {e}")
            return f"Error generating article: {str(e)}"
