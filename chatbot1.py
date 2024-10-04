from flask import Flask, request, jsonify
import requests
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import spacy
from rake_nltk import Rake  # For keyword extraction
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Load Pegasus Model
model_name = "google/pegasus-xsum"  # A good model for summarization tasks
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

# Load spaCy for keyword extraction
nlp = spacy.load("en_core_web_sm")

# Dummy Agent Function (simulate LangChain-like agent for task management)
class TaskAgent:
    def __init__(self):  # Fixed constructor method
        self.tasks = []

    def decide_action(self, user_input):
        if 'video' in user_input.lower():
            return 'search_videos'
        elif 'summarize' in user_input.lower():
            return 'summarize_video'
        else:
            return 'unknown_task'

    def perform_task(self, action, query=None):
        if action == 'search_videos':
            return search_youtube_videos(query)
        elif action == 'summarize_video':
            return summarize_video_content(query)
        else:
            return {"error": "Unknown task"}

# Function to summarize text using Pegasus
def summarize_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    summary_ids = model.generate(inputs['input_ids'], max_length=100, num_beams=4, length_penalty=2.0)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Keyword extraction using RAKE
def extract_keywords(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()[:5]  # Top 5 keywords

# Search YouTube videos based on query
def search_youtube_videos(query):
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    search_params = {
        'part': 'snippet',
        'q': query,
        'key': YOUTUBE_API_KEY,
        'maxResults': 5,
        'type': 'video'
    }
    response = requests.get(search_url, params=search_params)
    search_results = response.json()

    video_ids = []
    for item in search_results.get('items', []):
        video_ids.append(item['id']['videoId'])

    videos_url = 'https://www.googleapis.com/youtube/v3/videos'
    videos_params = {
        'part': 'snippet',
        'id': ','.join(video_ids),
        'key': YOUTUBE_API_KEY
    }
    response = requests.get(videos_url, params=videos_params)
    videos_data = response.json()

    video_info_list = []
    for item in videos_data.get('items', []):
        video_info = {
            'title': item['snippet']['title'],
            'url': f"https://www.youtube.com/watch?v={item['id']}",
            'description': item['snippet']['description']
        }
        # Generate summary and extract keywords
        summary = summarize_text(video_info['description'])
        keywords = extract_keywords(summary)

        video_info['summary'] = summary
        video_info['keywords'] = keywords
        video_info_list.append(video_info)

    return video_info_list

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    query = request.json.get('query')  # User provides a query for video search or summarization
    
    # Instantiate the agent
    agent = TaskAgent()
    
    # Agent decides what action to take based on the input
    action = agent.decide_action(user_input)
    
    # Perform the task based on agent's decision
    response_data = agent.perform_task(action, query)
    
    return jsonify({"response": response_data})

if __name__ == '__main__':
    app.run(debug=True)