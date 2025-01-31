import React from "react";
import Watchlist from "./Watchlist";
import StockData from "./StockData";
import axios from "axios";
import StockComparison from "./StockComparison";
import News from "./News";

function Home({ user, setUser }) {
  const handleLogout = async () => {
    try {
      await axios.post("http://localhost:5000/logout", {}, { withCredentials: true });
      setUser(null); // Clear the user state
      window.location.href = "/"; // Redirect to login page
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <div>
      <h2>Welcome, {user}!</h2>
      <button onClick={handleLogout}>Logout</button>

      {/* Watchlist */}
      <Watchlist user={user} />

      {/* Watchlist */}
      <News user={user} />

      {/* Watchlist */}
      <StockData user={user} />

   
    </div>
  );
}

export default Home;