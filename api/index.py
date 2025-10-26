import os
import json
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timedelta
import random

app = Flask(__name__, template_folder='../templates')
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

def check_database_initialized():
    """Check if database has been initialized with data"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM topics")
        count = cur.fetchone()[0]
        return count > 0
    except:
        return False
    finally:
        conn.close()

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
        
        # Get the path to seed files
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        seeds_path = os.path.join(base_path, 'data', 'seeds')
        
        # Load topics from JSON
        topics_file = os.path.join(seeds_path, 'topics.json')
        with open(topics_file, 'r') as f:
            topics_data = json.load(f)
        
        for topic in topics_data:
            cur.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic["name"],))
        
        conn.commit()
        
        # Load MCQ data from JSON
        mcq_file = os.path.join(seeds_path, 'mcq.json')
        with open(mcq_file, 'r') as f:
            mcq_data = json.load(f)
        
        for mcq in mcq_data:
            cur.execute("SELECT id FROM topics WHERE name = ?", (mcq["topic_name"],))
            result = cur.fetchone()
            if result:
                topic_id = result[0]
                
                cur.execute("""
                    INSERT INTO mcq (stem, choices_json, answer_idx, explanation, topic_id, source_ref)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    mcq["stem"],
                    json.dumps(mcq["choices"]),
                    mcq["answer_idx"],
                    mcq["explanation"],
                    topic_id,
                    mcq.get("source_ref", "")
                ))
        
        # Load SAQ data from JSON
        saq_file = os.path.join(seeds_path, 'saq.json')
        with open(saq_file, 'r') as f:
            saq_data = json.load(f)
        
        for saq in saq_data:
            cur.execute("SELECT id FROM topics WHERE name = ?", (saq["topic_name"],))
            result = cur.fetchone()
            if result:
                topic_id = result[0]
                
                cur.execute("""
                    INSERT INTO saq (prompt, model_outline, keywords_json, statute_refs_json, topic_id, source_ref)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    saq["prompt"],
                    saq["model_outline"],
                    json.dumps(saq["keywords_json"]),
                    json.dumps(saq["statute_refs_json"]),
                    topic_id,
                    saq.get("source_ref", "")
                ))
        
        # Load flashcards from JSON
        flashcards_file = os.path.join(seeds_path, 'flashcards.json')
        with open(flashcards_file, 'r') as f:
            flashcards_data = json.load(f)
        
        for card in flashcards_data:
            cur.execute("SELECT id FROM topics WHERE name = ?", (card["topic_name"],))
            result = cur.fetchone()
            if result:
                topic_id = result[0]
                
                cur.execute("""
                    INSERT INTO flashcards (front, back, topic_id, source_ref)
                    VALUES (?, ?, ?, ?)
                """, (
                    card["front"],
                    card["back"],
                    topic_id,
                    card.get("source_ref", "")
                ))
        
        conn.commit()
        print(f"Successfully loaded seed data: {len(topics_data)} topics, {len(mcq_data)} MCQs, {len(saq_data)} SAQs, {len(flashcards_data)} flashcards")
        
    except Exception as e:
        print(f"Error loading seed data: {e}")
        import traceback
        traceback.print_exc()

# Routes
@app.route('/test')
def test():
    """Simple test route to check if the app is working"""
    try:
        conn = get_db_connection()
        if not conn:
            return "Database connection failed", 500
        
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM topics")
        count = cur.fetchone()[0]
        conn.close()
        
        return f"App is working! Database has {count} topics."
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/')
def index():
    """Home dashboard with stats and weak topics"""
    user_id = session.get('user_id', 'local-user')
    
    # Ensure database is initialized
    if not check_database_initialized():
        init_database()
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor()
        
        # Get overall stats
        cur.execute("SELECT COUNT(*) FROM mcq")
        total_mcqs = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM saq")
        total_saqs = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM flashcards")
        total_flashcards = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM topics")
        total_topics = cur.fetchone()[0]
        
        # Get user progress - MCQ specific
        cur.execute("""
            SELECT COUNT(DISTINCT item_id) 
            FROM progress 
            WHERE user_id = ? AND item_type = 'mcq'
        """, (user_id,))
        mcq_completed = cur.fetchone()[0]
        
        cur.execute("""
            SELECT 
                SUM(correct_count) as correct,
                SUM(wrong_count) as wrong
            FROM progress 
            WHERE user_id = ? AND item_type = 'mcq'
        """, (user_id,))
        result = cur.fetchone()
        mcq_correct = result[0] or 0
        mcq_wrong = result[1] or 0
        mcq_attempts = mcq_correct + mcq_wrong
        mcq_accuracy = mcq_correct / mcq_attempts if mcq_attempts > 0 else 0
        
        # Get user progress - SAQ specific
        cur.execute("""
            SELECT COUNT(DISTINCT item_id) 
            FROM progress 
            WHERE user_id = ? AND item_type = 'saq'
        """, (user_id,))
        saq_completed = cur.fetchone()[0]
        
        cur.execute("""
            SELECT 
                SUM(correct_count) as correct,
                SUM(wrong_count) as wrong
            FROM progress 
            WHERE user_id = ? AND item_type = 'saq'
        """, (user_id,))
        result = cur.fetchone()
        saq_correct = result[0] or 0
        saq_wrong = result[1] or 0
        saq_attempts = saq_correct + saq_wrong
        saq_accuracy = saq_correct / saq_attempts if saq_attempts > 0 else 0
        
        # Combined stats
        total_correct = mcq_correct + saq_correct
        total_attempts = mcq_attempts + saq_attempts
        overall_accuracy = total_correct / total_attempts if total_attempts > 0 else 0
        
        cur.execute("""
            SELECT COUNT(DISTINCT t.id)
            FROM topics t
            JOIN mcq m ON t.id = m.topic_id
            JOIN progress p ON m.id = p.item_id AND p.item_type = 'mcq'
            WHERE p.user_id = ?
        """, (user_id,))
        topics_practiced = cur.fetchone()[0]
        
        stats = {
            'total_mcqs': total_mcqs,
            'total_saqs': total_saqs,
            'total_flashcards': total_flashcards,
            'total_topics': total_topics,
            'mcq_completed': mcq_completed,
            'mcq_correct': mcq_correct,
            'mcq_attempts': mcq_attempts,
            'mcq_accuracy': mcq_accuracy,
            'saq_completed': saq_completed,
            'saq_correct': saq_correct,
            'saq_attempts': saq_attempts,
            'saq_accuracy': saq_accuracy,
            'correct': total_correct,
            'total': total_attempts,
            'accuracy': overall_accuracy,
            'topics_practiced': topics_practiced
        }
        
        # Get topic-level progress
        cur.execute("""
            SELECT 
                t.name,
                SUM(p.correct_count) as correct,
                SUM(p.wrong_count) as wrong,
                SUM(p.correct_count + p.wrong_count) as attempts
            FROM topics t
            JOIN mcq m ON t.id = m.topic_id
            JOIN progress p ON m.id = p.item_id AND p.item_type = 'mcq' AND p.user_id = ?
            GROUP BY t.id, t.name
            HAVING attempts > 0
            ORDER BY CAST(correct AS FLOAT) / (correct + wrong) ASC
        """, (user_id,))
        
        topic_progress = []
        weak_topics = []
        
        for row in cur.fetchall():
            topic_data = {
                'name': row[0],
                'correct': row[1],
                'wrong': row[2],
                'total': row[3],
                'attempts': row[3],
                'accuracy': row[1] / row[3] if row[3] > 0 else 0
            }
            topic_progress.append(topic_data)
            
            # Topics with < 70% accuracy are weak
            if topic_data['accuracy'] < 0.7:
                weak_topics.append(topic_data)
        
        return render_template('index.html', 
                             stats=stats, 
                             topic_progress=topic_progress,
                             weak_topics=weak_topics)
        
    except Exception as e:
        import traceback
        print(f"Error in index: {e}")
        print(traceback.format_exc())
        return f"Error loading dashboard: {str(e)}", 500
    finally:
        conn.close()

@app.route('/drill/mcq')
def drill_mcq():
    """Start MCQ drill with improved variety and spaced repetition"""
    user_id = session.get('user_id', 'local-user')
    
    # Ensure database is initialized
    if not check_database_initialized():
        init_database()
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor()
        
        # Improved question selection algorithm:
        # 1. Prioritize questions with low accuracy (< 70%)
        # 2. Include questions from different topics for variety
        # 3. Mix in some new/unseen questions
        # 4. Use spaced repetition - questions answered correctly less recently
        
        # Get weak questions (accuracy < 70%, attempted at least once)
        cur.execute("""
            SELECT m.*, t.name as topic_name, p.correct_count, p.wrong_count,
                   CAST(p.correct_count AS FLOAT) / (p.correct_count + p.wrong_count) as accuracy
            FROM mcq m
            JOIN topics t ON m.topic_id = t.id
            LEFT JOIN progress p ON m.id = p.item_id AND p.item_type = 'mcq' AND p.user_id = ?
            WHERE p.correct_count + p.wrong_count > 0 
            AND CAST(p.correct_count AS FLOAT) / (p.correct_count + p.wrong_count) < 0.7
            ORDER BY accuracy ASC, RANDOM()
            LIMIT 4
        """, (user_id,))
        weak_questions = [dict(row) for row in cur.fetchall()]
        
        # Get questions from different topics for variety
        cur.execute("""
            SELECT m.*, t.name as topic_name
            FROM mcq m
            JOIN topics t ON m.topic_id = t.id
            LEFT JOIN progress p ON m.id = p.item_id AND p.item_type = 'mcq' AND p.user_id = ?
            WHERE m.id NOT IN (SELECT id FROM (
                SELECT m2.id FROM mcq m2
                LEFT JOIN progress p2 ON m2.id = p2.item_id AND p2.item_type = 'mcq' AND p2.user_id = ?
                WHERE p2.correct_count + p2.wrong_count > 0 
                AND CAST(p2.correct_count AS FLOAT) / (p2.correct_count + p2.wrong_count) < 0.7
            ))
            GROUP BY t.id
            ORDER BY RANDOM()
            LIMIT 3
        """, (user_id, user_id))
        variety_questions = [dict(row) for row in cur.fetchall()]
        
        # Get new/unseen questions
        cur.execute("""
            SELECT m.*, t.name as topic_name
            FROM mcq m
            JOIN topics t ON m.topic_id = t.id
            LEFT JOIN progress p ON m.id = p.item_id AND p.item_type = 'mcq' AND p.user_id = ?
            WHERE p.item_id IS NULL
            ORDER BY RANDOM()
            LIMIT 3
        """, (user_id,))
        new_questions = [dict(row) for row in cur.fetchall()]
        
        # Combine and shuffle
        all_questions = weak_questions + variety_questions + new_questions
        random.shuffle(all_questions)
        
        # Take only 10 questions
        questions = all_questions[:10]
        
        # If we don't have 10 questions, fill with random ones
        if len(questions) < 10:
            cur.execute("""
                SELECT m.*, t.name as topic_name
                FROM mcq m
                JOIN topics t ON m.topic_id = t.id
                ORDER BY RANDOM()
                LIMIT ?
            """, (10 - len(questions),))
            additional = [dict(row) for row in cur.fetchall()]
            questions.extend(additional)
        
        # Convert choices_json to list
        for q in questions:
            q['choices'] = json.loads(q['choices_json'])
        
        return render_template('drill_mcq.html', questions=questions)
        
    except Exception as e:
        print(f"Error in drill_mcq: {e}")
        import traceback
        traceback.print_exc()
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
    # Ensure database is initialized
    if not check_database_initialized():
        init_database()
    
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
        
        row = cur.fetchone()
        saq = None
        if row:
            saq = dict(row)
            saq['keywords'] = json.loads(saq['keywords_json'])
            saq['statute_refs'] = json.loads(saq['statute_refs_json'])
        
        return render_template('practice_saq.html', saq=saq)
        
    except Exception as e:
        print(f"Error in practice_saq: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Ensure database is initialized
    if not check_database_initialized():
        init_database()
    
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
    
    # Ensure database is initialized
    if not check_database_initialized():
        init_database()
    
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
            LEFT JOIN mcq m ON p.item_type = 'mcq' AND m.id = p.item_id
            LEFT JOIN saq s ON p.item_type = 'saq' AND s.id = p.item_id
            LEFT JOIN topics t ON (m.topic_id = t.id OR s.topic_id = t.id)
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
