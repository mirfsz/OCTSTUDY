import os
import json
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database connection
def get_db_connection():
    """Get database connection using SQLite"""
    try:
        # Use /tmp directory for Vercel serverless environment
        db_path = os.path.join('/tmp', 'study_coach.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database tables and seed data"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mcq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stem TEXT NOT NULL,
                choices_json TEXT NOT NULL,
                answer_idx INTEGER NOT NULL,
                explanation TEXT,
                topic_id INTEGER NOT NULL REFERENCES topics(id),
                source_ref TEXT
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS saq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                model_outline TEXT NOT NULL,
                keywords_json TEXT NOT NULL,
                statute_refs_json TEXT,
                topic_id INTEGER NOT NULL REFERENCES topics(id),
                source_ref TEXT
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                topic_id INTEGER NOT NULL REFERENCES topics(id),
                source_ref TEXT
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                item_type TEXT CHECK(item_type IN ('mcq','saq')),
                item_id INTEGER NOT NULL,
                correct_count INTEGER DEFAULT 0,
                wrong_count INTEGER DEFAULT 0,
                box INTEGER DEFAULT 1,
                last_seen_at TIMESTAMP,
                UNIQUE(user_id, item_type, item_id)
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                mode TEXT,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                score_json TEXT
            );
        """)
        
        conn.commit()
        
        # Load seed data
        load_seed_data(conn)
        
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        conn.close()

def load_seed_data(conn):
    """Load seed data from JSON files"""
    try:
        cur = conn.cursor()
        
        # Check if data already exists
        cur.execute("SELECT COUNT(*) FROM topics")
        if cur.fetchone()[0] > 0:
            return  # Data already loaded
        
        # Load topics
        topics_data = [
            {"name": "BWC"},
            {"name": "NWD"},
            {"name": "Scams"},
            {"name": "AOS"},
            {"name": "Roadblock"},
            {"name": "PHA"},
            {"name": "AOJ"},
            {"name": "SALUTE"},
            {"name": "Exhibits"},
            {"name": "Traffic"}
        ]
        
        for topic in topics_data:
            cur.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic["name"],))
        
        conn.commit()
        
        # Load sample MCQ data
        sample_mcqs = [
            {
                "stem": "When should a BWC be activated?",
                "choices": ["Only during arrests", "At the start of every police interaction", "Only when force is used", "When directed by supervisor"],
                "answer_idx": 1,
                "explanation": "BWC should be activated at the start of every police interaction to ensure complete documentation.",
                "topic_name": "BWC",
                "source_ref": "BWC Manual"
            },
            {
                "stem": "What is the primary purpose of SALUTE reporting?",
                "choices": ["Document arrests", "Report armed incidents", "Track traffic violations", "Record witness statements"],
                "answer_idx": 1,
                "explanation": "SALUTE is specifically for reporting armed incidents and threats.",
                "topic_name": "SALUTE",
                "source_ref": "SALUTE Guidelines"
            }
        ]
        
        for mcq in sample_mcqs:
            cur.execute("SELECT id FROM topics WHERE name = ?", (mcq["topic_name"],))
            topic_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO mcq (stem, choices_json, answer_idx, explanation, topic_id, source_ref)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                mcq["stem"],
                json.dumps(mcq["choices"]),
                mcq["answer_idx"],
                mcq["explanation"],
                topic_id,
                mcq["source_ref"]
            ))
        
        # Load sample SAQ data
        sample_saqs = [
            {
                "prompt": "Officer Tan responds to a complaint about a neighbor who has been throwing red paint at the complainant's gate every night. The neighbor admits to the act but claims it's just a prank. Analyze this scenario.",
                "model_outline": "1. Define: Criminal Mischief (S427 PC)\n2. Elements: Property damage, intentional act\n3. Apply: Red paint on gate = property damage, repeated acts show intent\n4. Conclusion: Arrestable offence under S427",
                "keywords_json": json.dumps(["property damage", "intentional", "criminal mischief", "S427"]),
                "statute_refs_json": json.dumps(["S427 Penal Code"]),
                "topic_name": "Scams",
                "source_ref": "Criminal Law Manual"
            }
        ]
        
        for saq in sample_saqs:
            cur.execute("SELECT id FROM topics WHERE name = ?", (saq["topic_name"],))
            topic_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO saq (prompt, model_outline, keywords_json, statute_refs_json, topic_id, source_ref)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                saq["prompt"],
                saq["model_outline"],
                saq["keywords_json"],
                saq["statute_refs_json"],
                topic_id,
                saq["source_ref"]
            ))
        
        # Load sample flashcards
        sample_flashcards = [
            {
                "front": "BWC 10 Exceptions",
                "back": "1. Personal hygiene 2. Medical emergencies 3. Undercover operations 4. Victim interviews 5. Witness protection 6. Family disputes 7. Mental health calls 8. Juvenile interviews 9. Sexual offences 10. National security",
                "topic_name": "BWC",
                "source_ref": "BWC Manual"
            },
            {
                "front": "SALUTE Format",
                "back": "S - Size, A - Activity, L - Location, U - Unit, T - Time, E - Equipment",
                "topic_name": "SALUTE",
                "source_ref": "SALUTE Guidelines"
            }
        ]
        
        for card in sample_flashcards:
            cur.execute("SELECT id FROM topics WHERE name = ?", (card["topic_name"],))
            topic_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO flashcards (front, back, topic_id, source_ref)
                VALUES (?, ?, ?, ?)
            """, (
                card["front"],
                card["back"],
                topic_id,
                card["source_ref"]
            ))
        
        conn.commit()
        
    except Exception as e:
        print(f"Error loading seed data: {e}")

# Routes
@app.route('/')
def index():
    """Home dashboard with weak topics"""
    user_id = session.get('user_id', 'local-user')
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor()
        
        # Get weak topics (topics with < 80% accuracy)
        cur.execute("""
            SELECT t.name, 
                   COALESCE(AVG(CASE WHEN p.correct_count + p.wrong_count > 0 
                               THEN CAST(p.correct_count AS FLOAT) / (p.correct_count + p.wrong_count) 
                               ELSE 0 END), 0) as accuracy
            FROM topics t
            LEFT JOIN progress p ON t.id = p.topic_id AND p.user_id = ?
            GROUP BY t.id, t.name
            HAVING COALESCE(AVG(CASE WHEN p.correct_count + p.wrong_count > 0 
                           THEN CAST(p.correct_count AS FLOAT) / (p.correct_count + p.wrong_count) 
                           ELSE 0 END), 0) < 0.8
            ORDER BY accuracy ASC
        """, (user_id,))
        
        weak_topics = [dict(row) for row in cur.fetchall()]
        
        return render_template('index.html', weak_topics=weak_topics)
        
    except Exception as e:
        print(f"Error in index: {e}")
        return "Error loading dashboard", 500
    finally:
        conn.close()

@app.route('/drill/mcq')
def drill_mcq():
    """Start MCQ drill"""
    user_id = session.get('user_id', 'local-user')
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor()
        
        # Get questions (60% weak topics, 40% random)
        cur.execute("""
            SELECT m.*, t.name as topic_name
            FROM mcq m
            JOIN topics t ON m.topic_id = t.id
            LEFT JOIN progress p ON m.id = p.item_id AND p.item_type = 'mcq' AND p.user_id = ?
            WHERE p.correct_count + p.wrong_count < 5 OR p.correct_count + p.wrong_count IS NULL
            ORDER BY RANDOM()
            LIMIT 10
        """, (user_id,))
        
        questions = [dict(row) for row in cur.fetchall()]
        
        # Convert choices_json to list
        for q in questions:
            q['choices'] = json.loads(q['choices_json'])
        
        return render_template('drill_mcq.html', questions=questions)
        
    except Exception as e:
        print(f"Error in drill_mcq: {e}")
        return "Error loading MCQ drill", 500
    finally:
        conn.close()

@app.route('/drill/mcq/answer', methods=['POST'])
def submit_mcq_answer():
    """Submit MCQ answer and update progress"""
    user_id = session.get('user_id', 'local-user')
    data = request.get_json()
    
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        
        # Get correct answer
        cur.execute("SELECT answer_idx FROM mcq WHERE id = ?", (question_id,))
        correct_answer = cur.fetchone()[0]
        
        is_correct = selected_answer == correct_answer
        
        # Update progress
        cur.execute("""
            INSERT INTO progress (user_id, item_type, item_id, correct_count, wrong_count, box, last_seen_at)
            VALUES (?, 'mcq', ?, ?, ?, 1, datetime('now'))
            ON CONFLICT (user_id, item_type, item_id)
            DO UPDATE SET
                correct_count = progress.correct_count + ?,
                wrong_count = progress.wrong_count + ?,
                box = CASE 
                    WHEN ? THEN MIN(progress.box + 1, 5)
                    ELSE MAX(progress.box - 1, 1)
                END,
                last_seen_at = datetime('now')
        """, (user_id, question_id, 
              1 if is_correct else 0, 0 if is_correct else 1,
              1 if is_correct else 0, 0 if is_correct else 1,
              is_correct))
        
        conn.commit()
        
        return jsonify({
            "correct": is_correct,
            "correct_answer": correct_answer
        })
        
    except Exception as e:
        print(f"Error in submit_mcq_answer: {e}")
        return jsonify({"error": "Error processing answer"}), 500
    finally:
        conn.close()

@app.route('/practice/saq')
def practice_saq():
    """Get random SAQ scenario"""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT s.*, t.name as topic_name
            FROM saq s
            JOIN topics t ON s.topic_id = t.id
            ORDER BY RANDOM()
            LIMIT 1
        """)
        
        saq = cur.fetchone()
        if saq:
            saq['keywords'] = json.loads(saq['keywords_json'])
            saq['statute_refs'] = json.loads(saq['statute_refs_json'])
        
        return render_template('practice_saq.html', saq=saq)
        
    except Exception as e:
        print(f"Error in practice_saq: {e}")
        return "Error loading SAQ practice", 500
    finally:
        conn.close()

@app.route('/practice/saq/grade', methods=['POST'])
def grade_saq():
    """Grade SAQ using keyword matching"""
    data = request.get_json()
    user_answer = data.get('answer', '').lower()
    keywords = data.get('keywords', [])
    
    # Simple keyword matching
    matched_keywords = [kw for kw in keywords if kw.lower() in user_answer]
    score = len(matched_keywords) / len(keywords) if keywords else 0
    
    return jsonify({
        "score": score,
        "matched_keywords": matched_keywords,
        "feedback": f"Matched {len(matched_keywords)}/{len(keywords)} keywords"
    })

@app.route('/cheats')
def cheats():
    """Flashcards by topic"""
    topic = request.args.get('topic', 'all')
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor()
        
        if topic == 'all':
            cur.execute("""
                SELECT f.*, t.name as topic_name
                FROM flashcards f
                JOIN topics t ON f.topic_id = t.id
                ORDER BY t.name, f.id
            """)
        else:
            cur.execute("""
                SELECT f.*, t.name as topic_name
                FROM flashcards f
                JOIN topics t ON f.topic_id = t.id
                WHERE t.name = ?
                ORDER BY f.id
            """, (topic,))
        
        flashcards = [dict(row) for row in cur.fetchall()]
        
        # Get all topics for filter
        cur.execute("SELECT name FROM topics ORDER BY name")
        topics = [row['name'] for row in cur.fetchall()]
        
        return render_template('cheats.html', flashcards=flashcards, topics=topics, current_topic=topic)
        
    except Exception as e:
        print(f"Error in cheats: {e}")
        return "Error loading flashcards", 500
    finally:
        conn.close()

@app.route('/review')
def review():
    """Review mistakes and weak areas"""
    user_id = session.get('user_id', 'local-user')
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor()
        
        # Get items with low accuracy
        cur.execute("""
            SELECT p.*, t.name as topic_name,
                   CASE WHEN p.item_type = 'mcq' THEN m.stem ELSE s.prompt END as content
            FROM progress p
            JOIN topics t ON p.topic_id = t.id
            LEFT JOIN mcq m ON p.item_type = 'mcq' AND m.id = p.item_id
            LEFT JOIN saq s ON p.item_type = 'saq' AND s.id = p.item_id
            WHERE p.user_id = ? 
            AND p.correct_count + p.wrong_count > 0
            AND CAST(p.correct_count AS FLOAT) / (p.correct_count + p.wrong_count) < 0.8
            ORDER BY CAST(p.correct_count AS FLOAT) / (p.correct_count + p.wrong_count) ASC
        """, (user_id,))
        
        weak_items = [dict(row) for row in cur.fetchall()]
        
        return render_template('review.html', weak_items=weak_items)
        
    except Exception as e:
        print(f"Error in review: {e}")
        return "Error loading review", 500
    finally:
        conn.close()

# Initialize database on startup
if __name__ == '__main__':
    init_database()
    app.run(debug=True)
else:
    # For Vercel deployment
    init_database()
