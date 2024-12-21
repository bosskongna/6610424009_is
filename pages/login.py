import streamlit as st
import json
import bcrypt
from google.cloud import storage
import subprocess
import os
import global_set as gb

gb.logo()

def initialize_gcs():
    try:
        client = storage.Client.from_service_account_json("/workspaces/6610424009_is/assets/mutelu-worldth-4019e9927759.json")
        bucket = client.bucket("mutelu_bucket")
        return bucket
    except Exception as e:
        st.error(f"Failed to initialize Google Cloud Storage: {str(e)}")
        return None

def verify_user(bucket, username, password):
    """Verify user credentials against stored data"""
    if bucket is None:
        return None
        
    blobs = bucket.list_blobs(prefix="users/")
    for blob in blobs:
        try:
            user_data = json.loads(blob.download_as_text())
            if user_data.get("username") == username:
                # Verify password
                stored_password = user_data.get("password").encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    return user_data
        except json.JSONDecodeError:
            continue
        except Exception as e:
            st.error(f"Error verifying user: {str(e)}")
    return None

def main():
    st.title("เข้าสู่ระบบ (Login)")
    
    # Initialize session state for login status if not exists
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_data = None

    # Login Form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if not username or not password:
                st.error("Please enter both username and password.")
                return

            bucket = initialize_gcs()
            if bucket:
                user_data = verify_user(bucket, username, password)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user_data
                    st.success("Login successful! 🎉")
                    
                    # Save user data to a temporary file that pages/streamlit_app.py can read
                    with open('user_session.json', 'w') as f:
                        json.dump(user_data, f)
                    
                    # Redirect to pages/streamlit_app.py
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    home_path = os.path.join(current_dir, 'pages/streamlit_app.py')
                    
                    if os.path.exists(home_path):
                        st.switch_page("pages/streamlit_app.py")
                    else:
                        st.error(f"Could not find pages/streamlit_app.py. Expected path: {home_path}")
                else:
                    st.error("Invalid username or password.")

    # Registration Link
    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("Sign Up"):
        st.switch_page("pages/register.py")
        st.experimental_rerun()

if __name__ == "__main__":
    main()