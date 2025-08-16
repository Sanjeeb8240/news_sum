from textblob import TextBlob
from utils.ai_services import analyze_sentiment_with_gemini

def analyze_sentiment(text, use_ai=True):
    """Analyze sentiment of text"""
    if not text.strip():
        return {"sentiment": "Neutral", "confidence": "0", "explanation": "No content to analyze."}
    
    if use_ai:
        try:
            return analyze_sentiment_with_gemini(text)
        except:
            pass
    
    # Fallback to basic analysis
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        confidence = min(abs(polarity) * 100, 100)
        explanation = f"TextBlob analysis shows {sentiment.lower()} sentiment with polarity {polarity:.2f}"
        
        return {
            "sentiment": sentiment,
            "confidence": str(int(confidence)),
            "explanation": explanation
        }
    except Exception as e:
        return {
            "sentiment": "Error",
            "confidence": "0",
            "explanation": f"Error analyzing sentiment: {str(e)}"
        }