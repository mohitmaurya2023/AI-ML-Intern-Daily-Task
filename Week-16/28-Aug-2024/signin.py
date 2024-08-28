import streamlit as st
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uuid
import json
import re

# Load environment variables
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# File for storing user data
USER_DATA_FILE = 'users.json'
RESET_TOKENS_FILE = 'reset_tokens.json'

# Utility Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f)

def load_reset_tokens():
    if os.path.exists(RESET_TOKENS_FILE):
        with open(RESET_TOKENS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_reset_tokens(data):
    with open(RESET_TOKENS_FILE, 'w') as f:
        json.dump(data, f)

def send_reset_email(user_email, token):
    sender_email = "mohitkmourya@gmail.com"
    sender_password = 'gavo mgvo eqyf joke'
    receiver_email = user_email


    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Password Reset Request'

    reset_link = f"http://localhost:8501/?token={token}&email={user_email}"
    body = f"Hi,\n\nClick the link below to reset your password:\n{reset_link}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def validate_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email)

def validate_password(password):
    # Password validation: at least 8 characters, one digit, one uppercase letter, and one special character
    password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(password_pattern, password)

# Custom CSS for the app
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

# Signup Page
def signup():
    st.title("Sign Up")
    with st.form("signup_form"):
        username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        if username and email:
            if st.form_submit_button("Sign Up", key="signup_button"):
                user_data = load_user_data()
                if not validate_email(email):
                    st.error("Invalid email address.")
                elif not validate_password(password):
                    st.error("Password must be at least 8 characters, contain one digit, one uppercase letter, and one special character.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif email in user_data:
                    st.error("Email address already in use.")
                else:
                    hashed_password = hash_password(password)
                    user_data[email] = {"username": username, "password": hashed_password}
                    save_user_data(user_data)
                    st.session_state['redirect_to_signin'] = True
                    st.success("Account created successfully!")
            else:
                st.error("Please enter the required fields")

# Login Page
def login():
    st.title("Log In")
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if email:
            if st.form_submit_button("Log In", key="login_button"):
                user_data = load_user_data()
                hashed_password = hash_password(password)
                if email in user_data and user_data[email]["password"] == hashed_password:
                    st.success(f"Welcome back, {user_data[email]['username']}!")
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user_data[email]['username']
                else:
                    st.error("Invalid email address or password.")
            else:
                st.success("Logged in successfully!")

# Reset Password Page
def reset_password():
        st.title("Reset Password")
        with st.form("reset_form"):
            email = st.text_input("Enter your email to reset your password", key="reset_email")
            if email:
                if st.form_submit_button("Send Reset Link", key="send_reset_link"):
                    if email:
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
                #     else:
                #         st.error("Please enter your email address.")
                # else:
                #     st.success("Reset link sent to your email address.")

    # Reset Password Confirmation Page
def reset_password_confirm():
    st.title("Reset Password Confirmation")
    token = st.query_params.get('token', [None])
    email = st.query_params.get('email', [None])
    
    if isinstance(token, list):
        token = tuple(token)
    
    if token and email and token in load_reset_tokens() and load_reset_tokens()[token] == email:
        with st.form("reset_confirm_form"):
            password = st.text_input("New Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password")

            if st.form_submit_button("Reset Password", key="reset_password_button"):
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

# Main App
st.title("StockAI")

pages = {
    "Sign Up": signup,
    "Log In": login,
    "Reset Password": reset_password
}

page = st.sidebar.selectbox("Page", list(pages.keys()))

if page == "Reset Password":
    if 'token' in st.experimental_get_query_params() and 'email' in st.experimental_get_query_params():
        st.session_state.token = st.experimental_get_query_params()['token'][0]
        st.session_state.email = st.experimental_get_query_params()['email'][0]
        reset_password_confirm()
    else:
        reset_password()
else:
    pages[page]()
    # Main App
st.title("StockAI")

pages = {
    "Sign Up": signup,
    "Log In": login,
    "Reset Password": reset_password
}

page = st.sidebar.selectbox("Page", list(pages.keys()))

if page == "Reset Password":
    if 'token' in st.experimental_get_query_params() and 'email' in st.experimental_get_query_params():
        st.session_state.token = st.experimental_get_query_params()['token'][0]
        st.session_state.email = st.experimental_get_query_params()['email'][0]
        reset_password_confirm()
    else:
        reset_password()
else:
    pages[page]()

# Footer
st.markdown("""
<footer>
    <p>&copy; 2023 Authentication App</p>
</footer>
""", unsafe_allow_html=True)