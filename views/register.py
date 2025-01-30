import streamlit as st
from utils.auth import register_user

def registration_page():
    st.title("Registration")
    st.write("Please register to create an account.")

    # Registration form
    reg_username = st.text_input("Username", key="reg_username")
    reg_password = st.text_input("Password", type="password", key="reg_password")
    if st.button("Register"):
        if register_user(reg_username, reg_password):
            st.success("User registered successfully! Please log in.")
            st.session_state['page'] = 'login'  # Redirect to the login page
        else:
            st.error("Registration failed")

    # Link to login page
    if st.button("Go to Login"):
        st.session_state['page'] = 'login'