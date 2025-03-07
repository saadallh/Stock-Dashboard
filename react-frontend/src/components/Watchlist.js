import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Watchlist.css"; // Import Watchlist CSS

function Watchlist({ user }) {
  const [watchlist, setWatchlist] = useState([]);
  const [newTicker, setNewTicker] = useState("");

  // Fetch watchlist on component mount
  useEffect(() => {
    fetchWatchlist();
  }, [user]);

  // Fetch watchlist from backend
  const fetchWatchlist = async () => {
    try {
      const response = await axios.get(`http://my-app-lb-1827961121.us-west-2.elb.amazonaws.com:5000/watchlist/${user}`, {
        withCredentials: true,
      });
      setWatchlist(response.data.watchlist);
    } catch (error) {
      console.error("Failed to fetch watchlist:", error);
    }
  };

  // Add a stock to the watchlist
  const addToWatchlist = async () => {
    try {
      await axios.post(
        "http://my-app-lb-1827961121.us-west-2.elb.amazonaws.com:5000/watchlist/add",
        { username: user, ticker: newTicker },
        { withCredentials: true }
      );
      setNewTicker("");
      fetchWatchlist(); // Refresh watchlist
    } catch (error) {
      alert("Failed to add stock to watchlist");
    }
  };

  // Remove a stock from the watchlist
  const removeFromWatchlist = async (ticker) => {
    try {
      await axios.post(
        "http://localhost:5000/watchlist/remove",
        { username: user, ticker },
        { withCredentials: true }
      );
      fetchWatchlist(); // Refresh watchlist
    } catch (error) {
      console.error("Failed to remove stock from watchlist:", error);
    }
  };

  return (
    <div className="watchlist">
      <h3>Your Watchlist</h3>
      <ul>
        {watchlist.map((ticker, index) => (
          <li key={index}>
            {ticker}
            <button className="remove-button" onClick={() => removeFromWatchlist(ticker)}>
              Remove
            </button>
          </li>
        ))}
      </ul>
      <div className="add-ticker">
        <input
          type="text"
          placeholder="Add a stock to your watchlist"
          value={newTicker}
          onChange={(e) => setNewTicker(e.target.value)}
        />
        <button onClick={addToWatchlist}>Add</button>
      </div>
    </div>
  );
}

export default Watchlist;