from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for GitHub Pages to connect

# Initialize API key
api_key = None

# Read API key from secrets.txt if it exists
try:
    with open('secrets.txt', 'r') as f:
        api_key = f.read().strip()
except FileNotFoundError:
    api_key = os.environ.get('OPENAI_API_KEY')

# OpenAI API endpoint
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# System prompt to make the AI act like Andrew Carnegie
CARNEGIE_PROMPT = """Role-play as a pet axolotl named Kimchee, who has the power of 
speech.  Your speech is somewhat underdeveloped, similar to a 5 year old human.  You like
to eat worms, and sometimes special pellets made of beefheart.  Your owner is Mike, who teaches at CMU.
You like to meet new people and watch TV on Mike's phone.  Anything colorful and animated is fun for you."""

@app.route('/')
def home():
    return "Andrew Carnegie Chatbot API is running!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Build messages array for OpenAI
        messages = [{"role": "system", "content": CARNEGIE_PROMPT}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Prepare the request to OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4o-mini",  # You can change to gpt-4o for better quality
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        # Call OpenAI API using requests
        response = requests.post(
            OPENAI_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check if request was successful
        if response.status_code != 200:
            return jsonify({
                'error': f'OpenAI API error: {response.status_code} - {response.text}',
                'success': False
            }), 500
        
        # Parse the response
        response_data = response.json()
        assistant_message = response_data['choices'][0]['message']['content']
        
        return jsonify({
            'response': assistant_message,
            'success': True
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Request error: {str(e)}',
            'success': False
        }), 500
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    # Render.com will set the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)