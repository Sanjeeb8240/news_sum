import streamlit as st
import os
from datetime import datetime
import pytz

# Configure page - MUST be first Streamlit command
st.set_page_config(
    page_title="AI News Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to expanded for chatbot
)

# Import custom modules after page config
from utils.auth import authenticate_user, register_user, get_user_data
from utils.helpers import get_greeting
from components.ui_components import load_css, create_header
from components.chatbot_widget import render_chatbot_widget

# Load custom CSS
load_css()

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'

def login_page():
    """Login and registration page"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #2E86AB; font-size: 3rem; margin-bottom: 0.5rem;">
            🤖 AI News Assistant
        </h1>
        <p style="color: #666; font-size: 1.2rem;">
            Your intelligent companion for personalized news and fact-checking
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.markdown("<h3 style='color: #2E86AB; text-align: center;'>Welcome Back!</h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.current_page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        st.markdown("<h3 style='color: #2E86AB; text-align: center;'>Join Us!</h3>", unsafe_allow_html=True)
        
        with st.form("register_form"):
            new_username = st.text_input("Choose Username", placeholder="Enter a unique username")
            new_password = st.text_input("Create Password", type="password", placeholder="Create a secure password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            email = st.text_input("Email (Optional)", placeholder="your.email@example.com")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                reg_submitted = st.form_submit_button("Register", use_container_width=True)
            
            if reg_submitted:
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        if register_user(new_username, new_password, email):
                            st.success("Registration successful! Please login.")
                        else:
                            st.error("Username already exists!")
                    else:
                        st.error("Passwords don't match!")
                else:
                    st.warning("Please fill in all required fields")

def dashboard():
    """Main dashboard page"""
    user_data = get_user_data(st.session_state.username)
    greeting = get_greeting()
    
    # Header with greeting and user info
    create_header(st.session_state.username, greeting)
    
    # Dashboard content
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    
    # Welcome message - reduced spacing
    st.markdown(f"""
    <div class="welcome-card">
        <h2>{greeting}, {st.session_state.username}! 👋</h2>
        <p>Choose from the features below to get started with your personalized news experience.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📰 News Summarizer", key="nav_news", use_container_width=True, help="Get AI-powered news summaries"):
            st.session_state.current_page = 'news_summarizer'
            st.rerun()
    
    with col2:
        if st.button("🔍 Fact Checker", key="nav_fact", use_container_width=True, help="Verify news authenticity"):
            st.session_state.current_page = 'fact_checker'
            st.rerun()
    
    with col3:
        if st.button("⚡ Breaking News", key="nav_breaking", use_container_width=True, help="Latest breaking news"):
            st.session_state.current_page = 'breaking_news'
            st.rerun()
    
    # User stats
    st.markdown("### 📊 Your Activity")
    activity = user_data.get('activity', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📰 News Summaries", activity.get('summaries_generated', 0))
    with col2:
        st.metric("🔍 Fact Checks", activity.get('fact_checks_performed', 0))
    with col3:
        st.metric("🔑 Login Count", activity.get('login_count', 0))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render chatbot widget in sidebar
    render_chatbot_widget()

def news_summarizer_page():
    """News summarizer page"""
    from utils.news_fetcher import fetch_news, get_country_codes, get_language_codes, get_news_categories, clean_article_content
    from utils.ai_services import summarize_text_with_gemini, is_gemini_configured
    from utils.auth import get_user_data, increment_user_activity
    
    user_data = get_user_data(st.session_state.username)
    greeting = get_greeting()
    create_header(st.session_state.username, greeting)
    
    # Navigation
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("🏠 Dashboard"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    with col2:
        if st.button("🔍 Fact Checker"):
            st.session_state.current_page = 'fact_checker'
            st.rerun()
    with col3:
        if st.button("⚡ Breaking News"):
            st.session_state.current_page = 'breaking_news'
            st.rerun()
    
    st.markdown("""
    <div class="welcome-card">
        <h2>📰 Personalized News Summarizer</h2>
        <p>Get AI-powered summaries of the latest news tailored to your preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Store news results in session state to persist across chatbot interactions
    if 'news_results' not in st.session_state:
        st.session_state.news_results = []
    
    # News preferences form
    with st.form("news_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            countries = get_country_codes()
            country = st.selectbox("📍 Country/Region:", list(countries.keys()))
            
            categories = get_news_categories()
            category = st.selectbox("📂 Category:", list(categories.keys()))
        
        with col2:
            languages = get_language_codes()
            language = st.selectbox("🌍 Language:", list(languages.keys()))
            
            num_articles = st.slider("📊 Number of Articles:", 3, 10, 5)
        
        summary_style = st.selectbox("✍️ Summary Style:", 
                                   ["Concise", "Detailed", "Bullet Points", "Casual", "Formal"])
        
        submitted = st.form_submit_button("🚀 Get News Summaries", use_container_width=True)
        
        if submitted:
            if not is_gemini_configured():
                st.error("⚠️ Please configure Gemini API key in utils/ai_services.py")
                return
            
            country_code = countries[country]
            category_code = categories[category]
            language_code = languages[language]
            
            st.info(f"🔍 Fetching {category} news from {country} in {language}...")
            
            with st.spinner("🔄 Fetching and summarizing news..."):
                articles = fetch_news(category_code, country_code, language_code, num_articles)
            
            if articles:
                st.success(f"✅ Found {len(articles)} articles from {country}")
                
                # Store results in session state
                st.session_state.news_results = []
                
                for i, article in enumerate(articles):
                    title = article.get('title', 'No Title')
                    content = clean_article_content(article)
                    source = article.get('source', {}).get('name', 'Unknown')
                    
                    if content and len(content.split()) > 10:
                        summary = summarize_text_with_gemini(content, summary_style.lower())
                        st.session_state.news_results.append({
                            'title': title,
                            'summary': summary,
                            'source': source,
                            'url': article.get('url', ''),
                            'published': article.get('publishedAt', '')
                        })
                    else:
                        st.session_state.news_results.append({
                            'title': title,
                            'summary': article.get('description', 'No description available'),
                            'source': source,
                            'url': article.get('url', ''),
                            'published': article.get('publishedAt', '')
                        })
                
                increment_user_activity(st.session_state.username, 'summaries_generated')
                
                # Removed balloons - st.balloons()
                st.success("🎉 News summaries generated successfully!")
            else:
                st.error("❌ No articles found. Try different preferences or check your internet connection.")
    
    # Display stored results
    if st.session_state.news_results:
        st.markdown("### 📰 Your News Summaries")
        
        for result in st.session_state.news_results:
            with st.expander(f"📰 {result['title']}"):
                st.write("**Summary:**")
                st.write(result['summary'])
                st.caption(f"Source: {result['source']}")
                if result['url']:
                    st.markdown(f"[🔗 Read Full Article]({result['url']})")
                if result['published']:
                    st.caption(f"Published: {result['published']}")
    
    render_chatbot_widget()

def fact_checker_page():
    """Fact checker page"""
    from utils.fact_checker import fact_check_from_input
    from utils.sentiment_analyzer import analyze_sentiment
    from utils.auth import increment_user_activity
    
    greeting = get_greeting()
    create_header(st.session_state.username, greeting)
    
    # Navigation
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("🏠 Dashboard"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    with col2:
        if st.button("📰 News Summarizer"):
            st.session_state.current_page = 'news_summarizer'
            st.rerun()
    with col3:
        if st.button("⚡ Breaking News"):
            st.session_state.current_page = 'breaking_news'
            st.rerun()
    
    st.markdown("""
    <div class="welcome-card">
        <h2>🔍 AI-Powered Fact Checker</h2>
        <p>Verify news authenticity and analyze sentiment using advanced AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input tabs
    tab1, tab2, tab3 = st.tabs(["✍️ Text Input", "📄 PDF Upload", "🔗 URL Input"])
    
    text_input = None
    pdf_file = None
    url_input = None
    
    with tab1:
        text_input = st.text_area("Enter text to fact-check:", height=200, 
                                placeholder="Paste news text, claims, or statements here...")
    
    with tab2:
        pdf_file = st.file_uploader("Upload PDF file:", type=['pdf'])
    
    with tab3:
        url_input = st.text_input("Enter news article URL:", 
                                placeholder="https://example.com/news-article")
    
    col1, col2 = st.columns(2)
    with col1:
        include_sentiment = st.checkbox("📊 Include Sentiment Analysis", value=True)
    
    if st.button("🔍 Analyze Content", use_container_width=True):
        if not any([text_input, pdf_file, url_input]):
            st.error("❌ Please provide content to analyze")
            return
        
        with st.spinner("🔄 Analyzing content..."):
            fact_result = fact_check_from_input(text_input, pdf_file, url_input)
        
        if fact_result['result'] not in ['Invalid URL', 'No Input', 'Processing Error']:
            st.markdown("### 🔍 Fact Check Results")
            
            # Display results with colored indicators
            result = fact_result['result']
            confidence = fact_result['confidence']
            
            if 'true' in result.lower():
                st.success(f"✅ **{result}** (Confidence: {confidence}%)")
            elif 'false' in result.lower():
                st.error(f"❌ **{result}** (Confidence: {confidence}%)")
            else:
                st.warning(f"⚠️ **{result}** (Confidence: {confidence}%)")
            
            st.write("**Explanation:**")
            st.write(fact_result['explanation'])
            
            # Sentiment analysis
            if include_sentiment and text_input:
                st.markdown("### 😊 Sentiment Analysis")
                sentiment_result = analyze_sentiment(text_input)
                
                sentiment = sentiment_result['sentiment']
                if 'positive' in sentiment.lower():
                    st.success(f"😊 **{sentiment}** (Confidence: {sentiment_result['confidence']}%)")
                elif 'negative' in sentiment.lower():
                    st.error(f"😟 **{sentiment}** (Confidence: {sentiment_result['confidence']}%)")
                else:
                    st.info(f"😐 **{sentiment}** (Confidence: {sentiment_result['confidence']}%)")
                
                st.write(sentiment_result['explanation'])
            
            increment_user_activity(st.session_state.username, 'fact_checks_performed')
        else:
            st.error(f"❌ {fact_result['explanation']}")
    
    render_chatbot_widget()

def breaking_news_page():
    """Breaking news page"""
    from utils.news_fetcher import fetch_breaking_news, clean_article_content
    from utils.ai_services import summarize_text_with_gemini, is_gemini_configured
    
    greeting = get_greeting()
    create_header(st.session_state.username, greeting)
    
    # Navigation
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("🏠 Dashboard"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    with col2:
        if st.button("📰 News Summarizer"):
            st.session_state.current_page = 'news_summarizer'
            st.rerun()
    with col3:
        if st.button("🔍 Fact Checker"):
            st.session_state.current_page = 'fact_checker'
            st.rerun()
    
    st.markdown("""
    <div class="welcome-card">
        <h2>⚡ Breaking News Center</h2>
        <p>Stay updated with the most important breaking news from around the world</p>
        <div style="display: flex; align-items: center; margin-top: 1rem;">
            <div style="width: 12px; height: 12px; background: #ef4444; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite;"></div>
            <span style="color: #ef4444; font-weight: 600;">LIVE</span>
        </div>
    </div>
    
    <style>
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        refresh_btn = st.button("🔄 Refresh News", use_container_width=True)
    with col2:
        summarize_all = st.checkbox("🤖 AI Summaries", value=True)
    
    # Fetch breaking news
    if 'breaking_news' not in st.session_state or refresh_btn:
        with st.spinner("⚡ Fetching latest breaking news..."):
            st.session_state.breaking_news = fetch_breaking_news()
    
    breaking_news = st.session_state.get('breaking_news', [])
    
    if breaking_news:
        st.success(f"⚡ Found {len(breaking_news)} breaking news articles")
        
        for i, article in enumerate(breaking_news[:8]):  # Show top 8
            title = article.get('title', 'No Title')
            content = clean_article_content(article)
            source = article.get('source', {}).get('name', 'Unknown')
            url = article.get('url', '')
            
            # Priority indicator
            priority_emoji = "🔴" if i < 2 else ("🟡" if i < 5 else "🔵")
            
            with st.expander(f"{priority_emoji} {title}"):
                if summarize_all and content and len(content.split()) > 20 and is_gemini_configured():
                    try:
                        summary = summarize_text_with_gemini(content, "concise", max_words=100)
                        st.write("**AI Summary:**")
                        st.write(summary)
                    except Exception as e:
                        st.write("**Description:**")
                        st.write(article.get('description', 'No description available'))
                else:
                    st.write("**Description:**")
                    st.write(article.get('description', 'No description available'))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"📰 Source: {source}")
                with col2:
                    if url:
                        st.markdown(f"[🔗 Read Full Article]({url})")
                
                # Show time info if available
                if article.get('publishedAt'):
                    try:
                        pub_time = article['publishedAt']
                        st.caption(f"⏰ {pub_time}")
                    except:
                        pass
    else:
        st.warning("⚠️ No breaking news available at the moment. Please try refreshing.")
    
    render_chatbot_widget()

def main():
    """Main application logic"""
    initialize_session_state()
    
    # Show appropriate page based on authentication and current page
    if not st.session_state.authenticated:
        login_page()
    else:
        # Handle page navigation
        current_page = st.session_state.current_page
        
        if current_page == 'news_summarizer':
            news_summarizer_page()
        elif current_page == 'fact_checker':
            fact_checker_page()
        elif current_page == 'breaking_news':
            breaking_news_page()
        else:
            dashboard()

if __name__ == "__main__":
    main()