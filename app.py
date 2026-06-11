import requests
import json
import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Create database
def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, 
                  user_message TEXT, 
                  ai_response TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

def chat_with_ai(user_message):
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'mistral',
            'prompt': user_message,
            'stream': False
        }
    )
    result = response.json()
    return result['response']

def save_message(user_msg, ai_msg):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages VALUES (NULL, ?, ?, ?)',
              (user_msg, ai_msg, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT user_message, ai_response FROM messages ORDER BY id DESC LIMIT 10')
    messages = c.fetchall()
    conn.close()
    return messages

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    ai_response = chat_with_ai(user_message)
    save_message(user_message, ai_response)  # Save to database
    return jsonify({'response': ai_response})

@app.route('/history', methods=['GET'])
def history():
    messages = get_history()
    return jsonify({'messages': messages})

if __name__ == '__main__':
    app.run(debug=True, port=5000)