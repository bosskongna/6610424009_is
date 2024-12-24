import streamlit as st
import json
import bcrypt
import global_set as gb
from datetime import datetime

gb.logo()

def main():
    st.title("เข้าสู่ระบบ (Login)")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_data = None
        st.session_state.user_id = None
        st.session_state.session_start = None

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if not username or not password:
                st.error("Please enter both username and password.")
                return

            bucket = gb.initialize_gcs()
            if bucket:
                user_data = gb.verify_user(bucket, username, password)
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
                    st.error("Invalid username or password.")

    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("Sign Up"):
        st.switch_page("pages/register.py")

if __name__ == "__main__":
    main()