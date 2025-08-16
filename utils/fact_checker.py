import requests
from urllib.parse import urlparse
import PyPDF2
import io
from utils.ai_services import check_fact_with_gemini
import re
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    """Extract text content from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(strip=True)
        text = re.sub(r'\s+', ' ', text)
        
        # Limit text length
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        return text
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        text = re.sub(r'\s+', ' ', text.strip())
        
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        return text
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def validate_url(url):
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def fact_check_from_input(text_input, pdf_file, url_input):
    """Process different types of input for fact-checking"""
    content = ""
    source_info = ""
    
    if text_input:
        content = text_input
        source_info = "Direct text input"
    elif pdf_file:
        content = extract_text_from_pdf(pdf_file)
        source_info = f"PDF file: {pdf_file.name}"
    elif url_input:
        if validate_url(url_input):
            content = extract_text_from_url(url_input)
            source_info = f"URL: {url_input}"
        else:
            return {
                "result": "Invalid URL",
                "confidence": "0",
                "explanation": "Please provide a valid URL starting with http:// or https://",
                "source_info": "Invalid input"
            }
    else:
        return {
            "result": "No Input",
            "confidence": "0",
            "explanation": "Please provide text, upload a PDF, or enter a URL to fact-check.",
            "source_info": "No input provided"
        }
    
    if not content or content.startswith("Error"):
        return {
            "result": "Processing Error",
            "confidence": "0",
            "explanation": content if content.startswith("Error") else "Could not extract content for analysis.",
            "source_info": source_info
        }
    
    # Perform fact check
    fact_check_result = check_fact_with_gemini(content[:2000])  # Limit content length
    fact_check_result["source_info"] = source_info
    
    return fact_check_result