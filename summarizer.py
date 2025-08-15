from transformers import pipeline

# Load model once at import
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_length=60, min_length=20):
    # NewsAPI may return very long or very short articles
    if len(text.split()) < 30:
        return text  # Too short, skip summarizing
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']
