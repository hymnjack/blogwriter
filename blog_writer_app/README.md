# AI Blog Writer

An AI-powered tool that helps you quickly generate high-quality blog articles on any topic.

## Features

- **Smart Topic Research**: Generates optimized search queries to find relevant information
- **Web Content Analysis**: Searches and analyzes multiple web articles
- **Keyword Optimization**: Identifies primary and secondary keywords for better SEO
- **Content Planning**: Creates a compelling title and detailed outline
- **Article Generation**: Produces a well-structured, SEO-optimized article

## Flow

1. **User Input**: Enter a topic you want to write about
2. **Research**: Automatically generates search queries and searches the web
3. **Content Analysis**: AI analyzes scraped content to extract keywords and structure
4. **Content Planning**: Edit the suggested primary keyword, secondary keywords, title, and outline
5. **Article Generation**: Generate a complete 1000-1500 word article based on your specifications

## Installation

1. Clone the repository:
```
git clone [repository-url]
```

2. Navigate to the project directory:
```
cd blog_writer_app
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Make sure you have set up your .env file with the required API keys:
```
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

## Usage

Run the Streamlit application:
```
streamlit run main.py
```

Then navigate to the provided URL in your browser (typically http://localhost:8501).

## Project Structure

- `/core/` - Core application logic
  - `blog_writer.py` - Main blog writing pipeline
- `/utils/` - Utility modules
  - `ai_utils.py` - AI model interactions
  - `search_utils.py` - Web search and content scraping
- `main.py` - Streamlit application
- `requirements.txt` - Required Python packages

## Requirements

- Python 3.7+
- OpenAI API key
- Serper API key (for web search)

## Notes

- The application uses the o3e-mini model for AI generation by default
- Web scraping may take a few minutes depending on the topic complexity
- Generated articles should be reviewed and edited for best results
