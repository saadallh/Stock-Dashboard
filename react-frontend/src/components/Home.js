import React, { useState, useEffect } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  Legend,
} from "chart.js";
import "chartjs-adapter-date-fns";
import News from "./News";
import "./Home.css";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  Legend
);

function Home({ user, setUser }) {
  const [searchTerm, setSearchTerm] = useState("AAPL"); // Default to AAPL
  const [stockData, setStockData] = useState(null);
  const [news, setNews] = useState([]);
  const [period, setPeriod] = useState("1d"); // Default period

  const handleLogout = async () => {
    try {
      await axios.post("http://my-app-lb-1056957048.us-west-2.elb.amazonaws.com:5000/logout", {}, { withCredentials: true });
      setUser(null);
      window.location.href = "/";
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  // Fetch stock data from the backend
  const fetchStockData = async (ticker, period) => {
    try {
      const response = await axios.get(`http://my-app-lb-1056957048.us-west-2.elb.amazonaws.com:5000/stock/${ticker}`, {
        params: { period }, // Use the selected period
      });
      setStockData(response.data);
    } catch (error) {
      console.error("Failed to fetch stock data:", error);
    }
  };

  // Fetch news data
  const fetchNews = async (symbol) => {
    try {
      const response = await axios.get(`http://my-app-lb-1056957048.us-west-2.elb.amazonaws.com:5000/news/${symbol}`);
      setNews(response.data);
    } catch (error) {
      console.error("Failed to fetch news:", error);
    }
  };

  // Fetch stock data and news when the component mounts or searchTerm/period changes
  useEffect(() => {
    fetchStockData(searchTerm, period);
    fetchNews(searchTerm);
  }, [searchTerm, period]);

  // Handle search form submission
  const handleSearch = (event) => {
    event.preventDefault();
    const symbol = event.target.elements.search.value;
    setSearchTerm(symbol);
  };

  // Handle period change
  const handlePeriodChange = (event) => {
    setPeriod(event.target.value);
  };

  // Prepare chart data for the graph
  const chartData = {
    labels: stockData?.history.map((entry) => new Date(entry.Date)), // Convert dates to Date objects
    datasets: [
      {
        label: "Stock Price",
        data: stockData?.history.map((entry) => entry.Close), // Extract closing prices from history
        borderColor: "rgba(75,192,192,1)",
        fill: false,
      },
    ],
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false, // Allow the chart to resize
    scales: {
      x: {
        type: "time",
        time: {
          unit: "day",
          displayFormats: {
            day: "MMM d",
          },
        },
        title: {
          display: true,
          text: "Date",
        },
      },
      y: {
        title: {
          display: true,
          text: "Price (USD)",
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || "";
            const value = context.raw || 0;
            return `${label}: $${value.toFixed(2)}`;
          },
        },
      },
    },
  };

  return (
    <div className="home">
      <div className="header">
        <h1>Welcome, {user}!</h1>
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <div className="search-bar">
        <form onSubmit={handleSearch}>
          <input type="text" name="search" placeholder="Search for a stock..." />
          <button type="submit">Search</button>
        </form>
      </div>

      <div className="graph">
        <h2>Stock Price Graph</h2>
        {stockData ? (
          <>
            <h3>{stockData.company_name}</h3>
            <p>Sector: {stockData.sector}</p>
            <div className="period-selector">
              <label htmlFor="period">Select Period: </label>
              <select id="period" value={period} onChange={handlePeriodChange}>
                <option value="1d">1 Day</option>
                <option value="5d">5 Days</option>
                <option value="1mo">1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="1y">1 Year</option>
              </select>
            </div>
            <div className="chart-container">
              <Line data={chartData} options={chartOptions} />
            </div>
          </>
        ) : (
          <p>Loading stock data...</p>
        )}
      </div>

      <div className="news">
        <News news={news} />
      </div>
    </div>
  );
}

export default Home;