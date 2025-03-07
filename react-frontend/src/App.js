import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import Login from "./components/Login";
import Register from "./components/Register";
import Home from "./components/Home";

function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true); // Add a loading state

  // Check if the user is already logged in (e.g., on page reload)
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get("http://localhost:5000/check-auth", {
          withCredentials: true, // Ensure cookies are sent with the request
        });

        if (response.data.authenticated) {
          setUser(response.data.username); // Set the user state if authenticated
        } else {
          setUser(null); // Clear the user state if not authenticated
        }
      } catch (error) {
        console.error("Error checking authentication:", error);
        setUser(null); // Clear the user state on error
      } finally {
        setIsLoading(false); // Set loading to false after the check
      }
    };

    checkAuth(); // Call the function to check authentication
  }, []);

  // If still loading, show a loading message or spinner
  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        {/* Redirect to /home if the user is logged in, otherwise show Login */}
        <Route
          path="/"
          element={user ? <Navigate to="/home" /> : <Login setUser={setUser} />}
        />
        {/* Register page */}
        <Route path="/register" element={<Register />} />
        {/* Home page (protected route) */}
        <Route
          path="/home"
          element={user ? <Home user={user} setUser={setUser} /> : <Navigate to="/" />}
        />
      </Routes>
    </Router>
  );
}

export default App;