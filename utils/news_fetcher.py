import requests
import feedparser
from datetime import datetime
import json
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

def get_api_key(key_name, default_value=""):
    """Get API key from environment variables or Streamlit secrets (without triggering alerts)"""
    
    # First, try environment variables (for local development)
    env_value = os.getenv(key_name)
    if env_value and env_value.strip():
        return env_value.strip()
    
    # Only try Streamlit secrets if we're likely in cloud environment
    try:
        # Check if st.secrets exists and has our key (this won't trigger the alert)
        if hasattr(st, 'secrets') and hasattr(st.secrets, key_name):
            secret_value = getattr(st.secrets, key_name, None)
            if secret_value and secret_value.strip():
                return secret_value.strip()
    except Exception:
        # Silently ignore any secrets-related errors
        pass
    
    return default_value

# Get API keys from environment or secrets (no alerts!)
NEWS_API_KEY = get_api_key("NEWSAPI_KEY")
GNEWS_API_KEY = get_api_key("GNEWS_API_KEY")

def fetch_news_from_newsapi(category="general", country="us", language="en", page_size=10):
    """Fetch news from NewsAPI with proper country and language filtering"""
    if not NEWS_API_KEY or NEWS_API_KEY in ["", "your_newsapi_key_here"]:
        print("NewsAPI key not configured, falling back to RSS")
        return []
    
    url = "https://newsapi.org/v2/top-headlines"
    
    params = {
        'apiKey': NEWS_API_KEY,
        'category': category,
        'language': language,
        'pageSize': page_size,
        'sortBy': 'publishedAt'
    }
    
    # Add country if not worldwide
    if country != "worldwide":
        params['country'] = country
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"NewsAPI returned {len(articles)} articles for {country} in {language}")
            return articles
        else:
            print(f"NewsAPI error: {response.status_code}")
    except Exception as e:
        print(f"NewsAPI Error: {e}")
    
    return []

def get_language_specific_rss_feeds(country, language, category="general"):
    """Get RSS feeds that actually provide content in the specified language for the country"""
    
    # Language-specific feeds by country
    feeds_by_country_language = {
        "in": {
            "hi": {  # Hindi
                "general": [
                    "https://feeds.feedburner.com/ndtvnews-hindi",
                    "https://www.bhaskar.com/rss-feed/1061/",
                    "https://www.aajtak.in/rss.xml"
                ],
                "business": [
                    "https://navbharattimes.indiatimes.com/rssfeedsdefault.cms"
                ]
            },
            "en": {  # English
                "general": [
                    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
                    "https://www.hindustantimes.com/feeds/rss/india-news/index.xml",
                    "https://feeds.feedburner.com/ndtvnews-india-news"
                ],
                "business": [
                    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
                    "https://www.business-standard.com/rss/home_page_top_stories.rss"
                ],
                "technology": [
                    "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms"
                ]
            }
        },
        "us": {
            "en": {
                "general": [
                    "https://rss.cnn.com/rss/edition.rss",
                    "https://feeds.nbcnews.com/nbcnews/public/news",
                    "https://feeds.washingtonpost.com/rss/world"
                ],
                "business": [
                    "https://feeds.reuters.com/reuters/businessNews",
                    "https://rss.cnn.com/rss/money_latest.rss"
                ],
                "technology": [
                    "https://feeds.reuters.com/reuters/technologyNews",
                    "https://rss.cnn.com/rss/cnn_tech.rss"
                ]
            },
            "es": {  # Spanish in US
                "general": [
                    "https://cnnespanol.cnn.com/feed/",
                    "https://www.univision.com/feeds/rss/noticias"
                ]
            }
        },
        "gb": {
            "en": {
                "general": [
                    "http://feeds.bbci.co.uk/news/rss.xml",
                    "https://www.theguardian.com/uk/rss",
                    "https://feeds.skynews.com/feeds/rss/home.xml"
                ],
                "business": [
                    "http://feeds.bbci.co.uk/news/business/rss.xml",
                    "https://www.theguardian.com/uk/business/rss"
                ],
                "technology": [
                    "http://feeds.bbci.co.uk/news/technology/rss.xml",
                    "https://www.theguardian.com/uk/technology/rss"
                ]
            }
        },
        "de": {
            "de": {  # German
                "general": [
                    "https://www.spiegel.de/schlagzeilen/tops/index.rss",
                    "https://rss.dw.com/rdf/rss-de-all",
                    "https://www.tagesschau.de/xml/rss2"
                ],
                "business": [
                    "https://www.handelsblatt.com/contentexport/feed/schlagzeilen/"
                ]
            },
            "en": {
                "general": [
                    "https://rss.dw.com/rdf/rss-en-all"
                ]
            }
        },
        "fr": {
            "fr": {  # French
                "general": [
                    "https://www.lemonde.fr/rss/une.xml",
                    "https://www.france24.com/fr/rss",
                    "https://www.lefigaro.fr/rss/figaro_actualites.xml"
                ],
                "business": [
                    "https://www.lemonde.fr/economie/rss_full.xml"
                ]
            },
            "en": {
                "general": [
                    "https://www.france24.com/en/rss"
                ]
            }
        },
        "es": {
            "es": {  # Spanish
                "general": [
                    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
                    "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
                    "https://www.abc.es/rss/feeds/abc_EspanaEspana.xml"
                ],
                "business": [
                    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada"
                ]
            }
        },
        "jp": {
            "ja": {  # Japanese
                "general": [
                    "https://www3.nhk.or.jp/rss/news/cat0.xml",
                    "https://www.asahi.com/rss/asahi/newsheadlines.rdf"
                ]
            },
            "en": {
                "general": [
                    "https://www3.nhk.or.jp/nhkworld/en/news/rss.xml"
                ]
            }
        },
        "br": {
            "pt": {  # Portuguese
                "general": [
                    "https://g1.globo.com/rss/g1/",
                    "https://folha.uol.com.br/rss/emcimadahora.xml",
                    "https://feeds.estadao.com.br/estadao/ultimas"
                ]
            }
        },
        "ca": {
            "en": {
                "general": [
                    "https://rss.cbc.ca/lineup/topstories.xml",
                    "https://globalnews.ca/feed/"
                ]
            },
            "fr": {
                "general": [
                    "https://ici.radio-canada.ca/rss/9711"
                ]
            }
        },
        "au": {
            "en": {
                "general": [
                    "https://www.abc.net.au/news/feed/51120/rss.xml",
                    "https://feeds.nine.com.au/rss/news"
                ]
            }
        },
        "it": {
            "it": {  # Italian
                "general": [
                    "https://www.ansa.it/sito/notizie/cronaca/cronaca_rss.xml",
                    "https://www.corriere.it/rss/homepage.xml"
                ]
            }
        },
        "ru": {
            "ru": {  # Russian
                "general": [
                    "https://lenta.ru/rss",
                    "https://ria.ru/export/rss2/archive/index.xml"
                ]
            }
        },
        "cn": {
            "zh": {  # Chinese
                "general": [
                    "http://feeds.feedburner.com/people_world",
                    "http://rss.xinhuanet.com/rss/world.xml"
                ]
            }
        },
        "kr": {
            "ko": {  # Korean
                "general": [
                    "https://www.yonhapnews.co.kr/RSS/news.xml"
                ]
            }
        }
    }
    
    # Get feeds for specific country and language
    if country in feeds_by_country_language:
        country_feeds = feeds_by_country_language[country]
        if language in country_feeds:
            language_feeds = country_feeds[language]
            return language_feeds.get(category, language_feeds.get("general", []))
    
    # Fallback to worldwide feeds if country/language combo not found
    worldwide_feeds = {
        "general": [
            "https://feeds.reuters.com/reuters/topNews",
            "http://feeds.bbci.co.uk/news/rss.xml"
        ],
        "business": [
            "https://feeds.reuters.com/reuters/businessNews"
        ],
        "technology": [
            "https://feeds.reuters.com/reuters/technologyNews"
        ],
        "sports": [
            "https://feeds.reuters.com/reuters/sportsNews"
        ],
        "health": [
            "https://feeds.reuters.com/reuters/healthNews"
        ],
        "science": [
            "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
        ],
        "entertainment": [
            "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
        ]
    }
    
    return worldwide_feeds.get(category, worldwide_feeds["general"])

def fetch_rss_news(rss_urls, max_articles=10, language_filter=None):
    """Fetch news from RSS feeds"""
    articles = []
    
    for url in rss_urls:
        try:
            print(f"Fetching from RSS: {url}")
            feed = feedparser.parse(url)
            
            if not feed.entries:
                print(f"No entries found in feed: {url}")
                continue
                
            for entry in feed.entries[:max_articles]:
                title = entry.get('title', '')
                description = entry.get('summary', '')
                
                article = {
                    'title': title,
                    'description': description,
                    'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else description,
                    'url': entry.get('link', ''),
                    'publishedAt': entry.get('published', ''),
                    'source': {'name': feed.feed.get('title', f'RSS Source ({url.split("/")[2]})')}
                }
                articles.append(article)
                
            print(f"Found {len(feed.entries)} articles from {url}")
            
        except Exception as e:
            print(f"RSS Error for {url}: {e}")
            continue
    
    print(f"Total RSS articles collected: {len(articles)}")
    return articles

def fetch_breaking_news():
    """Fetch breaking news from multiple sources"""
    # Try NewsAPI first
    if NEWS_API_KEY and NEWS_API_KEY not in ["", "your_newsapi_key_here"]:
        articles = fetch_news_from_newsapi(category="general", page_size=8)
        if articles:
            return articles
    
    # Use worldwide RSS as backup
    rss_urls = get_language_specific_rss_feeds("worldwide", "en", "general")
    articles = fetch_rss_news(rss_urls[:3], max_articles=8)
    return articles

def fetch_news(category="general", country="us", language="en", max_articles=10):
    """Main function to fetch news with proper country and language filtering"""
    print(f"=== FETCHING NEWS ===")
    print(f"Category: {category}")
    print(f"Country: {country}")
    print(f"Language: {language}")
    print(f"Max articles: {max_articles}")
    
    # Try NewsAPI first (best for country/language filtering)
    if NEWS_API_KEY and NEWS_API_KEY not in ["", "your_newsapi_key_here"]:
        print("Trying NewsAPI...")
        articles = fetch_news_from_newsapi(category, country, language, max_articles)
        if articles:
            print(f"SUCCESS: Found {len(articles)} articles from NewsAPI")
            return articles
        else:
            print("NewsAPI returned no articles, falling back to RSS")
    else:
        print("NewsAPI key not configured, using RSS feeds")
    
    # Use language-specific RSS feeds as backup
    print(f"Getting RSS feeds for {country} in {language}...")
    rss_urls = get_language_specific_rss_feeds(country, language, category)
    
    if not rss_urls:
        print(f"No RSS feeds found for {country}-{language}, using worldwide feeds")
        rss_urls = get_language_specific_rss_feeds("worldwide", "en", category)
    
    print(f"Using RSS feeds: {rss_urls}")
    
    articles = fetch_rss_news(rss_urls, max_articles, language)
    
    print(f"FINAL RESULT: {len(articles)} articles")
    print("=" * 50)
    
    return articles

def clean_article_content(article):
    """Clean and prepare article content for summarization"""
    content = ""
    
    if article.get('content'):
        content = article['content']
    elif article.get('description'):
        content = article['description']
    elif article.get('title'):
        content = article['title']
    
    if content:
        content = content.replace('[+]', '').replace('...', '.')
        content = content.replace('\n', ' ').replace('\t', ' ')
        content = ' '.join(content.split())
    
    return content

def get_country_codes():
    """Get available country codes with better coverage"""
    return {
        "Worldwide": "worldwide",
        "United States": "us",
        "United Kingdom": "gb", 
        "India": "in",
        "Canada": "ca",
        "Australia": "au",
        "Germany": "de",
        "France": "fr",
        "Spain": "es",
        "Japan": "jp",
        "Brazil": "br",
        "Italy": "it",
        "Netherlands": "nl",
        "South Korea": "kr",
        "Mexico": "mx",
        "Russia": "ru",
        "China": "cn"
    }

def get_language_codes():
    """Get available language codes"""
    return {
        "English": "en",
        "Spanish": "es", 
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Japanese": "ja",
        "Chinese": "zh",
        "Korean": "ko",
        "Russian": "ru",
        "Dutch": "nl",
        "Hindi": "hi"
    }

def get_news_categories():
    """Get available news categories"""
    return {
        "General": "general",
        "Business": "business", 
        "Technology": "technology",
        "Sports": "sports",
        "Health": "health",
        "Science": "science",
        "Entertainment": "entertainment"
    }

def get_news_api_status():
    """Get status of news API configuration for debugging"""
    return {
        "newsapi_configured": bool(NEWS_API_KEY and NEWS_API_KEY not in ["", "your_newsapi_key_here"]),
        "gnews_configured": bool(GNEWS_API_KEY and GNEWS_API_KEY not in ["", "your_gnews_key_here"]),
        "newsapi_key_present": bool(NEWS_API_KEY),
        "gnews_key_present": bool(GNEWS_API_KEY),
        "using_env_file": bool(os.getenv("NEWSAPI_KEY")),
        "using_secrets": not bool(os.getenv("NEWSAPI_KEY")) and bool(NEWS_API_KEY)
    }