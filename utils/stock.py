import requests
import pandas as pd
from textblob import TextBlob

# Flask server URL
FLASK_URL = "http://localhost:5000"

# Function to fetch stock data
def get_stock_data(ticker, period='1d'):
    response = requests.get(f"{FLASK_URL}/stock/{ticker}?period={period}")
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch news articles
def fetch_news(query):
    response = requests.get(f"{FLASK_URL}/news/{query}")
    if response.status_code == 200:
        return response.json()
    return []

# Function to analyze sentiment
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Function to add a stock to the watchlist
def add_to_watchlist(username, ticker):
    response = requests.post(f"{FLASK_URL}/watchlist/add", json={"username": username, "ticker": ticker})
    return response.status_code == 201

# Function to fetch the user's watchlist
def get_watchlist(username):
    response = requests.get(f"{FLASK_URL}/watchlist/{username}")
    if response.status_code == 200:
        return response.json().get("watchlist", [])
    return []