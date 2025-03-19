import streamlit as st
import os
import sys
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.blog_writer import BlogWriter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Blog Writer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "blog_writer" not in st.session_state:
        st.session_state.blog_writer = BlogWriter()
    
    if "step" not in st.session_state:
        st.session_state.step = 1
    
    if "show_search_results" not in st.session_state:
        st.session_state.show_search_results = False

def render_header():
    """Render the application header."""
    st.title("🤖 AI Blog Writer")
    # st.write("""
    # Generate professional blog content in minutes using AI. 
    # This tool searches the web for relevant information, analyzes it, 
    # and creates a high-quality blog post on your chosen topic.
    # """)

def render_topic_input():
    """Render the topic input section."""
    st.header("Step 1: Enter Your Topic")
    
    # Topic input
    topic = st.text_input(
        "What would you like to write about?",
        help="Enter a topic for your blog. Be specific for better results."
    )
    
    # Analyze button
    if st.button("Research Topic", type="primary") and topic:
        with st.spinner("Generating search queries..."):
            try:
                result = st.session_state.blog_writer.process_topic(topic)
                st.session_state.step = 2
                st.rerun()
            except Exception as e:
                st.error(f"Error analyzing topic: {str(e)}")

def render_research_results():
    """Render the research results section."""
    st.header("Step 2: Research")
    
    # Display topic
    state = st.session_state.blog_writer.get_state()
    st.write(f"**Topic:** {state['topic']}")
    
    # Display search queries
    st.write("### Search Queries")
    for i, query in enumerate(state['search_queries'], 1):
        st.write(f"{i}. {query}")
    
    # Research button
    if not state.get('scraped_content'):
        if st.button("Perform Research", type="primary"):
            with st.spinner("Searching the web and analyzing content... This may take a few minutes."):
                try:
                    scraped_content = st.session_state.blog_writer.perform_research()
                    st.success(f"Research complete! Found {len(scraped_content)} relevant articles.")
                    
                    # Automatically proceed to content analysis
                    with st.spinner("Analyzing content for keywords and structure..."):
                        analysis = st.session_state.blog_writer.analyze_content()
                        st.session_state.step = 3
                        st.rerun()
                except Exception as e:
                    st.error(f"Error performing research: {str(e)}")
    else:
        st.success(f"Research complete! Found {len(state['scraped_content'])} relevant articles.")
        
        # Toggle to show/hide research data
        if st.button("Show/Hide Search Results"):
            st.session_state.show_search_results = not st.session_state.show_search_results
        
        if st.session_state.show_search_results:
            for i, data in enumerate(state["scraped_content"], 1):
                with st.expander(f"Source {i}: {data.get('title', 'Untitled')}"):
                    st.write(f"**URL:** {data.get('url', 'N/A')}")
                    if 'headings' in data and data['headings']:
                        st.write("**Key Headings:**")
                        for heading in data['headings'][:5]:  # Limit to 5 headings
                            st.write(f"- {heading.get('text', '')}")
        
        # Continue button
        if st.button("Continue to Content Planning", type="primary"):
            with st.spinner("Analyzing content for keywords and structure..."):
                try:
                    analysis = st.session_state.blog_writer.analyze_content()
                    st.session_state.step = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Error analyzing content: {str(e)}")
    
    # Option to go back
    if st.button("Go Back"):
        st.session_state.step = 1
        st.rerun()

def render_content_plan():
    """Render the content plan section."""
    st.header("Step 3: Content Plan")
    
    # Get current state
    state = st.session_state.blog_writer.get_state()
    
    # Display topic
    st.write(f"**Topic:** {state['topic']}")
    
    # Primary keyword section
    st.subheader("Primary Keyword")
    primary_keyword = st.text_input(
        "Edit primary keyword if needed:",
        value=state.get('primary_keyword', ''),
        key="primary_keyword_input"
    )
    
    # Secondary keywords section
    st.subheader("Secondary Keywords")
    secondary_keywords_text = st.text_area(
        "Edit secondary keywords (one per line):",
        value="\n".join(state.get('secondary_keywords', [])),
        key="secondary_keywords_input"
    )
    secondary_keywords = [kw.strip() for kw in secondary_keywords_text.split("\n") if kw.strip()]
    
    # Title section
    st.subheader("Blog Title")
    title = st.text_input(
        "Edit blog title:",
        value=state.get('title', ''),
        key="title_input"
    )
    
    # Outline section
    st.subheader("Blog Outline")
    outline_text = st.text_area(
        "Edit blog outline (one item per line):",
        value="\n".join(state.get('outline', [])),
        key="outline_input"
    )
    outline = [item.strip() for item in outline_text.split("\n") if item.strip()]
    
    # Update and continue button
    if st.button("Update and Continue", type="primary"):
        # Update content plan
        st.session_state.blog_writer.update_content_plan(
            primary_keyword=primary_keyword,
            secondary_keywords=secondary_keywords,
            title=title,
            outline=outline
        )
        st.session_state.step = 4
        st.rerun()
    
    # Option to go back
    if st.button("Go Back"):
        st.session_state.step = 2
        st.rerun()

def render_article_generation():
    """Render the article generation section."""
    st.header("Step 4: Generate Article")
    
    # Get current state
    state = st.session_state.blog_writer.get_state()
    
    # Display content plan summary
    st.write(f"**Topic:** {state['topic']}")
    st.write(f"**Primary Keyword:** {state['primary_keyword']}")
    st.write(f"**Title:** {state['title']}")
    
    st.write("**Secondary Keywords:**")
    for kw in state['secondary_keywords']:
        st.write(f"- {kw}")
    
    st.write("**Outline:**")
    for item in state['outline']:
        st.write(f"- {item}")
    
    # Word count slider
    word_count = st.slider(
        "Target Word Count:",
        min_value=500,
        max_value=2500,
        value=1500,
        step=100,
        help="Choose the target word count for your blog post."
    )
    
    # Generate article button
    if not state.get('article'):
        if st.button("Generate Article", type="primary"):
            with st.spinner("Generating your blog post... This may take a few minutes."):
                try:
                    article = st.session_state.blog_writer.generate_article(word_count=word_count)
                    st.success("Article successfully generated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating article: {str(e)}")
    else:
        # Display the generated article
        st.subheader("Generated Article")
        st.markdown(state['article'])
        
        # Download button
        article_text = state['article']
        st.download_button(
            label="Download Article as Text",
            data=article_text,
            file_name=f"{state['topic'].replace(' ', '_')}_blog.md",
            mime="text/markdown"
        )
        
        # Regenerate button
        if st.button("Regenerate Article"):
            with st.spinner("Regenerating your blog post..."):
                try:
                    article = st.session_state.blog_writer.generate_article(word_count=word_count)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error regenerating article: {str(e)}")
    
    # Option to go back
    if st.button("Go Back"):
        st.session_state.step = 3
        st.rerun()

def render_sidebar():
    """Render the sidebar with progress tracking and settings."""
    with st.sidebar:
        st.header("Progress")
        
        # Get current step
        current_step = st.session_state.step
        
        # Progress bar
        progress = (current_step - 1) / 4  # 4 steps total
        st.progress(progress)
        
        # Steps list with highlighting
        steps = [
            "1. Enter Topic",
            "2. Research",
            "3. Content Plan",
            "4. Generate Article"
        ]
        
        for i, step in enumerate(steps, 1):
            if i == current_step:
                st.markdown(f"**→ {step}**")
            else:
                st.write(step)
        
        st.divider()
        
        # About section
        st.header("About")
        st.write("""
        Built with ❤️ by Wald AI
        """)

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Render current step
    if st.session_state.step == 1:
        render_topic_input()
    elif st.session_state.step == 2:
        render_research_results()
    elif st.session_state.step == 3:
        render_content_plan()
    elif st.session_state.step == 4:
        render_article_generation()

if __name__ == "__main__":
    main()
