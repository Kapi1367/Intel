from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

YOUTUBE_API_KEY = 'AIzaSyBZvZDcEUHoCjSRNowYkfE1ZfPtOCQxHJk'  # Replace with your actual API key

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
        # Simulate using summarization agent
        summary = summarize_text(video_info['description'])
        video_info['summary'] = summary
        video_info_list.append(video_info)

    return video_info_list

# Summarize video content (you can replace this with an AI model like GPT)
def summarize_text(text):
    return text[:100] + '...' if len(text) > 100 else text

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

if __name__ == '__main__':  # Fixed main check
    app.run(debug=True)