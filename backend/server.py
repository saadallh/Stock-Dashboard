from flask import Flask, request, jsonify, session, g
from dotenv import load_dotenv
import secrets
import yfinance as yf
from flask_session import Session
import sqlite3
import os
from newsapi import NewsApiClient
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Set session lifetime (e.g., 30 minutes)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Enable CORS for all routes, allow credentials, and specify the frontend origin
CORS(app, supports_credentials=True, origins=["http://specify frontend ip"])

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Database file path
DATABASE = 'stock_dashboard.db'

# Function to get the database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, check_same_thread=False)
    return g.db

# Function to get a new cursor
def get_cursor():
    return get_db().cursor()

# Close the database connection at the end of each request
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize database tables
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Create a portfolio table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ticker TEXT NOT NULL,
                shares INTEGER NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')

        # Create a users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Create a watchlist table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ticker TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')

        db.commit()

# Initialize the database tables
init_db()

# Initialize NewsAPI client
NEWS_API_KEY = os.getenv('NEWS_API_KEY')  # Use environment variable or hardcode (not recommended)
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

@app.route('/',methods=['GET'])
def health_check():
    return jsonify({"message": "Hi from the backend"}), 200  # ALB expects a 2xx response

# Endpoint to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    hash_password = generate_password_hash(password)
    try:
        cursor = get_cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password))
        get_db().commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists"}), 400

# Endpoint to log in a user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        cursor = get_cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        if result and check_password_hash(result[0] ,password):
            session['username'] = username  # Store username in session
            session.permanent = True
            print(f"Session created: {session}")  # Debugging
            return jsonify({"message": "Login successful"}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Database error"}), 500

# Endpoint to log out a user
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  # Remove username from session
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/check-auth', methods=['GET'])
def check_auth():
    if 'username' in session:
        return jsonify({"authenticated": True, "username": session['username']}), 200
    return jsonify({"authenticated": False}), 200

# Endpoint to fetch stock data
@app.route('/stock/<ticker>', methods=['GET'])
def get_stock(ticker):
    if 'username' not in session:
        return jsonify({"message": "Unauthorized", "redirect": "/login"}), 401
    period = request.args.get('period', '1d')  # Get the period from query parameters
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if not hist.empty:
        return jsonify({
            "current_price": hist['Close'][-1],
            "company_name": stock.info.get('longName', 'N/A'),
            "sector": stock.info.get('sector', 'N/A'),
            "history": hist.reset_index().to_dict(orient='records')  # Convert DataFrame to a list of dicts
        }), 200
    return jsonify({"message": "Invalid ticker or no data available"}), 404

# Endpoint to fetch news articles
@app.route('/news/<query>', methods=['GET'])
def get_news(query):
    print("I'm Here //////////////////////////////////////////////")
    articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=5)
    print("Query")
    
    return jsonify(articles['articles']), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
