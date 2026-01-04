# Trivia Game

A simple trivia game with Python backend and HTML/CSS/JS frontend that generates random trivia questions using OpenAI API.

## Features

- Generate random trivia MCQs using ChatGPT API
- Interactive frontend with smooth animations
- Real-time answer checking with visual feedback
- CSV logging of all questions asked
- Responsive design for all screen sizes

## Prerequisites

- Python 3.7+ installed
- OpenAI API key

## Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API key:**
   - Create a `.env` file in the backend directory if it doesn't exist
   - Open `.env` in a text editor
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

4. **Start the backend server:**
   ```bash
   python app.py
   ```
   - The server will run on `http://localhost:5000`

5. **Open the frontend:**
   - Navigate to the frontend directory
   - Simply open `index.html` in a web browser
   - No additional setup required for the frontend

## How to Play

1. Click the "Generate Question" button to get a new trivia question
2. Read the question and click on one of the four answer options
3. The game will immediately show if your answer was correct or not
   - Correct answers are highlighted in green
   - Wrong answers are highlighted in red
4. Click "Generate Question" again to get a new question

## Project Structure

```
├── backend/                    # Python backend directory
│   ├── app.py                  # Flask application with OpenAI API integration
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (API keys)
│   └── trivia_questions.csv    # Generated CSV with all questions (created automatically)
├── index.html                  # HTML structure (frontend)
├── style.css                   # CSS styling (frontend)
├── script.js                   # JavaScript for interactions (frontend)
└── README.md                   # This file
```

## Deployment

### GitHub Pages (Frontend)

1. Push your code to a GitHub repository
2. Go to the repository's settings
3. Navigate to "Pages" in the left sidebar
4. Under "Build and deployment", select "Source" as "Deploy from a branch"
5. Choose your main branch and the root directory
6. Click "Save"
7. Your frontend will be deployed at `https://<username>.github.io/<repository-name>/`

### Render (Backend)

1. Create a Render account at https://render.com/
2. Click "New +" > "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name:** chemquest-backend
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment Variables:** Add your `OPENAI_API_KEY`
5. Click "Create Web Service"
6. Your backend will be deployed at `https://<service-name>.onrender.com`

### Connecting Frontend to Backend

1. Update the backend URL in `script.js`:
   - Open `script.js`
   - Replace all instances of `https://chemquest-b8lk.onrender.com` with your Render backend URL

## Technical Details

- **Backend:** Flask (Python) with CORS support
- **API:** OpenAI GPT-4o-mini for question generation
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Data Storage:** CSV file for logging questions

## Notes

- Make sure to keep your OpenAI API key secure
- The backend server must be running for the game to work
- All questions are logged to `trivia_questions.csv` in the project directory
- The game uses a responsive design that works on desktop and mobile devices

## Troubleshooting

- **Backend not starting:** Ensure Python and all dependencies are installed correctly
- **No questions generated:** Check your OpenAI API key is valid and has sufficient credits
- **CORS errors:** The backend already includes CORS support, so this should not occur
- **CSV not generated:** Check if the backend has write permissions in the project directory

## License

MIT
