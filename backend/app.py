from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime, timedelta
import os, uuid
from PIL import Image
from functools import wraps

# Import all our modules
from ocr_module import extract_text
from simplify_module import simplify_text, get_text_statistics
from tts_module import generate_tts
from eyetracking_module import log_difficulty_event
from database import (
    init_db, create_user, verify_user, get_user_by_id, update_last_login,
    add_reading_history, get_user_history, get_random_motivation,
    hash_password, get_db
)
from nltk.corpus import wordnet
import random

# --- APP SETUP ---
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey_change_in_production')
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize database
init_db()

# --- DECORATORS ---
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- CONTEXT PROCESSOR ---
@app.context_processor
def inject_user():
    """Make user available in all templates"""
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    return dict(current_user=user)

# --- AUTHENTICATION ROUTES ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Generate username from email (before @ symbol)
        username = email.split('@')[0] if email else ''
        
        # Validation
        if not all([username, email, password, full_name]):
            flash('All fields are required!', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('signup.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long!', 'error')
            return render_template('signup.html')
        
        # Create user
        user_id = create_user(username, email, password, full_name)
        
        if user_id:
            session['user_id'] = user_id
            flash(f'Welcome, {full_name}! Your account has been created.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email already exists! Please use a different email.', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required!', 'error')
            return render_template('login.html')
        
        user = verify_user(email, password)
        
        if user:
            session['user_id'] = user['id']
            update_last_login(user['id'])
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

# --- MAIN ROUTES ---
@app.route('/')
def redirect_home():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with stats, progress, motivation"""
    user = get_user_by_id(session['user_id'])
    history = get_user_history(session['user_id'], limit=5)
    motivation = get_random_motivation()
    
    # Calculate streak
    streak = calculate_user_streak(session['user_id'])
    
    # Get weekly progress
    weekly_progress = get_weekly_progress(session['user_id'])
    
    return render_template('dashboard.html',
                         user=user,
                         history=history,
                         motivation=motivation,
                         streak=streak,
                         weekly_progress=weekly_progress)

@app.route('/practice')
def practice():
    """Practice page - accessible to all, but saves history only for logged-in users"""
    return render_template('practice.html')

@app.route('/process', methods=['POST'])
def process():
    """Process text simplification - works for all, saves only for logged in"""
    text_input = request.form.get('text_input', '').strip()
    level = request.form.get('level', 'basic')
    original_text = ""
    stats = None

    # 🖼️ OCR - Using the module now!
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename:
            filename = f"{uuid.uuid4().hex}_{image_file.filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                image_file.save(image_path)
                print(f"✅ Image saved to: {image_path}")
                
                # Extract text using OCR
                original_text = extract_text(image_path)
                print(f"✅ OCR extracted text: {original_text[:100]}...")
                
                # Check if OCR returned an error
                if "ERROR" in original_text or "not installed" in original_text:
                    flash(original_text, 'error')
                    return render_template('practice.html')
                    
            except Exception as e:
                print(f"❌ Error processing image: {e}")
                flash(f'Error processing image: {str(e)}', 'error')
                return render_template('practice.html')

    # ✏️ Text Input (prioritize text input over image)
    if text_input:
        original_text = text_input
        print(f"✅ Text input received: {original_text[:100]}...")

    # ✅ Simplify Text with selected level
    if not original_text.strip():
        flash("Please upload an image or enter text.", 'warning')
        return render_template('practice.html')
    else:
        print(f"🔄 Simplifying text at {level} level...")
        
        # USE ENHANCED SIMPLIFICATION
        simplified_text = simplify_text(original_text, level=level)
        
        print(f"✅ Simplified text: {simplified_text[:100]}...")
        
        # Get text statistics
        stats = get_text_statistics(simplified_text)

    # 🎧 Generate Audio
    try:
        audio_path = generate_tts(simplified_text)
        print(f"✅ Audio generated: {audio_path}")
    except Exception as e:
        print(f"⚠️ Audio generation failed: {e}")
        audio_path = None

    # 🕐 Save History (only if logged in)
    if 'user_id' in session and original_text.strip():
        words_count = len(original_text.split())
        add_reading_history(
            session['user_id'],
            original_text,
            simplified_text,
            level,
            words_count
        )
        print(f"✅ History saved for user {session['user_id']}")
        
        # Check and unlock achievements
        check_achievements(session['user_id'])

    # Also save to session for non-logged users
    if 'history' not in session:
        session['history'] = []
    
    session['history'].insert(0, {
        'id': uuid.uuid4().hex,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'original': original_text,
        'simplified': simplified_text,
        'level': level
    })
    
    # Keep only last 10 in session
    session['history'] = session['history'][:10]
    session.modified = True

    print("✅ Rendering result page...")
    return render_template('result.html',
                         original_text=original_text,
                         simplified_text=simplified_text,
                         audio_path=audio_path,
                         level=level,
                         stats=stats)

@app.route('/history')
def history():
    """Show history - DB for logged in, session for guests"""
    if 'user_id' in session:
        history_items = get_user_history(session['user_id'], limit=50)
    else:
        history_items = session.get('history', [])
    
    return render_template('history.html', history=history_items)

@app.route('/clear')
def clear_history():
    """Clear session history only (DB history preserved)"""
    session.pop('history', None)
    flash('Session history cleared!', 'success')
    return redirect(url_for('history'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_user_by_id(session['user_id'])
    total_history = get_user_history(session['user_id'], limit=1000)
    
    # Calculate statistics
    total_words = sum(item.get('words_count', 0) for item in total_history)
    avg_difficulty = calculate_avg_difficulty(total_history)
    
    # Get achievements
    achievements = get_user_achievements(session['user_id'])
    
    return render_template('profile.html',
                         user=user,
                         total_words=total_words,
                         avg_difficulty=avg_difficulty,
                         achievements=achievements)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        bio = request.form.get('bio', '').strip()
        reading_level = request.form.get('reading_level', 'basic')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET full_name = ?, bio = ?, reading_level = ?
            WHERE id = ?
        ''', (full_name, bio, reading_level, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    user = get_user_by_id(session['user_id'])
    return render_template('edit_profile.html', user=user)

@app.route('/resources')
def resources():
    """Learning resources page - articles, videos, exercises"""
    resources = get_learning_resources()
    return render_template('resources.html', resources=resources)

@app.route('/resources/<int:resource_id>')
def view_resource(resource_id):
    """View single resource"""
    resource = get_resource_by_id(resource_id)
    if not resource:
        flash('Resource not found!', 'error')
        return redirect(url_for('resources'))
    
    return render_template('view_resource.html', resource=resource)

@app.route('/bookmark/<int:resource_id>', methods=['POST'])
@login_required
def bookmark_resource(resource_id):
    """Bookmark a resource"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO bookmarks (user_id, resource_id)
            VALUES (?, ?)
        ''', (session['user_id'], resource_id))
        conn.commit()
        flash('Resource bookmarked!', 'success')
    except:
        flash('Already bookmarked!', 'info')
    finally:
        conn.close()
    
    return redirect(url_for('resources'))

@app.route('/leaderboard')
def leaderboard():
    """Global leaderboard"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, full_name, points, total_texts_simplified, streak_days
        FROM users
        ORDER BY points DESC
        LIMIT 50
    ''')
    top_users = cursor.fetchall()
    conn.close()
    
    return render_template('leaderboard.html', top_users=[dict(u) for u in top_users])

@app.route('/synonym')
def synonym():
    """Get synonyms for a word"""
    word = request.args.get('word', '')
    synonyms = set()
    
    try:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                if lemma.name().lower() != word.lower():
                    synonyms.add(lemma.name().replace('_', ' '))
    except:
        pass
    
    return jsonify({'synonyms': list(synonyms)[:8]})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '')
        message = request.form.get('message', '').strip()
        
        if all([name, email, message]):
            # Save to database or send email
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    subject TEXT,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                INSERT INTO contact_messages (name, email, subject, message)
                VALUES (?, ?, ?, ?)
            ''', (name, email, subject, message))
            conn.commit()
            conn.close()
            
            flash('Message sent! We will get back to you soon.', 'success')
            return render_template('contact.html', contact_sent=True)
        else:
            flash('Please fill all required fields!', 'error')
    
    return render_template('contact.html')

# --- EYE TRACKING ROUTES ---
@app.route('/start-eye-tracking', methods=['POST'])
@login_required
def start_tracking():
    """Start eye tracking session"""
    try:
        # Log that tracking started
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO eye_tracking_events (user_id, event_type)
            VALUES (?, ?)
        ''', (session['user_id'], 'tracking_started'))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'started', 'message': 'Eye tracking initiated'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/log-difficulty', methods=['POST'])
def log_difficulty():
    """Log difficulty event from eye tracking"""
    try:
        text_id = request.json.get('text_id')
        
        if 'user_id' in session:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO eye_tracking_events (user_id, event_type, text_id)
                VALUES (?, ?, ?)
            ''', (session['user_id'], 'difficulty_detected', text_id))
            conn.commit()
            conn.close()
        
        # Also log to file
        log_difficulty_event()
        
        return jsonify({'status': 'logged'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- HELPER FUNCTIONS ---
def calculate_user_streak(user_id):
    """Calculate user's reading streak"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(created_at) as date
        FROM reading_history
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not dates:
        return 0
    
    streak = 1
    for i in range(len(dates) - 1):
        date1 = datetime.strptime(dates[i], '%Y-%m-%d')
        date2 = datetime.strptime(dates[i + 1], '%Y-%m-%d')
        diff = (date1 - date2).days
        
        if diff == 1:
            streak += 1
        elif diff > 1:
            break
    
    return streak

def get_weekly_progress(user_id):
    """Get last 7 days progress"""
    conn = get_db()
    cursor = conn.cursor()
    
    progress = []
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) as count, SUM(words_count) as words
            FROM reading_history
            WHERE user_id = ? AND DATE(created_at) = ?
        ''', (user_id, date))
        result = cursor.fetchone()
        progress.append({
            'date': date,
            'texts': result[0] if result else 0,
            'words': result[1] if result and result[1] else 0
        })
    
    conn.close()
    return progress

def check_achievements(user_id):
    """Check and unlock achievements"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user stats
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = dict(cursor.fetchone())
    
    # Check "First Steps" achievement
    if user['total_texts_simplified'] == 1:
        unlock_achievement(user_id, 1)  # First Steps
    
    # Check "Speed Reader" achievement
    if user['total_texts_simplified'] >= 50:
        unlock_achievement(user_id, 4)  # Speed Reader
    
    # Check "Knowledge Seeker" achievement
    if user['total_texts_simplified'] >= 100:
        unlock_achievement(user_id, 5)  # Knowledge Seeker
    
    # Check streak achievements
    streak = calculate_user_streak(user_id)
    if streak >= 7:
        unlock_achievement(user_id, 2)  # Reading Streak
    
    conn.close()

def unlock_achievement(user_id, achievement_id):
    """Unlock an achievement for user"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO user_achievements (user_id, achievement_id)
            VALUES (?, ?)
        ''', (user_id, achievement_id))
        
        # Add points
        cursor.execute('SELECT points FROM achievements WHERE id = ?', (achievement_id,))
        points = cursor.fetchone()[0]
        cursor.execute('UPDATE users SET points = points + ? WHERE id = ?', (points, user_id))
        
        conn.commit()
    except:
        pass  # Already unlocked
    finally:
        conn.close()

def get_user_achievements(user_id):
    """Get user's unlocked achievements"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, ua.unlocked_at
        FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
    ''', (user_id,))
    achievements = cursor.fetchall()
    conn.close()
    return [dict(a) for a in achievements]

def calculate_avg_difficulty(history):
    """Calculate average difficulty from history"""
    if not history:
        return "N/A"
    
    levels = [item.get('reading_level', 'basic') for item in history]
    level_map = {'basic': 1, 'intermediate': 2, 'advanced': 3}
    avg = sum(level_map.get(l, 1) for l in levels) / len(levels)
    
    if avg < 1.5:
        return "Basic"
    elif avg < 2.5:
        return "Intermediate"
    else:
        return "Advanced"

def get_learning_resources():
    """Get all learning resources"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM learning_resources ORDER BY created_at DESC LIMIT 50')
    resources = cursor.fetchall()
    conn.close()
    return [dict(r) for r in resources]

def get_resource_by_id(resource_id):
    """Get single resource"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM learning_resources WHERE id = ?', (resource_id,))
    resource = cursor.fetchone()
    conn.close()
    return dict(resource) if resource else None

# --- ERROR HANDLERS ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# --- RUN APP ---
if __name__ == "__main__":
    print("🚀 Starting AI Reading Helper...")
    print("📍 Running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)