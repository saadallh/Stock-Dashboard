import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import Login from "./components/Login";
import Register from "./components/Register";
import Home from "./components/Home";

function App() {
  const [user, setUser] = useState(null);

  // Check if the user is already logged in (e.g., on page reload)
  useEffect(() => {
    const storedUser = localStorage.getItem("user"); // Retrieve user from localStorage
    if (storedUser) {
      setUser(storedUser); // Set the user state if a value exists in localStorage
    }
  }, []);

  // Update localStorage whenever the user state changes
  useEffect(() => {
    if (user) {
      localStorage.setItem("user", user); // Save user to localStorage
    } else {
      localStorage.removeItem("user"); // Remove user from localStorage on logout
    }
  }, [user]);

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