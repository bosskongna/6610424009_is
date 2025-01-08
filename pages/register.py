# import streamlit as st
# import datetime
# import json
# import uuid
# from google.cloud import storage
# import bcrypt
# import global_set as gb


# # Google Cloud Storage Setup

# gb.initialize_vertexai()  # Initialize Vertex
# bucket = gb.initialize_gcs()  # Initialize GC AI

# # Utility Functions
# def add_user(bucket, email, password, name, last_name, birth_date, membership_type):
#     """Add a new user to GCS"""
#     # Generate a unique User ID
#     user_id = str(uuid.uuid4())

#     # Hash the password
#     hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

#     # Prepare user data
#     user_data = {
#         "user_id": user_id,
#         "username": username,
#         "email": email,
#         "password": hashed_password,  # Store hashed password
#         "name": name,
#         "last_name": last_name,
#         "birth_date": birth_date,
#         "membership_type": membership_type,  # Store selected membership type
#         "created_at": datetime.datetime.now().isoformat(),
#     }

#     # Save to GCS
#     blob = bucket.blob(f"users/{user_id}.json")
#     blob.upload_from_string(json.dumps(user_data), content_type="application/json")
#     st.success(f"User {username} added successfully with ID: {user_id}")


# def is_unique_user(bucket, username, email):
#     """Check if username or email is already taken"""
#     blobs = list(bucket.list_blobs(prefix="users/"))  # List all user files

#     # If there are no files in the `users/` folder, return unique
#     if not blobs:
#         return True, ""

#     for blob in blobs:
#         try:
#             user_data = json.loads(blob.download_as_text())  # Attempt to decode JSON
#             if user_data.get("username") == username:
#                 return False, "Username already exists."
#             if user_data.get("email") == email:
#                 return False, "Email already exists."
#         except json.JSONDecodeError:
#             st.warning(f"Skipped invalid or empty file: {blob.name}")
#             continue
#     return True, ""


# def list_users(bucket):
#     """List all users (for debugging)"""
#     blobs = bucket.list_blobs(prefix="users/")
#     users = []
#     for blob in blobs:
#         try:
#             user_data = json.loads(blob.download_as_text())
#             users.append(user_data)
#         except json.JSONDecodeError:
#             st.warning(f"Skipped invalid or empty file: {blob.name}")
#             continue
#     return users


# # Streamlit App
# st.title("สมัครสมาชิก (Sign Up)")
# if st.button("< Back to login"):
#     st.switch_page("pages/login.py")
#     st.experimental_rerun()
# # Registration Form
# with st.form("registration_form"):
#     st.subheader("Sign Up")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     confirm_password = st.text_input("Confirm Password", type="password")
#     email = st.text_input("Email")
#     name = st.text_input("ชื่อจริง")
#     last_name = st.text_input("นามสกุล")
#     birth_date = st.date_input(label="วัน เดือน ปี เกิด (ค.ศ.)", min_value=datetime.date(1900, 1, 1))
#     st.text("สำหรับบุคคลทั่วไป เลือก Non-MADT")
#     membership_type = st.selectbox("Membership Type", ["MADT3", "MADT", "Non-MADT"])
#     submit_button = st.form_submit_button("Register")

# if submit_button:
#     # Validate form inputs
#     is_unique, error_message = is_unique_user(bucket, username, email)
#     if not is_unique:
#         st.error(error_message)
#     elif password != confirm_password:
#         st.error("Passwords do not match. Please try again.")
#     elif password == "":
#         st.warning("Password cannot be empty.")
#     else:
#         add_user(bucket, username, email, password, name, last_name, str(birth_date), membership_type)
#         st.success(f"Registration successful! Welcome, {username} 🎉")

# # # Show all users (Debugging)
# # if st.checkbox("Show All Users (Debug)"):
# #     users = list_users(bucket)
# #     st.json(users)\


import streamlit as st
from datetime import datetime
import json
import uuid
from google.cloud import storage
import bcrypt
import global_set as gb



# Google Cloud Storage Setup

gb.logo()
gb.initialize_vertexai()  # Initialize Vertex
bucket = gb.initialize_gcs()  # Initialize GC AI

# Utility Functions
def add_user(bucket, email, membership_type):
    """Add a new user to GCS"""
    # Generate a unique User ID
    user_id = str(uuid.uuid4())

    # Hash the password
    # hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Prepare user data
    user_data = {
        "user_id": user_id,
        # "username": username,
        "email": email,
        # "password": hashed_password,  # Store hashed password
        # "name": name,
        # "last_name": last_name,
        # "birth_date": birth_date,
        "membership_type": membership_type,  # Store selected membership type
        "created_at": datetime.now().isoformat(),
    }

    # Save to GCS
    blob = bucket.blob(f"users/{user_id}.json")
    blob.upload_from_string(json.dumps(user_data), content_type="application/json")
    st.success(f"User {email} added successfully with ID: {user_id}")


def is_unique_user(bucket, email):
    """Check if username or email is already taken"""
    blobs = list(bucket.list_blobs(prefix="users/"))  # List all user files

    # If there are no files in the `users/` folder, return unique
    if not blobs:
        return True, ""

    for blob in blobs:
        try:
            user_data = json.loads(blob.download_as_text())  # Attempt to decode JSON
            # if user_data.get("username") == username:
            #     return False, "Username already exists."
            if user_data.get("email") == email:
                return False, "Email already exists."
        except json.JSONDecodeError:
            # st.warning(f"Skipped invalid or empty file: {blob.name}")
            continue
    return True, ""


def list_users(bucket):
    """List all users (for debugging)"""
    blobs = bucket.list_blobs(prefix="users/")
    users = []
    for blob in blobs:
        try:
            user_data = json.loads(blob.download_as_text())
            users.append(user_data)
        except json.JSONDecodeError:
            st.warning(f"Skipped invalid or empty file: {blob.name}")
            continue
    return users


# Streamlit App
st.title("สมัครสมาชิก (Sign Up)")
if st.button("< Back to login"):
    st.switch_page("pages/login.py")
    st.experimental_rerun()
# Registration Form
with st.form("registration_form"):
    st.subheader("Sign Up")
    # username = st.text_input("Username")
    # password = st.text_input("Password", type="password")
    # confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email")
    # name = st.text_input("ชื่อจริง")
    # last_name = st.text_input("นามสกุล")
    # birth_date = st.date_input(label="วัน เดือน ปี เกิด (ค.ศ.)", min_value=datetime.date(1900, 1, 1))
    st.text("สำหรับบุคคลทั่วไป เลือก Non-MADT")
    membership_type = st.selectbox("Membership Type", ["MADT3", "MADT", "Non-MADT"])
    submit_button = st.form_submit_button("Register")

if submit_button:
    # Validate form inputs
    is_unique, error_message = is_unique_user(bucket, email)
    if not is_unique:
        st.error(error_message)
    else:
        add_user(bucket, email,  membership_type)
        if bucket:
            st.success(f"Registration successful! Welcome, {email} 🎉")
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

# # Show all users (Debugging)
# if st.checkbox("Show All Users (Debug)"):
#     users = list_users(bucket)
#     st.json(users)