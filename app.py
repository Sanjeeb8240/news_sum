import streamlit as st
from news_fetcher import fetch_news
from summarizer import summarize_text
from user_data import get_user_topics, set_user_topics

# 1. App title and description
st.title("Personalized News Summarizer Bot")
st.write(
    "Get concise summaries of the latest news, tailored to your interests!"
)

# 2. User login (basic, can be a simple username prompt)
username = st.text_input("Enter Your Name to Start:", max_chars=25)

if username:
    # 3. Topic selection
    st.subheader(f"Welcome, {username}! Select your news interests:")
    topic_options = ['Technology', 'Sports', 'Politics', 'Business', 'Health', 'Science', 'World', 'Entertainment']
    selected_topics = st.multiselect(
        "Choose topics (at least one):",
        topic_options,
        default=get_user_topics(username)
    )
    if st.button("Save Preferences"):
        set_user_topics(username, selected_topics)
        st.success("Your topics have been saved!")

    # 4. Show personalized news button
    if selected_topics:
        if st.button("Show My News Summaries"):
            for topic in selected_topics:
                st.subheader(f"{topic} News")
                articles = fetch_news(topic)
                if not articles:
                    st.warning("No news found for this topic.")
                    continue
                for a in articles:
                    st.markdown(f"**{a['title']}**")
                    # Sometimes content is None, fall back to description
                    text = (a.get('content') or a.get('description') or "")
                    summary = summarize_text(text)
                    st.write(summary)
                    st.caption(f"Source: {a['source']['name']}")
    else:
        st.info("Please select at least one topic above.")

    # 5. (Optional) Feedback section
    st.subheader("Help us improve! What do you think of these summaries?")
    feedback = st.radio("Your feedback:", ['Great', 'Okay', 'Poor'])
    if st.button("Submit Feedback"):
        st.success("Thanks for your feedback!")
else:
    st.info("Please enter your name above to continue.")
