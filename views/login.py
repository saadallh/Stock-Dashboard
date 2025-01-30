import streamlit as st
from utils.auth import authenticate_user

def login_page():
    st.title("Login")
    st.write("Please log in to access the dashboard.")

    # Login form
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if authenticate_user(login_username, login_password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = login_username
            st.session_state['page'] = 'home'  # Redirect to the home page
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

    # Link to registration page
    if st.button("Go to Registration"):
        st.session_state['page'] = 'register'