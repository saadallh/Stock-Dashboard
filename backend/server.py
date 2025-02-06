from flask import Flask, request, jsonify, session, g
from dotenv import load_dotenv
import secrets
import yfinance as yf
from flask_session import Session
import sqlite3
import os
from newsapi import NewsApiClient
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Enable CORS for all routes, allow credentials, and specify the frontend origin
CORS(app, supports_credentials=True, origins=["http://my-app-lb-1056957048.us-west-2.elb.amazonaws.com:3000"])

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
#NEWS_API_KEY = os.getenv('NEWS_API_KEY')  # Use environment variable or hardcode (not recommended)
NEWS_API_KEY = "d40fa564810544a68726d7755e269812"
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
    try:
        cursor = get_cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
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
    print(f"Login attempt: username={username}, password={password}")  # Debugging
    try:
        cursor = get_cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        if result and result[0] == password:
            session['username'] = username  # Store username in session
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

# Endpoint to add a stock to the user's watchlist
@app.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    data = request.json
    username = data.get('username')
    ticker = data.get('ticker')

    # Check if the ticker is valid using yfinance
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")  # Fetch 1 day of history to validate the ticker
        if hist.empty:
            return jsonify({"message": "Invalid ticker or no data available"}), 404
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return jsonify({"message": "Invalid ticker or no data available"}), 404

    # Add the ticker to the watchlist
    try:
        cursor = get_cursor()
        cursor.execute('INSERT INTO watchlist (username, ticker) VALUES (?, ?)', (username, ticker))
        get_db().commit()
        return jsonify({"message": "Stock added to watchlist"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Stock already in watchlist"}), 400
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Database error"}), 500

# Endpoint to remove a stock from the user's watchlist
@app.route('/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    data = request.json
    username = data.get('username')
    ticker = data.get('ticker')
    try:
        cursor = get_cursor()
        cursor.execute('DELETE FROM watchlist WHERE username = ? AND ticker = ?', (username, ticker))
        get_db().commit()
        return jsonify({"message": "Stock removed from watchlist"}), 200
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Failed to remove stock from watchlist"}), 500

# Endpoint to fetch the user's watchlist
@app.route('/watchlist/<username>', methods=['GET'])
def get_watchlist(username):
    try:
        cursor = get_cursor()
        cursor.execute('SELECT ticker FROM watchlist WHERE username = ?', (username,))
        watchlist = [row[0] for row in cursor.fetchall()]
        return jsonify({"watchlist": watchlist}), 200
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Failed to fetch watchlist"}), 500

# Endpoint to fetch stock data
@app.route('/stock/<ticker>', methods=['GET'])
def get_stock(ticker):
    
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

# Endpoint to fetch user portfolio
@app.route('/portfolio/<username>', methods=['GET'])
def get_portfolio(username):
    try:
        cursor = get_cursor()
        cursor.execute('SELECT ticker, shares FROM portfolio WHERE username = ?', (username,))
        portfolio = [{"ticker": row[0], "shares": row[1]} for row in cursor.fetchall()]
        return jsonify({"portfolio": portfolio}), 200
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Failed to fetch portfolio"}), 500

# Endpoint to add a stock to the user's portfolio
@app.route('/portfolio/add', methods=['POST'])
def add_to_portfolio():
    data = request.json
    username = data.get('username')
    ticker = data.get('ticker')
    shares = data.get('shares')
    try:
        cursor = get_cursor()
        cursor.execute('INSERT INTO portfolio (username, ticker, shares) VALUES (?, ?, ?)', (username, ticker, shares))
        get_db().commit()
        return jsonify({"message": "Stock added to portfolio"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Stock already in portfolio"}), 400
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Database error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
