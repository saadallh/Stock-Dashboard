import React, { useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js"; // For rendering Plotly charts

function StockData() {
  const [ticker, setTicker] = useState("AAPL"); // Default ticker
  const [period, setPeriod] = useState("1d"); // Default period
  const [stockData, setStockData] = useState(null); // Store stock data

  // Fetch stock data
  const fetchStockData = async () => {
    try {
      const response = await axios.get(`http://my-app-lb-1827961121.us-west-2.elb.amazonaws.com:5000/stock/${ticker}`, {
        params: { period },
        withCredentials: true,
      });
      setStockData(response.data); // Set the fetched stock data
    } catch (error) {
      alert("Invalid ticker or no data available");
    }
  };

  return (
    <div className="stock-data">
      <h3>Stock Data</h3>
      <input
        type="text"
        placeholder="Enter Stock Ticker (e.g., AAPL)"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
      />
      <select value={period} onChange={(e) => setPeriod(e.target.value)}>
        <option value="1d">1 Day</option>
        <option value="5d">5 Days</option>
        <option value="1mo">1 Month</option>
        <option value="3mo">3 Months</option>
        <option value="1y">1 Year</option>
      </select>
      <button onClick={fetchStockData}>Get Stock Data</button>

      {/* Display stock data */}
      {stockData && (
        <div>
          <p>Company Name: {stockData.company_name}</p>
          <p>Sector: {stockData.sector}</p>
          <p>Current Price: ${stockData.current_price.toFixed(2)}</p>

          {/* Render price chart */}
          <Plot
            data={[
              {
                x: stockData.history.map((entry) => entry.Date),
                y: stockData.history.map((entry) => entry.Close),
                type: "scatter",
                mode: "lines",
                name: ticker.toUpperCase(),
              },
            ]}
            layout={{ title: `${ticker.toUpperCase()} Price History` }}
          />
        </div>
      )}
    </div>
  );
}

export default StockData;