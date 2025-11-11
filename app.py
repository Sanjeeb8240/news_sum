from flask import Flask, render_template, request, jsonify
import requests
from textblob import TextBlob
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NEWSDATA_API_KEY = os.getenv('NEWSDATA_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

NEWSDATA_API_URL = 'https://newsdata.io/api/1/latest'

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print("⚠️ Gemini API key configuration failed:", e)

def fetch_news(country=None, category=None, size=10):
    """Fetch news from NewsData.io"""
    params = {
        'apikey': NEWSDATA_API_KEY,
        'size': min(size, 15),
        'language': 'en'
    }
    if country:
        params['country'] = country
    if category:
        params['category'] = category

    try:
        response = requests.get(NEWSDATA_API_URL, params=params, timeout=10)
        return response.json().get('results', [])
    except Exception as e:
        print("❌ Error fetching news:", e)
        return []

def create_summary(title, desc, content):
    text = f"{desc} {content}".strip()

    text = re.sub(r'\s*\bONLY AVAILABLE IN PAID PLANS\.?\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[.*?\]', '', text) 

    if title and title.lower() in text.lower():
        text = re.sub(re.escape(title), '', text, flags=re.IGNORECASE)

    sentences = re.split(r'(?<=[.!?])\s+', text)
    summary = " ".join(sentences[:2]).strip()

    if not summary:
        summary = desc or title
    return summary


def analyze_sentiment(text):
    """sentiment analysis"""
    if not text:
        return "Neutral", "neutral", 0.0
        
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        return "😊 Positive", "positive", polarity
    elif polarity < -0.1:
        return "😔 Negative", "negative", polarity
    return "😐 Neutral", "neutral", polarity

def detect_fake_news(text):
    """Gemini 2.5 Flash-powered fake news detector (outputs 'Real' or 'Fake')"""
    if not GEMINI_API_KEY:
        return "Error: Missing Gemini API key"
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        You are an AI fake-news detector.
        Respond with only one word: Real or Fake.
        Statement: "{text}"
        """
        response = model.generate_content(prompt)
        ai_reply = response.text.strip().lower()

        if "fake" in ai_reply:
            return "Fake"
        elif "real" in ai_reply:
            return "Real"
        return "Unclear"
    except Exception as e:
        print("❌ Fake news detection error:", str(e))
        return "Error"

def process_articles(articles):
    """Process and enrich fetched articles with summary and sentiment"""
    processed = []
    for a in articles:
        title = a.get('title', 'No title')
        desc = a.get('description', '')
        content = a.get('content', '')
        full_text = f"{title} {desc} {content}".strip()
        summary = create_summary(title, desc, content)
        sentiment, sentiment_class, _ = analyze_sentiment(full_text)
        
        processed.append({
            'title': title,
            'summary': summary,
            'sentiment': sentiment,
            'sentiment_class': sentiment_class,
            'source': a.get('source_name', 'Unknown'),
            'date': a.get('pubDate', '')[:10] if a.get('pubDate') else 'Unknown',
            'url': a.get('link', '')
        })
    return processed

@app.route('/')
def index():
    return render_template('news-analyzer.html')

@app.route('/api/country-news')
def country_news():
    country = request.args.get('country', 'us')
    articles = fetch_news(country=country)
    return jsonify({'articles': process_articles(articles)})

@app.route('/api/category-news')
def category_news():
    category = request.args.get('category', 'technology')
    articles = fetch_news(category=category)
    return jsonify({'articles': process_articles(articles)})

@app.route("/api/fake-news", methods=["POST"])
def fake_news():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"verdict": "❌ No text provided"}), 400

    verdict = detect_fake_news(text)
    if verdict == "Fake":
        result = "🚨 Fake News Detected"
    elif verdict == "Real":
        result = "✅ Real News"
    elif verdict.startswith("Error"):
        result = "⚠️ Error analyzing the news"
    else:
        result = "⚠️ Unable to determine authenticity"

    return jsonify({"verdict": result})

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True, port=5000)
