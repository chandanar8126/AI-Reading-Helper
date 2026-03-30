import sqlite3
from datetime import datetime
import hashlib
import os

DATABASE = 'reading_helper.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize all database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            avatar TEXT DEFAULT 'default.png',
            bio TEXT,
            reading_level TEXT DEFAULT 'basic',
            total_texts_simplified INTEGER DEFAULT 0,
            total_reading_time INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            badges TEXT DEFAULT '[]'
        )
    ''')
    
    # Reading History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reading_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original_text TEXT NOT NULL,
            simplified_text TEXT NOT NULL,
            reading_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reading_time INTEGER DEFAULT 0,
            difficulty_score FLOAT,
            words_count INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # User Progress Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date DATE,
            texts_simplified INTEGER DEFAULT 0,
            reading_time INTEGER DEFAULT 0,
            words_read INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Learning Resources Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            type TEXT, -- 'article', 'video', 'exercise'
            url TEXT,
            difficulty TEXT,
            category TEXT,
            thumbnail TEXT,
            duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User Bookmarks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            resource_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES learning_resources(id)
        )
    ''')
    
    # Achievements/Badges Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            requirement TEXT,
            points INTEGER DEFAULT 0
        )
    ''')
    
    # User Achievements Junction Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            achievement_id INTEGER,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (achievement_id) REFERENCES achievements(id)
        )
    ''')
    
    # Daily Motivations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_motivations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            author TEXT,
            category TEXT
        )
    ''')
    
    # Eye Tracking Events Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eye_tracking_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            text_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password, full_name):
    """Create a new user"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        hashed_pw = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_pw, full_name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def verify_user(email, password):
    """Verify user credentials"""
    conn = get_db()
    cursor = conn.cursor()
    
    hashed_pw = hash_password(password)
    cursor.execute('''
        SELECT * FROM users WHERE email = ? AND password = ?
    ''', (email, hashed_pw))
    
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_last_login(user_id):
    """Update user's last login time"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET last_login = ? WHERE id = ?
    ''', (datetime.now(), user_id))
    conn.commit()
    conn.close()

def add_reading_history(user_id, original_text, simplified_text, reading_level, words_count):
    """Add reading history entry"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO reading_history 
        (user_id, original_text, simplified_text, reading_level, words_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, original_text, simplified_text, reading_level, words_count))
    
    # Update user stats
    cursor.execute('''
        UPDATE users 
        SET total_texts_simplified = total_texts_simplified + 1,
            points = points + 10
        WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    history_id = cursor.lastrowid
    conn.close()
    return history_id

def get_user_history(user_id, limit=10):
    """Get user's reading history"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM reading_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    history = cursor.fetchall()
    conn.close()
    return [dict(row) for row in history]

def seed_motivations():
    """Seed database with motivational quotes"""
    conn = get_db()
    cursor = conn.cursor()
    
    motivations = [
        ("Reading is to the mind what exercise is to the body.", "Joseph Addison", "reading"),
        ("The more that you read, the more things you will know.", "Dr. Seuss", "learning"),
        ("A reader lives a thousand lives before he dies.", "George R.R. Martin", "inspiration"),
        ("Today a reader, tomorrow a leader.", "Margaret Fuller", "motivation"),
        ("Reading is a conversation. All books talk. But a good book listens as well.", "Mark Haddon", "wisdom"),
        ("Books are a uniquely portable magic.", "Stephen King", "inspiration"),
        ("I have always imagined that Paradise will be a kind of library.", "Jorge Luis Borges", "reading"),
        ("There is no friend as loyal as a book.", "Ernest Hemingway", "friendship"),
        ("Reading is essential for those who seek to rise above the ordinary.", "Jim Rohn", "motivation"),
        ("The reading of all good books is like a conversation with the finest minds of past centuries.", "Rene Descartes", "wisdom")
    ]
    
    for quote, author, category in motivations:
        cursor.execute('''
            INSERT OR IGNORE INTO daily_motivations (quote, author, category)
            VALUES (?, ?, ?)
        ''', (quote, author, category))
    
    conn.commit()
    conn.close()
    print("✅ Motivational quotes seeded!")

def seed_achievements():
    """Seed achievements/badges"""
    conn = get_db()
    cursor = conn.cursor()
    
    achievements = [
        ("First Steps", "Simplify your first text", "🌟", "first_text", 10),
        ("Reading Streak", "Read 7 days in a row", "🔥", "7_day_streak", 50),
        ("Word Master", "Read 10,000 words", "📚", "10k_words", 100),
        ("Speed Reader", "Complete 50 texts", "⚡", "50_texts", 200),
        ("Knowledge Seeker", "Read 100 texts", "🎓", "100_texts", 500),
        ("Night Owl", "Read after midnight", "🦉", "night_reading", 25),
        ("Early Bird", "Read before 6 AM", "🌅", "morning_reading", 25),
        ("Perfectionist", "Complete all difficulty levels", "💎", "all_levels", 150)
    ]
    
    for name, desc, icon, req, points in achievements:
        cursor.execute('''
            INSERT OR IGNORE INTO achievements (name, description, icon, requirement, points)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, desc, icon, req, points))
    
    conn.commit()
    conn.close()
    print("✅ Achievements seeded!")

def get_random_motivation():
    """Get a random motivational quote"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM daily_motivations ORDER BY RANDOM() LIMIT 1')
    quote = cursor.fetchone()
    conn.close()
    return dict(quote) if quote else None

# Initialize database on import
if __name__ == "__main__":
    init_db()
    seed_motivations()
    seed_achievements()
    print("🎉 Database setup complete!")