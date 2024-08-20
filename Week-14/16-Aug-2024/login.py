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
    password_pattern = r'^(?=.[A-Z])(?=.\d)(?=.[@$!%?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(password_pattern, password)
# Signup Page
def signup():
    st.title("Sign Up")
    username = st.text_input("Username", key="signup_username")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    if username and email:
        if st.button("Sign Up", key="signup_button"):
            user_data = load_user_data()
            if not validate_email(email):
                st.error("Invalid email address.")
            elif not validate_password(password):
                st.error("Password must be at least 8 characters long, include one digit, one uppercase letter, and one special character.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif email in user_data:
                st.error("Email already registered.")
            else:
                hashed_password = hash_password(password)
                user_data[email] = {"username": username, "password": hashed_password}
                save_user_data(user_data)
                st.success("Sign up successful! You can now log in.")
                st.session_state['redirect_to_signin']==True
        else :
            st.error("Please enter the required fields")
# Sign In Page
def signin():
    st.title("Sign In")
    email = st.text_input("Email", key="signin_email")
    password = st.text_input("Password", type="password", key="signin_password")
    if email:
        if st.button("Sign In", key="signin_button"):
            user_data = load_user_data()
            hashed_password = hash_password(password)
            if email in user_data and user_data[email]["password"] == hashed_password:
                st.success(f"Welcome back, {user_data[email]['username']}!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = user_data[email]['username']
            else:
                st.error("Invalid email or password.")

    
 
# Reset Password Page
def reset_password():
    st.subheader("Forgot Password?")
    reset_email = st.text_input("Enter your email to reset your password", key="reset_email")
    if reset_email:
        if st.button("Send Reset Link", key="send_reset_link"):
            if reset_email:
                user_data = load_user_data()
                if reset_email in user_data:
                    token = str(uuid.uuid4())
                    reset_tokens = load_reset_tokens()
                    reset_tokens[token] = reset_email
                    save_reset_tokens(reset_tokens)
                    if send_reset_email(reset_email, token):
                        st.success("A password reset link has been sent to your email.")
                else:
                    st.error("Email not registered.")
            else:
                st.error("Please enter an email address.")

    # Check for token and email in the query parameters
    # query_params = st.experimental_get_query_params()
    
    token = st.query_params.get('token', [None])
    email = st.query_params.get('email', [None])
    
    if isinstance(token, list):
        token = tuple(token)
    
    if token and email and token in load_reset_tokens() and load_reset_tokens()[token] == email:
        st.success("Please change the password and confirm!")
        st.title("Reset Password")
        new_password = st.text_input("New Password", type="password", key="new_password")
        confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password")

        if st.button("Reset Password", key="reset_password_button"):
            if new_password != confirm_new_password:
                st.error("Passwords do not match.")
            else:
                user_data = load_user_data()
                hashed_password = hash_password(new_password)

                if email in user_data:
                    user_data[email]["password"] = hashed_password
                    save_user_data(user_data)
                    st.success("Password has been reset. You can now log in.")
                    reset_tokens = load_reset_tokens()
                    del reset_tokens[token]
                    save_reset_tokens(reset_tokens)
    else:
        st.warning("Please enter the Email or check the email for the reset link .")

# Logout Function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.experimental_rerun()

# Main Function with Navigation
def main():
    st.sidebar.title("Navigation")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        st.sidebar.write(f"Welcome, {st.session_state['username']}!")
        choice = st.sidebar.radio("Navigate", ["Dashboard", "Account", "Analysis", "Logout"])

        if choice == "Dashboard":
            import dashboard
            # Load dashboard page
            st.write("This is the Dashboard page.")

        elif choice == "Account":
            import Aboutpage
            # Load account settings page
            st.write("This is the Account page.")

        elif choice == "Analysis":
            import analysis
            # Load analysis page
            st.write("This is the Analysis page.")

        elif choice == "Logout":
            logout()

    else:
        tabs = st.tabs(["Sign In", "Sign Up", "Reset Password"])

        # Display the content based on the selected tab
        with tabs[0]:
            signin()
        with tabs[1]:
            signup()
        with tabs[2]:
            reset_password()
            

if __name__ == "__main__":
    main()