import React, { useState, useEffect } from "react";
import axios from "axios";

function Watchlist({ user }) {
  const [watchlist, setWatchlist] = useState([]);
  const [newTicker, setNewTicker] = useState("");

  // Fetch watchlist on component mount
  useEffect(() => {
    fetchWatchlist();
  }, []);

  // Fetch watchlist from backend
  const fetchWatchlist = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/watchlist/${user}`, {
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
        "http://localhost:5000/watchlist/add",
        { username: user, ticker: newTicker },
        { withCredentials: true }
      );
      setNewTicker("");
      fetchWatchlist(); // Refresh watchlist
      alert(`${newTicker} added to your watchlist!`);
    } catch (error) {
      alert("Failed to add stock to watchlist");
    }
  };

  return (
    <div>
      <h3>Your Watchlist</h3>
      <ul>
        {watchlist.map((ticker, index) => (
          <li key={index}>{ticker}</li>
        ))}
      </ul>
      <input
        type="text"
        placeholder="Add a stock to your watchlist"
        value={newTicker}
        onChange={(e) => setNewTicker(e.target.value)}
      />
      <button onClick={addToWatchlist}>Add to Watchlist</button>
    </div>
  );
}

export default Watchlist;