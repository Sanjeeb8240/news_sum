# Flask Backend for Gamified News Analyzer
from flask import Flask, render_template, request, jsonify
import requests
from textblob import TextBlob
import google.generativeai as genai
import re
import os

app = Flask(__name__)

# Configuration
NEWSDATA_API_KEY = os.getenv('NEWSDATA_API_KEY', 'pub_dfd39213708245e6b983b3db29cfecff')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCTBB1nDinuDwK5TCvC8fJcdKfzAhmBPKY')
NEWSDATA_API_URL = 'https://newsdata.io/api/1/latest'

# Initialize Gemini
if GEMINI_API_KEY != 'your_gemini_key_here':
    genai.configure(api_key=GEMINI_API_KEY)

def fetch_news(country=None, category=None, size=6):
    """Fetch news from NewsData.io"""
    params = {
        'apikey': NEWSDATA_API_KEY,
        'size': min(size, 10),
        'language': 'en'
    }
    
    if country:
        params['country'] = country
    if category:
        params['category'] = category
        
    try:
        response = requests.get(NEWSDATA_API_URL, params=params, timeout=10)
        data = response.json()
        return data.get('results', [])
    except:
        return []

def create_summary(title, description, content):
    """Create 2-line summary"""
    all_text = f"{title} {description} {content}".strip()
    if not all_text:
        return "No content available."
    
    text = re.sub(r'\[.*?\]', '', all_text).strip()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if not sentences:
        return "Summary not available."
    
    if len(sentences) == 1:
        words = sentences[0].split()
        if len(words) > 15:
            mid = len(words) // 2
            return f"{' '.join(words[:mid])}. {' '.join(words[mid:])}."
        return sentences[0] + "."
    else:
        return f"{sentences[0]}. {sentences[1]}."

def analyze_sentiment(text):
    """Analyze sentiment"""
    if not text:
        return "Neutral", "neutral", 0.0
        
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        return "😊 Positive", "positive", polarity
    elif polarity < -0.1:
        return "😔 Negative", "negative", polarity
    else:
        return "😐 Neutral", "neutral", polarity

def detect_fake_news(text):
    """AI fake news detection using Gemini"""
    if GEMINI_API_KEY == 'your_gemini_key_here':
        return False, "Gemini API key required", 0.5
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Analyze this news text for authenticity. Respond ONLY with:
        VERDICT|CONFIDENCE|EXPLANATION
        
        VERDICT: REAL or FAKE
        CONFIDENCE: 0.0 to 1.0
        EXPLANATION: Brief reason (max 50 words)
        
        Text: "{text}"
        """
        
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        
        if len(parts) >= 3:
            verdict = parts[0].strip()
            confidence = float(parts[1].strip())
            explanation = parts[2].strip()
            
            is_fake = verdict == "FAKE"
            return is_fake, explanation, confidence
        else:
            return False, "Analysis unclear", 0.5
            
    except Exception as e:
        return False, "Analysis failed", 0.0

@app.route('/')
def index():
    """Serve the HTML page"""
    return render_template('news-analyzer.html')

@app.route('/api/country-news')
def country_news():
    """API endpoint for country-specific news"""
    country = request.args.get('country', 'us')
    articles = fetch_news(country=country)
    
    processed_articles = []
    for article in articles:
        title = article.get('title', 'No title')
        description = article.get('description', '')
        content = article.get('content', '')
        
        full_text = f"{title} {description} {content}".strip()
        summary = create_summary(title, description, content)
        sentiment, sentiment_class, score = analyze_sentiment(full_text)
        
        processed_articles.append({
            'title': title,
            'summary': summary,
            'sentiment': sentiment,
            'sentiment_class': sentiment_class,
            'source': article.get('source_name', 'Unknown'),
            'date': article.get('pubDate', '')[:10] if article.get('pubDate') else 'Unknown',
            'url': article.get('link', '')
        })
    
    return jsonify({'articles': processed_articles})

@app.route('/api/category-news')
def category_news():
    """API endpoint for category-specific news"""
    category = request.args.get('category', 'technology')
    articles = fetch_news(category=category)
    
    processed_articles = []
    for article in articles:
        title = article.get('title', 'No title')
        description = article.get('description', '')
        content = article.get('content', '')
        
        full_text = f"{title} {description} {content}".strip()
        summary = create_summary(title, description, content)
        sentiment, sentiment_class, score = analyze_sentiment(full_text)
        
        processed_articles.append({
            'title': title,
            'summary': summary,
            'sentiment': sentiment,
            'sentiment_class': sentiment_class,
            'source': article.get('source_name', 'Unknown'),
            'date': article.get('pubDate', '')[:10] if article.get('pubDate') else 'Unknown',
            'url': article.get('link', '')
        })
    
    return jsonify({'articles': processed_articles})

@app.route('/api/fake-news', methods=['POST'])
def fake_news():
    """API endpoint for fake news detection"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'error': 'No text provided'}), 400
    
    is_fake, explanation, confidence = detect_fake_news(text)
    
    return jsonify({
        'is_fake': is_fake,
        'verdict': 'FAKE NEWS DETECTED' if is_fake else 'APPEARS CREDIBLE',
        'explanation': explanation,
        'confidence': confidence
    })

if __name__ == '__main__':
    # Create templates directory and move HTML file there
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True, port=5000)