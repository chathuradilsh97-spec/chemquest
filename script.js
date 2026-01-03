// DOM Elements
const generateBtn = document.getElementById('generate-btn');
const questionContainer = document.getElementById('question-container');
const questionEl = document.getElementById('question');
const optionBtns = document.querySelectorAll('.option-btn');
const resultEl = document.getElementById('result');

// Stats Elements
const totalQuestionsEl = document.getElementById('total-questions');
const correctAnswersEl = document.getElementById('correct-answers');
const wrongAnswersEl = document.getElementById('wrong-answers');
const accuracyEl = document.getElementById('accuracy');

let currentQuestion = null;
let currentCorrectAnswer = null;

// Event Listeners
generateBtn.addEventListener('click', generateQuestion);
optionBtns.forEach(btn => {
    btn.addEventListener('click', handleOptionClick);
});

// Fetch stats when the page loads
window.addEventListener('DOMContentLoaded', fetchStats);

// Generate a new trivia question
async function generateQuestion() {
    try {
        // Show loading state
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        resultEl.className = 'result';
        resultEl.style.display = 'none';
        
        // Make API request
        const response = await fetch('https://chemquest-b8lk.onrender.com/generate-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentQuestion = data.question;
            const options = data.options;
            currentCorrectAnswer = data.correct_answer;
            
            // Display question and options
            displayQuestion(currentQuestion, options);
        } else {
            showResult('Error generating question: ' + data.error, false);
        }
    } catch (error) {
        console.error('Error:', error);
        showResult('Failed to connect to server. Make sure the backend is running.', false);
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Question';
    }
}

// Display the question and options
function displayQuestion(question, options) {
    // Update question text
    questionEl.textContent = question;
    
    // Update option buttons
    optionBtns.forEach((btn, index) => {
        btn.textContent = options[index];
        btn.className = 'option-btn';
        btn.disabled = false;
    });
    
    // Show question container
    questionContainer.classList.add('active');
    resultEl.className = 'result';
    resultEl.style.display = 'none';
}

// Handle option button click
async function handleOptionClick(e) {
    const selectedBtn = e.target;
    const selectedOption = selectedBtn.textContent;
    
    // Disable all option buttons
    optionBtns.forEach(btn => {
        btn.disabled = true;
    });
    
    // Check if the answer is correct
    const isCorrect = selectedOption === currentCorrectAnswer;
    
    // Update button styles
    selectedBtn.classList.add(isCorrect ? 'correct' : 'wrong');
    
    // Mark the correct answer
    optionBtns.forEach(btn => {
        if (btn.textContent === currentCorrectAnswer) {
            btn.classList.add('correct');
        } else if (btn !== selectedBtn && !isCorrect) {
            btn.classList.add('wrong');
        }
    });
    
    // Show result
    showResult(isCorrect ? 'Correct! Well done!' : `Wrong! The correct answer is: ${currentCorrectAnswer}`, isCorrect);
    
    // Update stats
    await updateStats(isCorrect);
}

// Fetch stats from the backend
async function fetchStats() {
    try {
        const response = await fetch('https://chemquest-b8lk.onrender.com/stats', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayStats(data.stats);
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Update stats in the backend
async function updateStats(isCorrect) {
    try {
        const response = await fetch('https://chemquest-b8lk.onrender.com/update-stats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_correct: isCorrect
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayStats(data.stats);
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Display stats on the page
function displayStats(stats) {
    totalQuestionsEl.textContent = stats.total_questions;
    correctAnswersEl.textContent = stats.correct_answers;
    wrongAnswersEl.textContent = stats.wrong_answers;
    
    // Calculate accuracy
    const accuracy = stats.total_questions > 0 
        ? Math.round((stats.correct_answers / stats.total_questions) * 100)
        : 0;
    accuracyEl.textContent = `${accuracy}%`;
}

// Show the result message
function showResult(message, isCorrect) {
    resultEl.textContent = message;
    resultEl.className = `result active ${isCorrect ? 'correct' : 'wrong'}`;
    resultEl.style.display = 'block';
}

// Check answer with backend (optional, but implemented as per requirements)
async function checkAnswerWithBackend(userAnswer, correctAnswer) {
    try {
        const response = await fetch('https://chemquest-b8lk.onrender.com/check-answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_answer: userAnswer,
                correct_answer: correctAnswer
            })
        });
        
        const data = await response.json();
        return data.is_correct;
    } catch (error) {
        console.error('Error checking answer:', error);
        // Fallback to local check if backend is unavailable
        return userAnswer === correctAnswer;
    }
}
