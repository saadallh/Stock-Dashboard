import React, { useState } from "react";
import axios from "axios";

function News() {
  const [ticker, setTicker] = useState("AAPL"); // Default ticker
  const [articles, setArticles] = useState([]); // Store news articles

  // Fetch news articles
  const fetchNews = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/news/${ticker}`, {
        withCredentials: true,
      });
      setArticles(response.data); // Set the fetched articles
    } catch (error) {
      console.error("Failed to fetch news:", error);
    }
  };

  return (
    <div className="news">
      <h3>Latest News & Sentiment Analysis</h3>
      <input
        type="text"
        placeholder="Enter Stock Ticker (e.g., AAPL)"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
      />
      <button onClick={fetchNews}>Fetch News</button>

      {/* Display news articles */}
      {articles.map((article, index) => (
        <div key={index} className="article">
          <h4>{article.title}</h4>
          <p>{article.description}</p>
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            Read more
          </a>
          {/* Placeholder for sentiment analysis */}
          <div style={{ marginTop: "10px" }}>
            <strong>Sentiment:</strong> [Add sentiment analysis here]
          </div>
        </div>
      ))}
    </div>
  );
}

export default News;