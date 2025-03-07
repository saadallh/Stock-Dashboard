import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Login.css";

function Login({ setUser }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    // Check if the user is already authenticated
    axios.get("http://localhost:5000/check-auth", { withCredentials: true })
      .then(response => {
        if (response.data.authenticated) {
          setUser(response.data.username);
          window.location.href = "/home";
        }
      })
      .catch(error => {
        console.error("Error checking authentication:", error);
      });
  }, [setUser]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:5000/login",
        { username, password },
        { withCredentials: true }
      );
      if (response.status === 200) {
        setUser(username);
        window.location.href = "/home"; // Redirect to home page after login
      }
    } catch (error) {
      setError("Invalid credentials");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="error">{error}</p>}
          <button type="submit">Login</button>
        </form>
        <p className="register-link">
          Don't have an account? <a href="/register">Register here</a>
        </p>
      </div>
    </div>
  );
}

export default Login;