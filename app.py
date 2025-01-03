# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_chroma import Chroma
# from langchain_core.tools import tool
# from langchain_community.utilities import SQLDatabase
# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# from langgraph.graph import MessagesState, START, StateGraph
# from langgraph.prebuilt import tools_condition, ToolNode
# from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
# from langgraph.checkpoint.memory import MemorySaver
# from utils import *

import streamlit as st
import warnings
import os
import uuid
import random

# Access the API key
gemini_api_key = st.secrets["api"]["gemini_api_key"]
# st.write(f"Gemini API Key: {gemini_api_key}")

st.set_page_config(
    page_title="Lucky Tarot",
    page_icon='assets/logo.png'
    )

st.image("assets/logo.png", width=300)

import streamlit as st
import random

# Function to generate random numbers
def generate_random_numbers(count, range_end):
    return random.sample(range(0, range_end + 1), count)

if st.button("ลงทะเบียน"):
    st.switch_page("/workspaces/6610424009_is/pages/register.py")
elif st.button("เปิดไพ่"):
    st.switch_page("pages/streamlit_app.py")

# import streamlit as st
# import datetime
# import json
# import uuid
# from google.cloud import storage
# import bcrypt

# def initialize_gcs():
#     client = storage.Client.from_service_account_json("/workspaces/6610424009_is/assets/mutelu-worldth-4019e9927759.json")
#     bucket = client.bucket("mutelu_bucket")  # Replace with your bucket name
#     return bucket

# bucket = initialize_gcs()

# def delete_user(bucket, user_id):
#     """Delete a user by user_id"""
#     blob = bucket.blob(f"users/{user_id}.json")
#     if blob.exists():
#         blob.delete()
#         return f"User with ID {user_id} has been successfully deleted."
#     else:
#         return f"User with ID {user_id} not found."
    
# user_id = "8f16e481-dfce-4cb4-99b0-e0d3f294ef50"  # Replace with the actual user_id
# result = delete_user(bucket, user_id)
# print(result)