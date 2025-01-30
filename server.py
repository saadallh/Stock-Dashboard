from flask import Flask, request, jsonify
from dotenv import load_dotenv
import sqlite3
import os
from newsapi import NewsApiClient

app = Flask(__name__)

# Initialize SQLite database
conn = sqlite3.connect('stock_dashboard.db', check_same_thread=False)
cursor = conn.cursor()

# Create a users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

# Create a watchlist table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        ticker TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
''')
conn.commit()

# Initialize NewsAPI client
load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')  # Use environment variable or hardcode (not recommended)
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# Endpoint to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists"}), 400

# Endpoint to authenticate a user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    if result and result[0] == password:
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# Endpoint to add a stock to the user's watchlist
@app.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    data = request.json
    username = data.get('username')
    ticker = data.get('ticker')
    try:
        cursor.execute('INSERT INTO watchlist (username, ticker) VALUES (?, ?)', (username, ticker))
        conn.commit()
        return jsonify({"message": "Stock added to watchlist"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Stock already in watchlist"}), 400

# Endpoint to fetch the user's watchlist
@app.route('/watchlist/<username>', methods=['GET'])
def get_watchlist(username):
    cursor.execute('SELECT ticker FROM watchlist WHERE username = ?', (username,))
    watchlist = [row[0] for row in cursor.fetchall()]
    return jsonify({"watchlist": watchlist}), 200

# Endpoint to fetch stock data
@app.route('/stock/<ticker>', methods=['GET'])
def get_stock(ticker):
    import yfinance as yf
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
    articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=5)
    return jsonify(articles['articles']), 200

if __name__ == '__main__':
    app.run(debug=True)