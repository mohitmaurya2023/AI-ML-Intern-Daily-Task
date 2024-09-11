import streamlit as st
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uuid
import json
import re
import pymongo

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["userdata"]

USER_DATA_FILE = db["users"]
RESET_TOKENS_FILE = db["reset_token"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_data():
    return [user["email"] for user in USER_DATA_FILE.find() if "email" in user]

def save_user_data(data):
    USER_DATA_FILE.insert_one(data)

def load_reset_tokens():
    return list(RESET_TOKENS_FILE.find())

def save_reset_tokens(data):
    RESET_TOKENS_FILE.insert_one(data)

def send_reset_email(user_email, token):
    # Send email implementation
    pass

def validate_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email)

def validate_password(password):
    password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(password_pattern, password)


st.markdown("""
<style>
    body {
        background-color: #f0f0f0;
    }
    .main {
        max-width: 800px;
        margin: 40px auto;
        padding: 20px;
        background-color: #659;
        border: 1px solid #fff;
        border-radius: 15px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    }
    .header {
        background-color: #3df;
        color: #fcc;
        padding: 10px;
        text-align: center;
    }
    .header h1 {
        margin: 0;
    }
    .form {
        padding: 20px;
    }
    .form label {
        display: block;
        margin-bottom: 10px;
    }
    .form input[type="text"], .form input[type="password"] {
        width: 100%;
        padding: 10px;
        margin-bottom: 20px;
        border: 2px solid #ccc;
    }
    .form button[type="submit"] {
        background-color: #4CAF50;
        color: #fff;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .form button[type="submit"]:hover {
        background-color: #3e8e41;
    }
</style>
""", unsafe_allow_html=True)

def signup():
    st.title("Sign Up")
    with st.form("signup_form"):
        username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        if st.form_submit_button("Sign Up"):
            # Validate user input
            if not validate_email(email):
                st.error("Invalid email address.")
            elif not validate_password(password):
                st.error("Password must be at least 8 characters, contain one digit, one uppercase letter, and one special character.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif email in load_user_data():
                st.error("Email address already in use.")
            else:
                hashed_password = hash_password(password)
                user_data = {"username": username, "email": email, "password": hashed_password}
                save_user_data(user_data)
                st.session_state['redirect_to_signin'] = True
                st.success("Account created successfully!")


def login():
    st.title("Log In")
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.form_submit_button("Log In"):
            user_data = load_user_data()
            hashed_password = hash_password(password)
            for user in user_data:
                if user["email"] == email and user["password"] == hashed_password:
                    st.success(f"Welcome back, {user['username']}!")
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user['username']
                    break
            else:
                st.error("Invalid email address or password.")


def reset_password():
    st.title("Reset Password")
    with st.form("reset_form"):
        email = st.text_input("Enter your email to reset your password", key="reset_email")
        if st.form_submit_button("Send Reset Link"):
            user_data = load_user_data()
            if email not in user_data:
                st.error("Invalid email address.")
            else:
                token = str(uuid.uuid4())
                reset_tokens = load_reset_tokens()
                reset_tokens[token] = email
                save_reset_tokens(reset_tokens)
                if send_reset_email(email, token):
                    st.success("Reset link sent to your email address.")


def reset_password_confirm():
    st.title("Reset Password Confirmation")
    if 'token' in st.query_params and 'email' in st.query_params:
        token = int(st.query_params['token'])
        email = int(st.query_params['email'])
    if isinstance(token, list):
        token = tuple(token)
    
    if token and email and token in load_reset_tokens() and load_reset_tokens()[token] == email:
        with st.form("reset_confirm_form"):
            password = st.text_input("New Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password")

            if st.form_submit_button("Reset Password"):
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    user_data = load_user_data()
                    hashed_password = hash_password(password)

                    if email in user_data:
                        user_data[email]['password'] = hashed_password
                        save_user_data(user_data)
                        reset_tokens = load_reset_tokens()
                        del reset_tokens[token]
                        save_reset_tokens(reset_tokens)
                        st.success("Password reset successfully!")


def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["email"] = ""
    st.rerun()



if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if 'redirect_to_signin' in st.session_state and st.session_state['redirect_to_signin']:
    st.session_state['redirect_to_signin'] = False
    st.rerun()
if st.session_state["logged_in"]:
    st.sidebar.write(f"Welcome, {st.session_state['username']}!")
    choice = st.sidebar.radio("Navigate", ["Dashboard", "Account", "Analysis", "Logout"])
    if choice == "Dashboard":
        # Load dashboard page
        st.write("This is the Dashboard page.")
    elif choice == "Account":
        # Load account settings page
        st.write("This is the Account page.")
    elif choice == "Analysis":
        # Load analysis page
        st.write("This is the Analysis page.")
    elif choice == "Logout":
        logout()
else:
    tabs = st.tabs(["Sign In", "Sign Up", "Reset Password"])
    # Display the content based on the selected tab
    with tabs[0]:
        login()
    with tabs[1]:
        signup()
    with tabs[2]:
        reset_password()


st.markdown("""
<footer>
    <p>&copy; 2024 Stock Price Prediction WebApp</p>
</footer>
""", unsafe_allow_html=True)
