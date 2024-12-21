import streamlit as st
import warnings
import os
import uuid
import random
from google.cloud import storage
import pandas as pd

def logo():
    # Access the API key
    gemini_api_key = st.secrets["api"]["gemini_api_key"]
    # st.write(f"Gemini API Key: {gemini_api_key}")
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

def ohm():
    st.write("#### ॐ โอม ศรีคเณศายะ นะมะฮา ॐ")

def focus():
    st.success("ตั้งสมาธิ หายใจเข้าลึกๆ พิมพ์คำถาม แล้วกดปุ่ม ทำนายดวง")

def main():
    # Initialize the storage client
    storage_client = storage.Client()

    # Get a reference to the bucket
    bucket = storage_client.bucket("mutelu_bucket")

    # Download a blob from the bucket
    blobs = bucket.list_blobs(prefix="cards/")
    blob.download_to_filename("023_cleaned_all_tarot_card_data.csv")

    # Read the downloaded data and display it in Streamlit
    with open("023_cleaned_all_tarot_card_data.csv", "r") as f:
        data = f.read()
        st.write(data)

if __name__ == "__main__":
    main()

# Fetch tarot data from local CSV
def fetch_local_tarot_data():
    """Fetch tarot data from local CSV file."""
    try:
        df = pd.read_csv("/workspaces/6610424009_is/cards/023_cleaned_all_tarot_card_data.csv")
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลไพ่ทาโรต์ได้: {e}")
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