import streamlit as st
import pandas as pd
import plotly.express as px
from utils.stock import get_stock_data, fetch_news, analyze_sentiment, add_to_watchlist, get_watchlist

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