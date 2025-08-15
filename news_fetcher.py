import requests

API_KEY = "1ff42a79cef74cbcbb4ceaa9e683771c"

def fetch_news(query, language="en", page_size=5):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'apiKey': API_KEY,
        'language': language,
        'pageSize': page_size,
        'sortBy': 'publishedAt',
    }
    response = requests.get(url, params=params)
    data = response.json()
    # Ensure articles exist
    return data.get('articles', [])
