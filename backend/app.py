from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import csv
import os
import random
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize OpenAI client with API key
api_key = os.getenv("OPENAI_API_KEY")

# Fix: If the API key starts with "OPENAI_API_KEY=", extract just the key value
if api_key and api_key.startswith("OPENAI_API_KEY="):
    api_key = api_key.split("=", 1)[1]

client = openai.OpenAI(
    api_key=api_key
)

# Initialize CSV file
CSV_FILE = "trivia_questions.csv"
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer"])

# Initialize stats file
STATS_FILE = "stats.json"
if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"correct_answers": 0, "wrong_answers": 0, "total_questions": 0}, f, indent=2)

# Function to read stats

def read_stats():
    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Function to write stats

def write_stats(stats):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

@app.route('/generate-question', methods=['POST'])
def generate_question():
    try:
        # Generate trivia question using OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a trivia question generator. Generate a random multiple-choice trivia question with 4 options (A, B, C, D) and indicate the correct answer. Format the response as JSON with keys: 'question', 'options' (list of 4 strings), 'correct_answer' (string). Make sure the options are unique and the correct answer is one of the options. Keep it simple."}
            ],
            temperature=0.7,
            max_tokens=300,
            timeout=10
        )
        
        trivia_data = response.choices[0].message.content.strip()
        print(f"Raw OpenAI response: {trivia_data}")
        
        # Clean the response by removing markdown backticks and JSON label
        import re
        trivia_data = re.sub(r'^```json\n|```$', '', trivia_data.strip())
        print(f"Cleaned response: {trivia_data}")
        
        # Parse the JSON response
        import json
        trivia_json = json.loads(trivia_data)
        
        question = trivia_json["question"]
        options = trivia_json["options"]
        correct_answer = trivia_json["correct_answer"]
        
        print(f"Processed question: {question}")
        print(f"Options: {options}")
        print(f"Correct answer: {correct_answer}")
        
        # Log to CSV
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([question, options[0], options[1], options[2], options[3], correct_answer])
        
        return jsonify({
            "success": True,
            "question": question,
            "options": options,
            "correct_answer": correct_answer
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/check-answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    user_answer = data.get('user_answer')
    correct_answer = data.get('correct_answer')
    
    is_correct = user_answer == correct_answer
    
    return jsonify({
        "success": True,
        "is_correct": is_correct,
        "correct_answer": correct_answer
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        stats = read_stats()
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/update-stats', methods=['POST'])
def update_stats():
    try:
        data = request.get_json()
        is_correct = data.get('is_correct')
        
        stats = read_stats()
        stats['total_questions'] += 1
        
        if is_correct:
            stats['correct_answers'] += 1
        else:
            stats['wrong_answers'] += 1
        
        write_stats(stats)
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
