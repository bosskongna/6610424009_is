import streamlit as st
from google.cloud import storage
import json
from datetime import datetime

def initialize_gcs():
    """Initialize GCS client"""
    try:
        client = storage.Client.from_service_account_json("/workspaces/6610424009_is/assets/mutelu-worldth-4019e9927759.json")
        bucket = client.bucket("mutelu_bucket")
        return bucket
    except Exception as e:
        st.error(f"Failed to initialize Google Cloud Storage: {str(e)}")
        return None

def query_users(bucket, filters=None):
    """
    Query users from GCS with optional filters
    filters: dict of field:value pairs to filter by
    """
    if bucket is None:
        return []

    users = []
    blobs = bucket.list_blobs(prefix="users/")
    
    for blob in blobs:
        try:
            user_data = json.loads(blob.download_as_text())
            
            # Apply filters if any
            if filters:
                matches = all(
                    str(user_data.get(key, "")).lower() == str(value).lower()
                    for key, value in filters.items()
                )
                if not matches:
                    continue
                    
            # Remove sensitive data
            if 'password' in user_data:
                del user_data['password']
                
            users.append(user_data)
            
        except json.JSONDecodeError:
            st.warning(f"Skipped invalid JSON in file: {blob.name}")
            continue
            
    return users

def main():
    st.title("Query User Data from GCS")
    
    bucket = initialize_gcs()
    if bucket is None:
        st.error("Failed to connect to Google Cloud Storage")
        return

    # Query Options
    st.header("Query Options")
    
    query_type = st.selectbox(
        "Select Query Type",
        ["All Users", "Filter by Membership", "Search by Name", "Custom Filter"]
    )
    
    if query_type == "All Users":
        users = query_users(bucket)
        
    elif query_type == "Filter by Membership":
        membership = st.selectbox(
            "Select Membership Type",
            ["MADT3", "MADT", "Non-MADT"]
        )
        users = query_users(bucket, {"membership_type": membership})
        
    elif query_type == "Search by Name":
        name = st.text_input("Enter Name to Search")
        if name:
            users = query_users(bucket, {"name": name})
        else:
            users = []
            
    elif query_type == "Custom Filter":
        col1, col2 = st.columns(2)
        with col1:
            field = st.selectbox(
                "Select Field",
                ["username", "email", "name", "last_name", "membership_type"]
            )
        with col2:
            value = st.text_input("Enter Value")
            
        if value:
            users = query_users(bucket, {field: value})
        else:
            users = []

    # Display Results
    st.header("Results")
    if not users:
        st.write("No users found matching the criteria.")
    else:
        st.write(f"Found {len(users)} users:")
        
        # Display options
        display_type = st.radio(
            "Display Format",
            ["Table", "JSON", "Summary"]
        )
        
        if display_type == "Table":
            # Convert to a format suitable for table display
            table_data = []
            for user in users:
                table_data.append({
                    "Username": user.get("username"),
                    "Name": f"{user.get('name')} {user.get('last_name')}",
                    "Email": user.get("email"),
                    "Membership": user.get("membership_type"),
                    "Created": user.get("created_at")
                })
            st.table(table_data)
            
        elif display_type == "JSON":
            st.json(users)
            
        else:  # Summary
            for user in users:
                st.write(f"**{user.get('username')}** - {user.get('name')} {user.get('last_name')}")
                st.write(f"Membership: {user.get('membership_type')}")
                st.write("---")

if __name__ == "__main__":
    main()