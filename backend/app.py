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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "trivia_questions.csv")
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer"])

# Initialize stats file
STATS_FILE = os.path.join(BASE_DIR, "stats.json")
if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"correct_answers": 0, "wrong_answers": 0, "total_questions": 0}, f, indent=2)

# Function to read stats
def read_stats():
    try:
        print(f"Reading stats from: {STATS_FILE}")
        print(f"File exists: {os.path.exists(STATS_FILE)}")
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                print(f"Read stats: {stats}")
                return stats
        else:
            # If file doesn't exist, create default stats
            default_stats = {"correct_answers": 0, "wrong_answers": 0, "total_questions": 0}
            print(f"Creating default stats: {default_stats}")
            write_stats(default_stats)
            return default_stats
    except Exception as e:
        print(f"Error reading stats: {str(e)}")
        # Return default stats on error
        return {"correct_answers": 0, "wrong_answers": 0, "total_questions": 0}

# Function to write stats
def write_stats(stats):
    try:
        print(f"Writing stats to: {STATS_FILE}")
        print(f"Stats to write: {stats}")
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        print(f"Stats written successfully")
        # Verify write was successful
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            verified_stats = json.load(f)
            print(f"Verified stats: {verified_stats}")
    except Exception as e:
        print(f"Error writing stats: {str(e)}")

@app.route('/generate-question', methods=['POST'])
def generate_question():
    try:
        # Read existing questions to check for duplicates
        existing_questions = set()
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if row:
                        existing_questions.add(row[0].strip().lower())
            print(f"Loaded {len(existing_questions)} existing questions")
        except Exception as e:
            print(f"Error reading existing questions: {str(e)}")
            existing_questions = set()
        
        max_attempts = 5
        attempt = 0
        trivia_json = None
        
        while attempt < max_attempts:
            attempt += 1
            print(f"Attempt {attempt} to generate unique question")
            
            # Generate trivia question using OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a trivia question generator. Generate a completely unique, random multiple-choice trivia question with 4 distinct options (A, B, C, D) and indicate the correct answer. Ensure this question is different from any standard trivia questions and covers diverse topics. Format the response as JSON with keys: 'question', 'options' (list of 4 strings), 'correct_answer' (string). Make sure all options are unique, plausible, and the correct answer is one of the options. Keep it simple but varied."}
                ],
                temperature=0.9,  # Increased temperature for more randomness
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
            
            # Check if question is duplicate
            if question.strip().lower() not in existing_questions:
                print("Generated unique question!")
                break
            else:
                print("Duplicate question found, generating new one...")
        
        if not trivia_json:
            return jsonify({
                "success": False,
                "error": "Could not generate a unique question after multiple attempts"
            })
        
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
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
