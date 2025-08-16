import streamlit as st
import base64
from datetime import datetime

def load_css():
    """Load custom CSS for beautiful UI"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* MAJOR SPACING FIX - Remove all extra padding */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: none !important;
    }
    
    
    /* Header Styles - Minimal margin */
    .header-container {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        padding: 1rem 2rem;
        margin: -1rem -1rem 0.5rem -1rem !important;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px rgba(46, 134, 171, 0.3);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .header-left h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .header-left p {
        margin: 0.3rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .header-right {
        text-align: right;
    }
    
    .user-profile {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Welcome Card - Minimal spacing */
    .welcome-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08);
        margin: 0.5rem 0 1rem 0 !important;
        border-left: 4px solid #2E86AB;
    }
    
    .welcome-card h2 {
        color: #2E86AB;
        margin: 0 0 0.3rem 0 !important;
        font-size: 1.4rem;
        font-weight: 600;
    }
    
    .welcome-card p {
        color: #64748b;
        margin: 0 !important;
        font-size: 0.95rem;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 3px 12px rgba(46, 134, 171, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 18px rgba(46, 134, 171, 0.4);
    }
    
    /* Input Styles */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.6rem;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2E86AB;
        box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
    }
    
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    /* Remove space from columns */
    .row-widget.stHorizontal > div {
        padding: 0.25rem 0.5rem !important;
    }
    
    /* Tab Styles */
    .stTabs > div > div > div > div {
        font-weight: 500;
        font-size: 1rem;
    }
    
    /* Alert Styles */
    .stAlert {
        border-radius: 8px;
        border-left-width: 4px;
    }
    
    /* Expander Styles */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            text-align: center;
        }
        
        .header-right {
            text-align: center;
            margin-top: 0.5rem;
        }
        
        .main .block-container {
            padding: 0.5rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_header(username, greeting):
    """Create beautiful header with user info"""
    st.markdown(f"""
    <div class="header-container">
        <div class="header-content">
            <div class="header-left">
                <h1>🤖 AI News Assistant</h1>
                <p>{greeting}, {username}!</p>
            </div>
            <div class="header-right">
                <div class="user-profile">
                    <div style="font-weight: 500; font-size: 1rem;">👤 {username}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.1rem;">
                        {datetime.now().strftime("%B %d, %Y")}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)