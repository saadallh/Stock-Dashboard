import React from "react";

function News({ news }) {
    // Fetch news data
    
  
  return (
    <div className="news">
      <h3>Latest News & Sentiment Analysis</h3>

      {/* Display news articles */}
      {news.map((article, index) => (
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