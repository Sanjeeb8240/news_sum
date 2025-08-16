from datetime import datetime
import pytz

def get_greeting():
    """Get time-based greeting in IST"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    hour = current_time.hour
    
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"