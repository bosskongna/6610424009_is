import streamlit as st
import warnings
import os
import uuid
import random

def logo():
    # Access the API key
    gemini_api_key = st.secrets["api"]["gemini_api_key"]
    # st.write(f"Gemini API Key: {gemini_api_key}")
    st.set_page_config(
        page_title="Lucky Tarot",
        page_icon='assets/logo.png'
        )
    st.image("assets/logo.png", width=300)

def ohm():
    st.write("#### ॐ โอม ศรีคเณศายะ นะมะฮา ॐ")

from google.cloud import storage

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