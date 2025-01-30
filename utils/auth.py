import requests

# Flask server URL
FLASK_URL = "http://localhost:5000"

# Function to register a new user
def register_user(username, password):
    response = requests.post(f"{FLASK_URL}/register", json={"username": username, "password": password})
    return response.status_code == 201

# Function to authenticate a user
def authenticate_user(username, password):
    response = requests.post(f"{FLASK_URL}/login", json={"username": username, "password": password})
    return response.status_code == 200