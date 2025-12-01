# -*- coding: utf-8 -*-
from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

# HTML template for displaying questions
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Would You Rather - Questions Database</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            color: white;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .subtitle {
            text-align: center;
            color: rgba(255,255,255,0.9);
            font-size: 1.2em;
            margin-bottom: 30px;
        }

        .stats {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
            color: white;
            font-size: 1.1em;
        }

        .questions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .question-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .question-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }

        .question-id {
            position: absolute;
            top: 15px;
            right: 15px;
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }

        .category {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-bottom: 15px;
            font-weight: 600;
        }

        .question-text {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            line-height: 1.4;
        }

        .options {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .option {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.2s ease;
        }

        .option:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }

        .option-label {
            font-weight: bold;
            color: #667eea;
            margin-right: 8px;
        }

        .option-text {
            color: #555;
        }

        .vote-stats {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #f0f0f0;
            display: flex;
            justify-content: space-around;
            font-size: 0.9em;
        }

        .vote-count {
            text-align: center;
        }

        .vote-number {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }

        .vote-label {
            color: #888;
            font-size: 0.85em;
        }

        @media (max-width: 768px) {
            .questions-grid {
                grid-template-columns: 1fr;
            }

            h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>> Would You Rather Questions</h1>
        <p class="subtitle">Browse all questions in the database</p>

        <div class="stats">
            =� Total Questions: <strong>{{ total_questions }}</strong> |
            =� Total Votes: <strong>{{ total_votes }}</strong>
        </div>

        <div class="questions-grid">
            {% for q in questions %}
            <div class="question-card">
                <span class="question-id">#{{ q.id }}</span>
                <div class="category">{{ q.category }}</div>
                <div class="question-text">{{ q.question }}</div>
                <div class="options">
                    <div class="option">
                        <span class="option-label">=H Option A:</span>
                        <span class="option-text">{{ q.option_a }}</span>
                    </div>
                    <div class="option">
                        <span class="option-label">=I Option B:</span>
                        <span class="option-text">{{ q.option_b }}</span>
                    </div>
                </div>
                <div class="vote-stats">
                    <div class="vote-count">
                        <div class="vote-number">{{ q.a_votes }}</div>
                        <div class="vote-label">Option A Votes</div>
                    </div>
                    <div class="vote-count">
                        <div class="vote-number">{{ q.b_votes }}</div>
                        <div class="vote-label">Option B Votes</div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect('wyr_bot.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Display all questions from the database"""
    conn = get_db_connection()

    # Get all questions
    questions = conn.execute(
        'SELECT id, question, option_a, option_b, category FROM questions ORDER BY id'
    ).fetchall()

    # Get vote counts for each question
    questions_with_votes = []
    total_votes = 0

    for q in questions:
        # Get vote counts for this question
        votes = conn.execute(
            'SELECT choice, COUNT(*) as count FROM votes WHERE question_id = ? GROUP BY choice',
            (q['id'],)
        ).fetchall()

        a_votes = 0
        b_votes = 0

        for vote in votes:
            if vote['choice'] == 'a':
                a_votes = vote['count']
            elif vote['choice'] == 'b':
                b_votes = vote['count']

        total_votes += a_votes + b_votes

        questions_with_votes.append({
            'id': q['id'],
            'question': q['question'],
            'option_a': q['option_a'],
            'option_b': q['option_b'],
            'category': q['category'],
            'a_votes': a_votes,
            'b_votes': b_votes
        })

    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        questions=questions_with_votes,
        total_questions=len(questions_with_votes),
        total_votes=total_votes
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
