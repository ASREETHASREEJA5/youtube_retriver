import streamlit as st
import requests
import csv
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3/search'

# Function to get video links
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

    video_links = []
    for item in data.get('items', []):
        video_id = item['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video_links.append(video_url)

    return video_links

# Function to save feedback to CSV
def save_feedback_to_csv(video_feedback):
    file_name = "feedback_data.csv"
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Video URL', 'Feedback'])
        
        for video_url, feedback in video_feedback.items():
            writer.writerow([video_url, feedback])

# Function to load all feedbacks from CSV
def load_feedback_from_csv():
    file_name = "feedback_data.csv"
    feedbacks = []
    
    if os.path.isfile(file_name):
        with open(file_name, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            feedbacks = list(reader)
    
    return feedbacks

# Initialize session state
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = {}

st.title("YouTube Video Search")
st.write("Enter a question and get the top 5 YouTube video links related to it.")

# Host mode toggle
is_host = st.checkbox("Host Mode (View All Feedbacks)")

# Input field for question
question = st.text_input("Ask a question:")

if question:
    videos = get_video_links(question)

    if videos:
        st.write("Here are some video links related to your question:")
        for idx, video in enumerate(videos, 1):
            st.write(f"{idx}. {video}")
            feedback_key = f"video_{idx}_feedback"
            
            if feedback_key not in st.session_state:
                st.session_state.feedback_data[video] = "Select"

            feedback = st.radio(
                f"Feedback for video {idx}",
                ('Select', 'Like', 'Dislike'),
                key=feedback_key
            )

            st.session_state.feedback_data[video] = feedback

        if st.button("Save Feedback"):
            save_feedback_to_csv(st.session_state.feedback_data)
            st.success("Feedback saved successfully!")
    else:
        st.write("No videos found.")

# Display all feedbacks only in Host Mode
if is_host:
    st.write("Collected Feedbacks:")
    feedbacks = load_feedback_from_csv()
    if feedbacks:
        for feedback in feedbacks:
            st.write(f"Video: {feedback[0]} | Feedback: {feedback[1]}")
    else:
        st.write("No feedbacks available yet.")
