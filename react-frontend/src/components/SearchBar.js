import React, { useState } from "react";
import axios from "axios";
import "./SearchBar.css"; // Import the CSS file

function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  // Fetch stock search results
  const fetchSearchResults = async () => {
    if (!query) return; // Don't search if the query is empty
    try {
      const response = await axios.get(
        `https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=${query}&apikey=YOUR_API_KEY`
      );
      setResults(response.data.bestMatches || []);
    } catch (error) {
      console.error("Failed to fetch search results:", error);
    }
  };

  // Handle search input change
  const handleInputChange = (e) => {
    setQuery(e.target.value);
    fetchSearchResults(); // Fetch results as the user types
  };

  // Handle search result click
  const handleResultClick = (symbol) => {
    onSearch(symbol); // Pass the selected symbol to the parent component
    setQuery(""); // Clear the search input
    setResults([]); // Clear the results
  };

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search for a stock..."
        value={query}
        onChange={handleInputChange}
      />
      {results.length > 0 && (
        <ul className="search-results">
          {results.map((result, index) => (
            <li key={index} onClick={() => handleResultClick(result["1. symbol"])}>
              {result["1. symbol"]} - {result["2. name"]}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default SearchBar;