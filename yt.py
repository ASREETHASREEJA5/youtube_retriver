import streamlit as st
import requests
import json
import os

API_KEY = 'AIzaSyDNnYA5vexObnFA-1vs_hvBkhBu6TNst00'
BASE_URL = 'https://www.googleapis.com/youtube/v3/search'
FEEDBACK_FILE = 'feedback.json'  # File to store feedback

# Initialize session state for video links and feedback
if 'video_links' not in st.session_state:
    st.session_state.video_links = []
if 'feedback' not in st.session_state:
    st.session_state.feedback = []

# Function to fetch YouTube video links
def get_video_links(question):
    params = {
        'part': 'snippet',
        'q': question,
        'key': API_KEY,
        'type': 'video',
        'maxResults': 5
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if 'error' in data:
        st.error(f"Error: {data['error']}")
        return []

    if 'items' not in data:
        st.warning("No items found in the response.")
        return []

    video_links = []
    for item in data['items']:
        video_id = item['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video_links.append(video_url)

    return video_links

# Function to save feedback
def save_feedback(video_url, feedback):
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump([], f)

    with open(FEEDBACK_FILE, 'r') as f:
        feedback_data = json.load(f)

    feedback_data.append({'video_url': video_url, 'feedback': feedback})

    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f)

# Function to retrieve feedback
def get_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return []

# Streamlit app
st.title("YouTube Video Search and Feedback")

# Query input
question = st.text_input("Enter your question:")
if st.button("Search"):
    if question:
        videos = get_video_links(question)
        st.session_state.video_links = videos
    else:
        st.warning("Please enter a question to search.")

# Display video links and feedback buttons
if st.session_state.video_links:
    st.subheader("Video Links:")
    for video in st.session_state.video_links:
        st.write(video)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"👍 Like {video}", key=f"like-{video}"):
                save_feedback(video, "like")
                st.session_state.feedback.append({'video_url': video, 'feedback': 'like'})
        with col2:
            if st.button(f"👎 Dislike {video}", key=f"dislike-{video}"):
                save_feedback(video, "dislike")
                st.session_state.feedback.append({'video_url': video, 'feedback': 'dislike'})

# Feedback records
st.subheader("Feedback Records")
if st.session_state.feedback:
    for record in st.session_state.feedback:
        st.write(f"Video: {record['video_url']} - Feedback: {record['feedback']}")
else:
    st.write("No feedback records found.")
