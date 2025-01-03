import streamlit as st
import warnings
import os
import uuid
import random
from google.cloud import storage
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime
import json
import bcrypt
import pytz
import vertexai
import io
import tempfile  # Import the full tempfile module
from google.api_core import exceptions

def get_bangkok_time():
    """Get current time in Bangkok timezone"""
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    utc_now = datetime.now(pytz.UTC)  # Get current UTC time
    bangkok_time = utc_now.astimezone(bangkok_tz)  # Convert to Bangkok time
    return bangkok_time

def button_main_page():
    if st.button("ย้อนกลับ"):
        st.switch_page("pages/streamlit_app.py")

def button_under_page():
    if st.button("กลับ"):
        st.switch_page("pages/streamlit_app.py")

def format_key_for_deployment(key):
    """Ensure private key is properly formatted"""
    clean_key = key.strip()
    if not clean_key.startswith('-----BEGIN PRIVATE KEY-----'):
        clean_key = '-----BEGIN PRIVATE KEY-----\n' + clean_key
    if not clean_key.endswith('-----END PRIVATE KEY-----'):
        clean_key = clean_key + '\n-----END PRIVATE KEY-----'
    return clean_key

def initialize_services():
    """Initialize all required Google Cloud services."""
    try:
        credentials_info = dict(st.secrets["mutelu_chat"])  # Use mutelu_chat for Vertex AI
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Initialize storage with mutelu_worldth
        storage_info = dict(st.secrets["mutelu_worldth"])
        storage_credentials = service_account.Credentials.from_service_account_info(storage_info)
        storage_client = storage.Client(credentials=storage_credentials)
        bucket = storage_client.bucket("mutelu_bucket")
        
        # Initialize Vertex AI with mutelu_chat
        vertexai.init(
            project=credentials_info["project_id"],
            location="asia-southeast1",
            credentials=credentials
        )
        
        return bucket, True
        
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, False

def initialize_gcs():
    bucket, _ = initialize_services()
    return bucket

def initialize_vertexai():
    _, success = initialize_services()
    return success
# def api_key():
#     """
#     Retrieves the Gemini API key and initializes GCS and Vertex AI.

#     Returns:
#         dict: A dictionary containing the API key, GCS bucket object, and a
#               boolean indicating successful Vertex AI initialization.
#               Returns None if any error occurs.
#     """
#     try:
#         gemini_api_key = st.secrets["api"]["gemini_api_key"]

#         # Initialize GCS
#         gcs_creds = {
#             "type": st.secrets["mutelu-worldth"]["type"],
#             "project_id": st.secrets["mutelu-worldth"]["project_id"],
#             "private_key_id": st.secrets["mutelu-worldth"]["private_key_id"],
#             "private_key": st.secrets["mutelu-worldth"]["private_key"],
#             "client_email": st.secrets["mutelu-worldth"]["client_email"],
#             "client_id": st.secrets["mutelu-worldth"]["client_id"],
#             "auth_uri": st.secrets["mutelu-worldth"]["auth_uri"],
#             "token_uri": st.secrets["mutelu-worldth"]["token_uri"],
#             "auth_provider_x509_cert_url": st.secrets["mutelu-worldth"]["auth_provider_x509_cert_url"],
#             "client_x509_cert_url": st.secrets["mutelu-worldth"]["client_x509_cert_url"],
#             "universe_domain": st.secrets["mutelu-worldth"]["universe_domain"],
#         }
#         client = storage.Client.from_service_account_info(gcs_creds)
#         bucket = client.bucket("mutelu_bucket")

#         # Initialize Vertex AI
#         vertexai_creds = {
#             "type": st.secrets["mutelu-chat"]["type"],
#             "project_id": st.secrets["mutelu-chat"]["project_id"],
#             "private_key_id": st.secrets["mutelu-chat"]["private_key_id"],
#             "private_key": st.secrets["mutelu-chat"]["private_key"],
#             "client_email": st.secrets["mutelu-chat"]["client_email"],
#             "client_id": st.secrets["mutelu-chat"]["client_id"],
#             "auth_uri": st.secrets["mutelu-chat"]["auth_uri"],
#             "token_uri": st.secrets["mutelu-chat"]["token_uri"],
#             "auth_provider_x509_cert_url": st.secrets["mutelu-chat"]["auth_provider_x509_cert_url"],
#             "client_x509_cert_url": st.secrets["mutelu-chat"]["client_x509_cert_url"],
#             "universe_domain": st.secrets["mutelu-chat"]["universe_domain"],
#         }

#         vertexai.init(
#             project=vertexai_creds["project_id"],
#             location="asia-southeast1",
#             credentials=service_account.Credentials.from_service_account_info(vertexai_creds)
#         )

#         return {
#             "gemini_api_key": gemini_api_key,
#             "gcs_bucket": bucket,
#             "vertexai_initialized": True
#         }

#     except FileNotFoundError:
#         st.error("Failed to find service account key file.")
#         return None
#     except Exception as e:
#         st.error(f"Unable to access API key or initialize services: {e}")
#         return None



def ohm():
    st.write("#### ก่อนถามคำถามให้ระลึกถึงสิ่งศักดิ์สิทธิ์ที่ตนเองนับถือ หรือ ท่องบทบูชาพระพิฆเนศ 1 จบ")
    st.write("##### ॐ โอม ศรีคเณศายะ นะมะฮา ॐ")

def focus(set):
    st.markdown("#### ॐ โอม ศรีคเณศายะ นะมะฮา ॐ")
    if set == 'no input':
        st.success("ตั้งสมาธิ หายใจเข้าลึกๆ แล้วกดปุ่ม ทำนายดวง")
    else:
        st.success("ตั้งสมาธิ หายใจเข้าลึกๆ พิมพ์คำถาม แล้วกดปุ่ม ทำนายดวง")

# def fetch_local_tarot_data():
#     """Fetch tarot data from local CSV file."""
#     try:
#         df = pd.read_csv("/workspaces/6610424009_is/023_cleaned_all_tarot_card_data.csv")
#         return df
#     except Exception as e:
#         st.error(f"ไม่สามารถโหลดข้อมูลไพ่ทาโรต์ได้: {e}")
#         return None
# import io  # Import the StringIO module

def fetch_local_tarot_data():
    """Fetch tarot data from Google Cloud Storage."""
    try:
        # Get storage credentials
        # credentials_info = dict(st.secrets["mutelu_worldth"])
        # credentials = service_account.Credentials.from_service_account_info(
        #     credentials_info,
        #     scopes=['https://www.googleapis.com/auth/cloud-platform']
        # )
        
        # Initialize storage client
        # storage_client = storage.Client(credentials=credentials)
        # bucket = storage_client.bucket("mutelu-worldth.appspot.com")
        
        # Get the CSV file
        # blob = bucket.blob("pages/023_cleaned_all_tarot_card_data.csv")
        # data = blob.download_as_text()
        data = 'pages/023_cleaned_all_tarot_card_data.csv'
        return pd.read_csv(data)
        
    except Exception as e:
        st.error(f"Unable to load tarot card data: {e}")
        return None

def survey():
    st.link_button(
        label="แบบสำรวจการใช้งาน",
        url="https://forms.gle/R6uCm9oEdkfb4ogAA",
        type="primary",
        use_container_width=True
    )

def end_predict():
    st.success("สิ้นสุดคำทำนาย")


def save_reading_log(user_input, reading_type, cards_drawn, predictions, bucket_name="mutelu_bucket"):
    """Save tarot reading log to Google Cloud Storage"""
    try:
        # Get storage credentials
        credentials_info = dict(st.secrets["mutelu_worldth"])
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Initialize storage client
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket("mutelu_bucket")

        # Get Bangkok time
        bangkok_time = get_bangkok_time()
        bangkok_timestamp = bangkok_time.strftime('%Y-%m-%d %H:%M:%S')

        user_id = st.session_state.get('user_id', 'anonymous')
        session_start = st.session_state.get('session_start', bangkok_timestamp)
        log_entry = {
            "user_id": user_id,
            "session_start": session_start,
            "reading_timestamp": bangkok_timestamp,
            "reading_type": reading_type,
            "user_input": user_input,
            "cards": {
                "positions": {},
                "card_numbers": []
            },
            "predictions": predictions,
            "session_id": str(uuid.uuid4())
        }

        # Add cards based on reading type
        if reading_type == "daily":
            log_entry["cards"]["positions"] = {
                "daily_card": cards_drawn
            }
        else:
            log_entry["cards"]["positions"] = cards_drawn

        bangkok_date = bangkok_time.strftime('%Y/%m/%d')
        filename = f"user_logs/{user_id}/{reading_type}/{bangkok_date}/{log_entry['session_id']}.json"
        
        blob = bucket.blob(filename)
        blob.upload_from_string(
            data=json.dumps(log_entry, ensure_ascii=False),
            content_type='application/json'
        )

    except Exception as e:
        st.error(f"Error saving reading log: {e}")

def verify_user(bucket, email):
    """Verify user by email."""
    if bucket is None:
        return None

    blobs = bucket.list_blobs(prefix="users/")
    for blob in blobs:
        try:
            user_data = json.loads(blob.download_as_text())
            if user_data.get("email") == email:
                return user_data
        except json.JSONDecodeError:
            continue
        except Exception as e:
            st.error(f"Error verifying user: {str(e)}")
    return None


def logo():
    st.set_page_config(
        page_title="Lucky Tarot",
        page_icon='assets/logo.png'
        )
    st.image("assets/logo.png", width=300)
    
    st.markdown("""
        <style>
        .stSidebar {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)
