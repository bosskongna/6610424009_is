import streamlit as st
import json
import bcrypt
from datetime import datetime
import sys
import os
import uuid

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import global_set as gb

def add_user(bucket,email, password, membership_type):
    """Add a new user to GCS"""
    # Generate a unique User ID
    user_id = str(uuid.uuid4())

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Prepare user data
    user_data = {
        "user_id": user_id,
        "email": email,
        "membership_type" : membership_type
    }

    # Save to GCS
    blob = bucket.blob(f"users/{user_id}.json")
    blob.upload_from_string(json.dumps(user_data), content_type="application/json")
    st.success(f"User {email} added successfully with ID: {user_id}")



gb.logo()
def main():
    st.title("เข้าสู่ระบบ (Login)")

    # Initialize both services at once
    bucket, services_initialized = gb.initialize_services()
    
    if not services_initialized:
        st.error("Failed to initialize required services")
        return

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_data = None
        st.session_state.user_id = None
        st.session_state.session_start = None

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your.email@example.com")
        # password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if not email or '@' not in email:
                st.error("กรุณากรอก Email ให้ถูกต้อง")
                return
            try:
                if bucket:
                    user_data = gb.verify_user(bucket, email)
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.user_data = user_data
                        st.session_state.user_id = user_data.get('user_id')
                        st.session_state.session_start = datetime.now().isoformat()
                        st.success("Login successful! 🎉")

                        with open('user_session.json', 'w') as f:
                            json.dump(user_data, f)

                        st.switch_page("pages/streamlit_app.py")
                    else:
                        st.error(f"Please register")
            except Exception as e:
                st.error(f"Login error: {str(e)}")
                print(f"Detailed error: {e}")

    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("Sign Up"):
        st.switch_page("pages/register.py")

if __name__ == "__main__":
    main()

# import streamlit as st

# def test_deploy_secrets():
#     try:
#         creds = st.secrets["mutelu_worldth"]
#         required_fields = ["type", "project_id", "private_key_id", "private_key", 
#                          "client_email", "client_id", "auth_uri", "token_uri",
#                          "auth_provider_x509_cert_url", "client_x509_cert_url"]
        
#         missing = [f for f in required_fields if f not in creds]
#         if missing:
#             st.error(f"Missing fields: {', '.join(missing)}")
#             return
            
#         st.success("All required fields present")
        
#         # Check private key format
#         key = creds["private_key"]
#         if "BEGIN PRIVATE KEY" in key and "END PRIVATE KEY" in key:
#             st.success("Private key format appears correct")
#         else:
#             st.error("Private key format incorrect")

#     except Exception as e:
#         st.error(f"Error: {str(e)}")

# test_deploy_secrets()