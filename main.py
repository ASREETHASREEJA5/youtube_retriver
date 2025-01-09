import streamlit as st
import requests
from langchain_groq import ChatGroq
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')
GROQ_API_KEY  = os.getenv('GROQ_API_KEY ')

# Streamlit app title
st.title('YouTube Video Search and Ranking')

# Input for the user question
question = st.text_input("Enter your question:", "")

# Initialize feedback counters
feedback_count = {'positive': 0, 'negative': 0}

llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-70b-versatile"
)

# Function to get video links and titles from YouTube API
SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
VIDEO_DETAILS_URL = 'https://www.googleapis.com/youtube/v3/videos'

def get_video_links_and_titles(query):
    params = {
        'part': 'snippet',
        'q': query,
        'key': API_KEY,
        'type': 'video',
        'maxResults': 10
    }

    response = requests.get(SEARCH_URL, params=params)

    if response.status_code != 200:
        st.error(f"Error fetching videos for '{query}'. Status code: {response.status_code}")
        return []

    data = response.json()
    if 'items' not in data:
        st.error(f"Error: 'items' key not found in the response for query '{query}'")
        return []

    video_data = []
    for item in data['items']:
        video_id = item['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        title = item['snippet']['title']
        video_data.append((title, video_url, video_id))

    return video_data

def get_video_details(video_ids):
    params = {
        'part': 'statistics,snippet',
        'id': ','.join(video_ids),
        'key': API_KEY
    }
    response = requests.get(VIDEO_DETAILS_URL, params=params)

    if response.status_code != 200:
        st.error(f"Error fetching video details. Status code: {response.status_code}")
        return []

    data = response.json()
    video_details = []
    for item in data['items']:
        video_id = item['id']
        stats = item.get('statistics', {})
        snippet = item.get('snippet', {})
        like_count = int(stats.get('likeCount', 0))
        comment_count = int(stats.get('commentCount', 0))
        published_date = snippet.get('publishedAt', "1970-01-01T00:00:00Z")
        published_years_ago = (datetime.now() - datetime.fromisoformat(published_date.replace("Z", ""))).days / 365
        video_details.append((video_id, like_count, comment_count, published_years_ago))

    return video_details

# When the user submits the question
if question:
    prompt = f"""
    Provide the top 2 most relevant search queries for YouTube related to the given question: "{question}". 
    Only return the headings or titles of the search queries without any descriptions.
    """

    res = llm.invoke(prompt)

    raw_ques = res.content.split('\n')

    ques = [re.sub(r'^\d+\.\s*', '', item).strip() for item in raw_ques if item.strip()]

    video_metadata = []
    video_ids = []
    for query in ques:
        videos = get_video_links_and_titles(query)
        video_metadata.extend(videos)
        video_ids.extend([video[2] for video in videos])  # Collect video IDs

    video_details = get_video_details(video_ids)
    video_details_dict = {vid[0]: vid[1:] for vid in video_details}  

    titles = [title for title, _, _ in video_metadata]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([question] + titles)

    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    ranked_videos = set()
    for (title, url, video_id), sim_score in zip(video_metadata, similarity_scores):
        like_count, comment_count, years_ago = video_details_dict.get(video_id, (0, 0, float('inf')))
        final_score = (
            sim_score * 0.6 +
            (like_count / 1000) * 0.2 + 
            (comment_count / 100) * 0.1 +  
            max(0, 1 - years_ago / 10) * 0.1  
        )
        ranked_videos.append(((title, url), final_score))
    ranked_videos = list(ranked_videos)

    ranked_videos.sort(key=lambda x: x[1], reverse=True)

    top_3_videos = ranked_videos[:3]

    # Display the top 3 video links with feedback buttons
    st.subheader("Top 3 Video Links:")
    for (title, url), _ in top_3_videos:
        st.write(f"[{title}]({url})")
        
        # Add feedback buttons after each video
        feedback = st.radio(f"Feedback for {title}:", ("", "Positive", "Negative"), key=url)
        if feedback == "Positive":
            feedback_count['positive'] += 1
        elif feedback == "Negative":
            feedback_count['negative'] += 1

    # Log feedback counts in the console
    st.write(f"Positive Feedback Count: {feedback_count['positive']}")
    st.write(f"Negative Feedback Count: {feedback_count['negative']}")
    print(f"Positive Feedback Count: {feedback_count['positive']}")
    print(f"Negative Feedback Count: {feedback_count['negative']}")
