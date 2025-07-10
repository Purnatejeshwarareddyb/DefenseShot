"""
DefenseShot: Elite Sniper Academy
Database management module - SQLite operations
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime
from config import DB_PATH, TOTAL_MODULES, SESSION_FILE

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    # PDFs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_number INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module_number INTEGER,
            is_unlocked BOOLEAN DEFAULT FALSE,
            is_completed BOOLEAN DEFAULT FALSE,
            completion_date TIMESTAMP,
            study_time INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, module_number)
        )
    ''')

    # Quiz results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module_number INTEGER,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            time_taken INTEGER,
            attempt_number INTEGER,
            quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Initialize PDF records
    for i in range(1, TOTAL_MODULES + 1):
        cursor.execute('''
            INSERT OR IGNORE INTO pdfs (module_number, title, file_path)
            VALUES (?, ?, ?)
        ''', (i, f"Module {i}: Advanced Topic", f"study_materials/module_{i}.pdf"))

    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email=None):
    """Register a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        password_hash = hash_password(password)

        cursor.execute('''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        ''', (username, password_hash, email))

        user_id = cursor.lastrowid

        # Initialize progress for all modules (only module 1 unlocked)
        for i in range(1, TOTAL_MODULES + 1):
            is_unlocked = (i == 1)  # Only first module unlocked
            cursor.execute('''
                INSERT INTO progress (user_id, module_number, is_unlocked)
                VALUES (?, ?, ?)
            ''', (user_id, i, is_unlocked))

        conn.commit()
        conn.close()
        return True, "Registration successful"

    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def verify_login(username, password):
    """Verify user login credentials"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        password_hash = hash_password(password)

        cursor.execute('''
            SELECT id, username, email FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))

        user = cursor.fetchone()

        if user:
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user['id'],))
            conn.commit()

            # Save session
            save_session(dict(user))

            conn.close()
            return True, dict(user)
        else:
            conn.close()
            return False, "Invalid username or password"

    except Exception as e:
        return False, f"Login failed: {str(e)}"

def get_unlocked_modules(user_id):
    """Get list of unlocked modules for user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT module_number, is_unlocked, is_completed
            FROM progress
            WHERE user_id = ? AND is_unlocked = 1
            ORDER BY module_number
        ''', (user_id,))

        modules = cursor.fetchall()
        conn.close()

        return [dict(module) for module in modules]

    except Exception as e:
        print(f"Error getting unlocked modules: {e}")
        return []

def update_progress(user_id, module_number, study_time):
    """Update study progress for a module"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE progress 
            SET study_time = study_time + ?
            WHERE user_id = ? AND module_number = ?
        ''', (study_time, user_id, module_number))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error updating progress: {e}")
        return False

def save_quiz_result(user_id, module_number, score, total_questions, time_taken):
    """Save quiz result and unlock next module if passed"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current attempt number
        cursor.execute('''
            SELECT COUNT(*) as attempts FROM quiz_results
            WHERE user_id = ? AND module_number = ?
        ''', (user_id, module_number))

        attempts = cursor.fetchone()['attempts'] + 1

        # Save quiz result
        cursor.execute('''
            INSERT INTO quiz_results 
            (user_id, module_number, score, total_questions, time_taken, attempt_number)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, module_number, score, total_questions, time_taken, attempts))

        # Update progress attempts
        cursor.execute('''
            UPDATE progress 
            SET attempts = ?
            WHERE user_id = ? AND module_number = ?
        ''', (attempts, user_id, module_number))

        # Check if passed and unlock next module
        if score >= 8:  # Passing score
            # Mark current module as completed
            cursor.execute('''
                UPDATE progress 
                SET is_completed = 1, completion_date = CURRENT_TIMESTAMP
                WHERE user_id = ? AND module_number = ?
            ''', (user_id, module_number))

            # Unlock next module if exists
            if module_number < TOTAL_MODULES:
                cursor.execute('''
                    UPDATE progress 
                    SET is_unlocked = 1
                    WHERE user_id = ? AND module_number = ?
                ''', (user_id, module_number + 1))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error saving quiz result: {e}")
        return False

def get_user_stats(user_id):
    """Get user statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get completed modules count
        cursor.execute('''
            SELECT COUNT(*) as completed FROM progress
            WHERE user_id = ? AND is_completed = 1
        ''', (user_id,))
        completed = cursor.fetchone()['completed']

        # Get average score
        cursor.execute('''
            SELECT AVG(score) as avg_score FROM quiz_results
            WHERE user_id = ?
        ''', (user_id,))
        avg_score = cursor.fetchone()['avg_score'] or 0

        # Get total study time
        cursor.execute('''
            SELECT SUM(study_time) as total_time FROM progress
            WHERE user_id = ?
        ''', (user_id,))
        total_time = cursor.fetchone()['total_time'] or 0

        conn.close()

        return {
            'completed_modules': completed,
            'total_modules': TOTAL_MODULES,
            'average_score': round(avg_score, 2),
            'total_study_time': total_time
        }

    except Exception as e:
        print(f"Error getting user stats: {e}")
        return None

def save_session(user_data):
    """Save user session to file"""
    try:
        session_data = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'email': user_data.get('email', ''),
            'login_time': datetime.now().isoformat()
        }

        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error saving session: {e}")
        return False

def load_session():
    """Load user session from file"""
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

def clear_session():
    """Clear user session"""
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return True
    except Exception as e:
        print(f"Error clearing session: {e}")
        return False