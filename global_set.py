import streamlit as st
import warnings
import os
import uuid
import random
from google.cloud import storage
import pandas as pd
from datetime import datetime
import json
import bcrypt
import pytz
import io  # Import for handling in-memory strings
import vertexai

# ----------------------------- Utility Functions ----------------------------- #

def get_bangkok_time():
    """Get current time in Bangkok timezone"""
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    utc_now = datetime.now(pytz.UTC)  # Get current UTC time
    return utc_now.astimezone(bangkok_tz)  # Convert to Bangkok time

def initialize_vertex_ai():
    """Initialize Vertex AI using credentials from Streamlit secrets."""
    try:
        vertexai.init(
            project=st.secrets["api"]["vertexai_project"],
            location="asia-southeast1"
        )
        st.success("Vertex AI initialized successfully")
    except Exception as e:
        st.error(f"Failed to initialize Vertex AI: {e}")

# ----------------------------- GCS Initialization ----------------------------- #

def initialize_gcs():
    """Initialize Google Cloud Storage using credentials from Streamlit secrets."""
    try:
        credentials = {
            "type": st.secrets["gcs"]["type"],
            "project_id": st.secrets["gcs"]["project_id"],
            "private_key_id": st.secrets["gcs"]["private_key_id"],
            "private_key": st.secrets["gcs"]["private_key"],
            "client_email": st.secrets["gcs"]["client_email"],
            "client_id": st.secrets["gcs"]["client_id"],
            "auth_uri": st.secrets["gcs"]["auth_uri"],
            "token_uri": st.secrets["gcs"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcs"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcs"]["client_x509_cert_url"]
        }

        client = storage.Client.from_service_account_info(credentials)
        bucket = client.bucket(st.secrets["gcs"]["bucket_name"])
        return bucket
    except Exception as e:
        st.error(f"Failed to initialize GCS: {e}")
        return None

# ----------------------------- App Functions ----------------------------- #

def fetch_tarot_data():
    """Fetch tarot data from Google Cloud Storage."""
    try:
        bucket = initialize_gcs()
        if not bucket:
            raise Exception("Failed to initialize GCS bucket.")

        blob = bucket.blob("cards/023_cleaned_all_tarot_card_data.csv")
        data = blob.download_as_text()  # Get the CSV data as a string

        df = pd.read_csv(io.StringIO(data))  # Use io.StringIO to convert string to DataFrame
        return df
    except Exception as e:
        st.error(f"Unable to load tarot card data: {e}")
        return None

def save_reading_log(user_input, reading_type, cards_drawn, predictions):
    """Save tarot reading log to Google Cloud Storage"""
    try:
        bucket = initialize_gcs()
        if not bucket:
            raise Exception("Failed to initialize GCS bucket.")

        bangkok_time = get_bangkok_time()
        bangkok_timestamp = bangkok_time.strftime('%Y-%m-%d %H:%M:%S')  # Format time as string

        user_id = st.session_state.get('user_id', 'anonymous')
        session_start = st.session_state.get('session_start', bangkok_timestamp)

        log_entry = {
            "user_id": user_id,
            "session_start": session_start,
            "reading_timestamp": bangkok_timestamp,
            "reading_type": reading_type,
            "user_input": user_input,
            "cards": cards_drawn,
            "predictions": predictions,
            "session_id": str(uuid.uuid4())
        }

        filename = f"user_logs/{user_id}/{reading_type}/{bangkok_time.strftime('%Y/%m/%d')}/{log_entry['session_id']}.json"
        blob = bucket.blob(filename)
        blob.upload_from_string(
            data=json.dumps(log_entry, ensure_ascii=False),
            content_type='application/json'
        )
    except Exception as e:
        st.error(f"Error saving reading log: {e}")

def verify_user(bucket, username, password):
    """Verify user credentials against stored data."""
    try:
        blobs = bucket.list_blobs(prefix="users/")
        for blob in blobs:
            user_data = json.loads(blob.download_as_text())
            if user_data.get("username") == username:
                stored_password = user_data.get("password").encode("utf-8")
                if bcrypt.checkpw(password.encode("utf-8"), stored_password):
                    return user_data
    except Exception as e:
        st.error(f"Error verifying user: {e}")
    return None

# ----------------------------- UI Components ----------------------------- #

def logo():
    st.set_page_config(
        page_title="Lucky Tarot",
        page_icon="assets/logo.png"
    )
    st.image("assets/logo.png", width=300)
    st.markdown("""
        <style>
        .stSidebar { display: none; }
        </style>
    """, unsafe_allow_html=True)

def ohm():
    st.write("#### Before asking a question, focus on your belief system or recite a prayer")
    st.write("##### ॐ Om Shri Ganeshaya Namaha ॐ")

def focus(set):
    st.markdown("#### ॐ Om Shri Ganeshaya Namaha ॐ")
    if set == 'no input':
        st.success("Focus your mind, take a deep breath, and press the Predict button.")
    else:
        st.success("Focus your mind, take a deep breath, type your question, and press the Predict button.")

def survey():
    st.button(
        label="Take our survey",
        url="https://forms.gle/R6uCm9oEdkfb4ogAA",
        use_container_width=True
    )

def end_predict():
    st.success("Prediction complete")
