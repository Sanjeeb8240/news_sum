import streamlit as st
from utils.ai_services import get_rate_limit_info, get_api_status

def show_rate_limit_dashboard():
    """Display rate limit information in the sidebar"""
    
    with st.sidebar:
        st.markdown("### 🚦 API Status")
        
        # Get current status
        api_status = get_api_status()
        rate_info = get_rate_limit_info()
        
        # API Configuration
        if api_status['gemini_configured']:
            st.success("✅ Gemini API Connected")
        else:
            st.error("❌ Gemini API Not Configured")
        
        # Rate Limit Status
        st.markdown("**Rate Limits (Free Tier):**")
        st.metric(
            "Requests This Minute", 
            f"{rate_info['requests_last_minute']}/{rate_info['max_requests_per_minute']}"
        )
        
        # Warning if close to limit
        if rate_info['requests_last_minute'] >= 6:
            st.warning("⚠️ Approaching rate limit!")
        
        if not rate_info['can_make_request']:
            st.error(f"🚫 Rate limited! Wait {rate_info['seconds_until_next_available']:.0f}s")
        
        # Upgrade suggestion
        if rate_info['requests_last_minute'] >= 5:
            st.info("""
            💡 **Getting rate limited?**
            
            **Free Tier**: 10 req/min, 250 req/day
            **Tier 1**: 1000 req/min, 10k req/day
            
            [Upgrade to Paid Tier](https://ai.google.dev/gemini-api/docs/rate-limits#how-to-upgrade-to-the-next-tier)
            """)

def show_usage_tips():
    """Show usage optimization tips"""
    
    with st.expander("💡 Rate Limit Tips"):
        st.markdown("""
        ### 🚀 Optimize Your Usage:
        
        **Current Free Tier Limits:**
        - 📊 10 requests per minute
        - 📅 250 requests per day
        - 🎯 250k tokens per minute
        
        **Tips to Avoid Rate Limits:**
        1. ⏳ **Wait between requests** - App automatically adds delays
        2. 📝 **Shorten text inputs** - Less tokens = faster processing
        3. 🎯 **Use fewer articles** - Start with 3-5 instead of 10
        4. 🔄 **Batch operations** - Process multiple items together
        
        **Upgrade Options:**
        - 💳 **Tier 1**: $0+ billing → 1,000 req/min, 10k req/day
        - 🏢 **Tier 2**: $250+ spent → 2,000 req/min, 100k req/day
        - 🚀 **Tier 3**: $1,000+ spent → 10,000 req/min, 1M req/day
        """)

# Add this to your main app sidebar
def render_enhanced_sidebar():
    """Enhanced sidebar with rate limit monitoring"""
    show_rate_limit_dashboard()
    show_usage_tips()