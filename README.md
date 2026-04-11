# ⧖ Life Timeline Analyzer & Personal Time Dashboard

A full-stack Flask + SQLite web application that turns your date of birth into a living, breathing analytics dashboard.

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 Auth | Register, login, logout with password hashing |
| 📅 DOB Setup | Set/edit date of birth + timezone |
| 🧠 Age Engine | Years, months, days, hours, minutes, live seconds |
| 🌗 Day/Night Split | Approximate daylight vs. night hours lived |
| ⏰ Live Clock | Real-time digital clock + ticking age counter |
| 📊 Charts | Pie, bar, and progress charts via Chart.js |
| 💡 Life Progress | % of 80-year lifespan completed, with progress bar |
| 🎂 Birthday Countdown | Days + live HH:MM:SS countdown |
| 🧬 Bio Stats | Heartbeats, breaths, sleep time, steps walked |
| 🧾 PDF Export | Download full report via ReportLab |
| 🌍 Timezone | Calculations adjust to user's timezone |
| 💡 Time Insights | "You've lived over 1 billion seconds" etc. |

## 📁 Project Structure

```
life_timeline/
├── app.py                   # Flask application, routes, auth
├── database.db              # SQLite database (auto-created)
├── requirements.txt
├── README.md
├── utils/
│   ├── __init__.py
│   ├── calculations.py      # LifeCalculator class
│   └── pdf_generator.py     # ReportLab PDF builder
├── templates/
│   ├── base.html            # Base layout
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── setup.html           # DOB + timezone setup
│   └── dashboard.html       # Main analytics dashboard
└── static/
    ├── css/
    │   └── main.css         # Dark glassmorphism theme
    └── js/
        └── dashboard.js     # Live counters, charts, countdown
```

## 🚀 Running Locally

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone / unzip the project
cd life_timeline

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

The app will be available at **http://localhost:5050**

### First Use
1. Go to http://localhost:5050/register
2. Create your account
3. Enter your date of birth and timezone
4. Enjoy your personal life dashboard!

## 🗄️ Database Schema

```sql
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT UNIQUE NOT NULL,
    email      TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_data (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER UNIQUE NOT NULL,
    dob        TEXT NOT NULL,
    timezone   TEXT DEFAULT 'UTC',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🔒 Security

- Passwords are hashed using `werkzeug.security.generate_password_hash` (PBKDF2+SHA256)
- Session secret key is randomly generated at startup
- Input validation on all form fields
- SQL injection prevented via parameterized queries
- Date format validated before storage

## 🎨 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3 |
| Database | SQLite (via stdlib `sqlite3`) |
| Frontend | HTML5, CSS3, JavaScript (ES6+) |
| UI Framework | Bootstrap 5 |
| Charts | Chart.js 4 |
| PDF | ReportLab |
| Fonts | Google Fonts (Syne + DM Sans + JetBrains Mono) |
| Icons | Bootstrap Icons |
| Timezone | pytz |
