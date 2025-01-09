import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')
# Replace with your YouTube API key
BASE_URL = 'https://www.googleapis.com/youtube/v3/search'

# Initialize the feedback count
feedback_count = {"👍": 0, "👎": 0}

def get_video_links(question):
    params = {
        'part': 'snippet',
        'q': question,
        'key': API_KEY,
        'type': 'video',
        'maxResults': 5  # Limit the results to top 5
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    video_links = []
    for item in data['items']:
        video_id = item['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video_links.append(video_url)

    return video_links

# Streamlit UI
st.title("YouTube Video Search")
st.write("Enter a question and get the top 5 YouTube video links related to it.")

# Input field for user to enter a question
question = st.text_input("Ask a question:")

if question:
    # Get video links for the entered question
    videos = get_video_links(question)
    
    # Display the video links and update feedback count for terminal output
    if videos:
        st.write("Here are some video links related to your question:")
        for idx, video in enumerate(videos, 1):
            st.write(f"{idx}. {video}")
            
            # Simulate feedback collection in terminal (no buttons displayed in Streamlit)
            feedback = st.radio(f"Feedback for video {idx}", ('Select', '👍', '👎'), key=idx)

            if feedback == '👍':
                feedback_count["👍"] += 1
            elif feedback == '👎':
                feedback_count["👎"] += 1

        # Print the feedback count to the console (for terminal output)
        print("Current feedback count in terminal:")
        print(f"👍: {feedback_count['👍']}")
        print(f"👎: {feedback_count['👎']}")

    else:
        st.write("No videos found.")
