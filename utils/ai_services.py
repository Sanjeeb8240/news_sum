import google.generativeai as genai
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

def get_api_key(key_name, default_value=""):
    """Get API key from environment variables or Streamlit secrets"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass
    
    # Try environment variables (for local development)
    return os.getenv(key_name, default_value)

# Get API keys from environment or secrets
GEMINI_API_KEY = get_api_key("GEMINI_API_KEY")

def configure_gemini():
    """Configure Gemini API"""
    if GEMINI_API_KEY and GEMINI_API_KEY not in ["", "your_gemini_api_key_here"]:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    return False

def get_gemini_model():
    """Get Gemini model instance"""
    try:
        if configure_gemini():
            # Updated to use the new model name
            return genai.GenerativeModel('gemini-1.5-flash')
        return None
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return None

def summarize_text_with_gemini(text, style="concise", max_words=100):
    """Summarize text using Gemini API"""
    if not text.strip():
        return "No content to summarize."
    
    model = get_gemini_model()
    if not model:
        return "AI service unavailable. Please check your API configuration."
    
    # Create style-specific prompts
    style_prompts = {
        "concise": f"Provide a concise summary of the following news article in {max_words} words or less. Focus on the key facts and main points:",
        "detailed": f"Provide a detailed summary of the following news article in {max_words} words or less. Include background context and important details:",
        "bullet points": f"Summarize the following news article as bullet points in {max_words} words or less. Use • for each point:",
        "casual": f"Summarize the following news article in a casual, conversational tone in {max_words} words or less:",
        "formal": f"Provide a formal, professional summary of the following news article in {max_words} words or less:"
    }
    
    prompt = style_prompts.get(style, style_prompts["concise"]) + f"\n\nArticle: {text[:3000]}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini summarization error: {e}")
        return f"Error generating summary: {str(e)}"

def check_fact_with_gemini(text):
    """Check facts using Gemini API"""
    if not text.strip():
        return {"result": "No content to analyze.", "confidence": "0", "explanation": ""}
    
    model = get_gemini_model()
    if not model:
        return {
            "result": "Service unavailable", 
            "confidence": "0", 
            "explanation": "AI service unavailable. Please check your API configuration."
        }
    
    prompt = f"""
    Analyze the following text for factual accuracy. Consider:
    1. Are the claims verifiable?
    2. Do the facts seem consistent with known information?
    3. Are there any obvious signs of misinformation?
    
    Respond with:
    - RESULT: True/False/Uncertain
    - CONFIDENCE: (0-100)
    - EXPLANATION: Brief explanation of your assessment
    
    Text to analyze: {text[:2000]}
    """
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse the response
        lines = result_text.split('\n')
        result = {"result": "Uncertain", "confidence": "50", "explanation": result_text}
        
        for line in lines:
            if "RESULT:" in line:
                result["result"] = line.replace("RESULT:", "").strip()
            elif "CONFIDENCE:" in line:
                result["confidence"] = line.replace("CONFIDENCE:", "").strip().replace("%", "")
            elif "EXPLANATION:" in line:
                result["explanation"] = line.replace("EXPLANATION:", "").strip()
        
        return result
    except Exception as e:
        print(f"Gemini fact check error: {e}")
        return {
            "result": "Error", 
            "confidence": "0", 
            "explanation": f"Error analyzing content: {str(e)}"
        }

def answer_question_with_gemini(question, context=""):
    """Answer questions using Gemini API with optional context"""
    if not question.strip():
        return "Please ask a question."
    
    model = get_gemini_model()
    if not model:
        return "AI service unavailable. Please check your API configuration."
    
    if context:
        prompt = f"""
        Based on the following context, answer the question. If the context doesn't contain enough information, 
        provide a general answer but mention that more specific information isn't available in the context.
        
        Context: {context[:1000]}
        
        Question: {question}
        """
    else:
        prompt = f"Answer the following question clearly and concisely: {question}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Q&A error: {e}")
        return f"I'm sorry, I encountered an error while processing your question: {str(e)}"

def analyze_sentiment_with_gemini(text):
    """Analyze sentiment using Gemini API"""
    if not text.strip():
        return {"sentiment": "Neutral", "confidence": "0", "explanation": "No content to analyze."}
    
    model = get_gemini_model()
    if not model:
        return {
            "sentiment": "Unknown", 
            "confidence": "0", 
            "explanation": "AI service unavailable."
        }
    
    prompt = f"""
    Analyze the sentiment of the following text. Respond with:
    - SENTIMENT: Positive/Negative/Neutral
    - CONFIDENCE: (0-100)
    - EXPLANATION: Brief explanation of the sentiment analysis
    
    Text: {text[:1000]}
    """
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse the response
        lines = result_text.split('\n')
        result = {"sentiment": "Neutral", "confidence": "50", "explanation": result_text}
        
        for line in lines:
            if "SENTIMENT:" in line:
                result["sentiment"] = line.replace("SENTIMENT:", "").strip()
            elif "CONFIDENCE:" in line:
                result["confidence"] = line.replace("CONFIDENCE:", "").strip().replace("%", "")
            elif "EXPLANATION:" in line:
                result["explanation"] = line.replace("EXPLANATION:", "").strip()
        
        return result
    except Exception as e:
        print(f"Gemini sentiment analysis error: {e}")
        return {
            "sentiment": "Error", 
            "confidence": "0", 
            "explanation": f"Error analyzing sentiment: {str(e)}"
        }

def is_gemini_configured():
    """Check if Gemini API is properly configured"""
    return GEMINI_API_KEY and GEMINI_API_KEY not in ["", "your_gemini_api_key_here"]

def get_api_status():
    """Get status of API configuration for debugging"""
    return {
        "gemini_configured": is_gemini_configured(),
        "gemini_key_present": bool(GEMINI_API_KEY),
        "gemini_key_preview": f"{GEMINI_API_KEY[:10]}..." if GEMINI_API_KEY else "Not set"
    }

def list_available_models():
    """List available Gemini models (for debugging)"""
    try:
        if configure_gemini():
            models = genai.list_models()
            for model in models:
                print(f"Model: {model.name}")
                print(f"Supported methods: {model.supported_generation_methods}")
                print("---")
        else:
            print("API key not configured")
    except Exception as e:
        print(f"Error listing models: {e}")