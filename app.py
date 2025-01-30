import streamlit as st
import requests
import pandas as pd
import plotly.express as px

from views.login import login_page
from views.register import registration_page
from views.home import home_page

# Flask server URL
FLASK_URL = "http://localhost:5000"

# Function to register a new user
def register_user(username, password):
    response = requests.post(f"{FLASK_URL}/register", json={"username": username, "password": password})
    return response.status_code == 201

# Function to authenticate a user
def authenticate_user(username, password):
    response = requests.post(f"{FLASK_URL}/login", json={"username": username, "password": password})
    return response.status_code == 200

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
    from textblob import TextBlob
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Login page
def login_page():
    st.title("Login")
    st.write("Please log in to access the dashboard.")

    # Login form
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if authenticate_user(login_username, login_password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = login_username
            st.session_state['page'] = 'home'  # Redirect to the home page
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

    # Link to registration page
    if st.button("Go to Registration"):
        st.session_state['page'] = 'register'

# Registration page
def registration_page():
    st.title("Registration")
    st.write("Please register to create an account.")

    # Registration form
    reg_username = st.text_input("Username", key="reg_username")
    reg_password = st.text_input("Password", type="password", key="reg_password")
    if st.button("Register"):
        if register_user(reg_username, reg_password):
            st.success("User registered successfully! Please log in.")
            st.session_state['page'] = 'login'  # Redirect to the login page
        else:
            st.error("Registration failed")

    # Link to login page
    if st.button("Go to Login"):
        st.session_state['page'] = 'login'

# Main dashboard (home page)
def home_page():
    st.title("Stock Dashboard")
    st.header(f"Welcome, {st.session_state['username']}!")

    # Watchlist
    st.header("Your Watchlist")
    watchlist = get_watchlist(st.session_state['username'])
    for ticker in watchlist:
        st.write(f"- {ticker}")
    new_ticker = st.text_input("Add a stock to your watchlist")
    if st.button("Add to Watchlist"):
        if add_to_watchlist(st.session_state['username'], new_ticker):
            st.success(f"Added {new_ticker} to your watchlist!")
        else:
            st.error("Failed to add stock to watchlist")

    # Stock data
    st.header("Stock Data")
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")
    period = st.selectbox("Select Period", ['1d', '5d', '1mo', '3mo', '1y'], key="period")
    if st.button("Get Stock Data"):
        stock_data = get_stock_data(ticker, period)
        if stock_data:
            st.write(f"**Company Name:** {stock_data['company_name']}")
            st.write(f"**Sector:** {stock_data['sector']}")
            st.write(f"**Current Price:** ${stock_data['current_price']:.2f}")

            # Display price chart
            st.header(f"{ticker.upper()} Price Chart")
            hist = pd.DataFrame(stock_data['history'])  # Convert history back to DataFrame
            hist['Date'] = pd.to_datetime(hist['Date'])  # Convert 'Date' column to datetime
            fig = px.line(hist, x='Date', y='Close', title=f'{ticker.upper()} Price History')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Invalid ticker or no data available")

    # Comparison functionality
    st.header("Compare Stocks")
    compare_tickers = st.text_input("Enter Stock Tickers to Compare (comma-separated, e.g., AAPL,GOOGL,MSFT)", "AAPL,GOOGL")
    compare_tickers = [t.strip() for t in compare_tickers.split(",")]
    compare_period = st.selectbox("Select Period for Comparison", ['1d', '5d', '1mo', '3mo', '1y'], key="compare_period")
    if st.button("Compare Stocks"):
        combined_data = pd.DataFrame()
        for ticker in compare_tickers:
            stock_data = get_stock_data(ticker, compare_period)
            if stock_data:
                hist = pd.DataFrame(stock_data['history'])  # Convert history back to DataFrame
                hist['Date'] = pd.to_datetime(hist['Date'])  # Convert 'Date' column to datetime
                hist['Ticker'] = ticker.upper()
                combined_data = pd.concat([combined_data, hist])
        
        if not combined_data.empty:
            st.header("Combined Stock Price Comparison")
            fig = px.line(combined_data, x='Date', y='Close', color='Ticker', title='Stock Price Comparison')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No valid data available for comparison")

    # News sentiment analysis
    st.header("Latest News & Sentiment Analysis")
    articles = fetch_news(ticker)
    for article in articles:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(article['title'])
            st.write(article['description'])
            st.markdown(f"[Read more]({article['url']})")
        with col2:
            sentiment = analyze_sentiment(article['title'] + " " + (article['content'] or ""))
            sentiment_color = "green" if sentiment > 0 else "red" if sentiment < 0 else "gray"
            st.markdown(f"**Sentiment:** :{sentiment_color}[{sentiment:.2f}]")

    # Logout button
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.session_state['page'] = 'login'  # Redirect to the login page
        st.success("Logged out successfully!")

# Main app logic
def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'  # Default to the login page

    # Render the appropriate page
    if st.session_state['authenticated']:
        if st.session_state['page'] == 'home':
            home_page()
    else:
        if st.session_state['page'] == 'login':
            login_page()
        elif st.session_state['page'] == 'register':
            registration_page()

# Run the app
if __name__ == '__main__':
    main()