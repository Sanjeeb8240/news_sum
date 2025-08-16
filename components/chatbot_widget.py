import streamlit as st
from utils.ai_services import answer_question_with_gemini

def render_chatbot_widget():
    """Render the circular chatbot widget"""
    
    # Initialize chatbot state
    if 'chatbot_open' not in st.session_state:
        st.session_state.chatbot_open = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "👋 Hi! I'm your AI news assistant. Ask me anything about news or current events!"}
        ]
    
    # Only show chatbot in sidebar to prevent page interference
    with st.sidebar:
        st.markdown("### 💬 AI Assistant")
        
        # Toggle chatbot visibility
        if st.button("🤖 Open/Close Chat", use_container_width=True):
            st.session_state.chatbot_open = not st.session_state.chatbot_open
        
        # Show chatbot interface if open
        if st.session_state.chatbot_open:
            st.markdown("---")
            
            # Display chat messages (last 3 to save space)
            for message in st.session_state.chat_messages[-3:]:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**AI:** {message['content']}")
            
            # Chat input
            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_area("Ask about news:", height=80, key="chat_input", placeholder="Type your question here...")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    send_button = st.form_submit_button("Send")
                with col2:
                    clear_button = st.form_submit_button("Clear")
                
                if send_button and user_input:
                    # Add user message
                    st.session_state.chat_messages.append({"role": "user", "content": user_input})
                    
                    # Get AI response
                    with st.spinner("Thinking..."):
                        ai_response = answer_question_with_gemini(user_input)
                    
                    # Add AI response
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                    st.rerun()
                
                if clear_button:
                    st.session_state.chat_messages = [
                        {"role": "assistant", "content": "👋 Hi! I'm your AI news assistant. Ask me anything about news or current events!"}
                    ]
                    st.rerun()

def add_news_to_context(title, summary, source):
    """Add news summary to context for chatbot"""
    if 'news_context' not in st.session_state:
        st.session_state.news_context = []
    
    news_item = f"Title: {title}\nSummary: {summary}\nSource: {source}"
    st.session_state.news_context.append(news_item)
    
    # Keep only last 5 news items to avoid memory issues
    if len(st.session_state.news_context) > 5:
        st.session_state.news_context = st.session_state.news_context[-5:]