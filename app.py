"""
Life Timeline Analyzer & Personal Time Dashboard
Main Flask Application Entry Point
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
from functools import wraps
import io

# Import utility modules
from utils.calculations import LifeCalculator
from utils.pdf_generator import generate_pdf_report

# ─── App Configuration ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'database.db'


# ─── Database Helpers ─────────────────────────────────────────────────────────
def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database with required tables."""
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    UNIQUE NOT NULL,
                email    TEXT    UNIQUE NOT NULL,
                password TEXT    NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_data (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER UNIQUE NOT NULL,
                dob        TEXT    NOT NULL,
                timezone   TEXT    DEFAULT "UTC",
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')
    print("✅ Database initialized.")


# ─── Auth Decorator ───────────────────────────────────────────────────────────
def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ─── Routes: Auth ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Basic validation
        if not username or not email or not password:
            error = "All fields are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            hashed_pw = generate_password_hash(password)
            try:
                with get_db() as conn:
                    conn.execute(
                        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                        (username, email, hashed_pw)
                    )
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = "Username or email already exists."

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            error = "Both fields are required."
        else:
            with get_db() as conn:
                user = conn.execute(
                    "SELECT * FROM users WHERE username = ?", (username,)
                ).fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id']   = user['id']
                session['username']  = user['username']
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid username or password."

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ─── Routes: DOB Setup ────────────────────────────────────────────────────────
@app.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    error = None
    if request.method == 'POST':
        dob      = request.form.get('dob', '').strip()
        timezone = request.form.get('timezone', 'UTC').strip()

        try:
            datetime.strptime(dob, '%Y-%m-%d')  # Validate date format
            with get_db() as conn:
                existing = conn.execute(
                    "SELECT id FROM user_data WHERE user_id = ?", (session['user_id'],)
                ).fetchone()
                if existing:
                    conn.execute(
                        "UPDATE user_data SET dob = ?, timezone = ? WHERE user_id = ?",
                        (dob, timezone, session['user_id'])
                    )
                else:
                    conn.execute(
                        "INSERT INTO user_data (user_id, dob, timezone) VALUES (?, ?, ?)",
                        (session['user_id'], dob, timezone)
                    )
            return redirect(url_for('dashboard'))
        except ValueError:
            error = "Invalid date format. Please use YYYY-MM-DD."

    # Check if user already has DOB set (for edit mode)
    with get_db() as conn:
        data = conn.execute(
            "SELECT * FROM user_data WHERE user_id = ?", (session['user_id'],)
        ).fetchone()

    return render_template('setup.html', error=error, existing_data=data)


# ─── Routes: Dashboard ────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    with get_db() as conn:
        data = conn.execute(
            "SELECT * FROM user_data WHERE user_id = ?", (session['user_id'],)
        ).fetchone()

    if not data:
        return redirect(url_for('setup'))

    # Calculate all life stats
    calc   = LifeCalculator(data['dob'], data['timezone'])
    stats  = calc.get_all_stats()

    return render_template('dashboard.html',
                           username=session['username'],
                           stats=stats,
                           dob=data['dob'])


# ─── Routes: API (for live updates) ──────────────────────────────────────────
@app.route('/api/stats')
@login_required
def api_stats():
    """Return live-updated stats as JSON."""
    with get_db() as conn:
        data = conn.execute(
            "SELECT * FROM user_data WHERE user_id = ?", (session['user_id'],)
        ).fetchone()

    if not data:
        return jsonify({'error': 'No DOB set'}), 404

    calc  = LifeCalculator(data['dob'], data['timezone'])
    stats = calc.get_all_stats()
    return jsonify(stats)


# ─── Routes: PDF Export ──────────────────────────────────────────────────────
@app.route('/export/pdf')
@login_required
def export_pdf():
    """Generate and serve a PDF report."""
    with get_db() as conn:
        data = conn.execute(
            "SELECT * FROM user_data WHERE user_id = ?", (session['user_id'],)
        ).fetchone()
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?", (session['user_id'],)
        ).fetchone()

    if not data:
        return redirect(url_for('setup'))

    calc  = LifeCalculator(data['dob'], data['timezone'])
    stats = calc.get_all_stats()

    pdf_bytes = generate_pdf_report(user['username'], user['email'], data['dob'], stats)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'life_timeline_{user["username"]}.pdf'
    )


# ─── Bootstrap & Run ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)
