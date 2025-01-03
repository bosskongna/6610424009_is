import streamlit as st
import global_set as gb
import json
import pandas as pd

bucket = gb.initialize_gcs()
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

def query_logs(bucket, filters=None):
    """
    Query reading logs from GCS with optional filters
    filters: dict of field:value pairs to filter by
    """
    if bucket is None:
        return []

    logs = []
    log_ori = []
    blobs = bucket.list_blobs(prefix="user_logs/")
    
    for blob in blobs:
        try:
            # Skip directories/folders
            if blob.name.endswith('/'):
                continue
                
            log_data = json.loads(blob.download_as_text())
            
            # Apply filters if any
            if filters:
                matches = all(
                    str(log_data.get(key, "")).lower() == str(value).lower()
                    for key, value in filters.items()
                )
                if not matches:
                    continue

            # Exclude specific user_id
            if log_data.get('user_id') == '24db0843-ff09-467d-bbe1-f5e013a41355':
                continue
                
            # Add metadata about the log
            log_data['file_path'] = blob.name
            log_data['created_at'] = blob.time_created.isoformat()
            logs.append(log_data)
            log_ori.append({"user_input": log_data.get("user_input"),"user_id": log_data.get("user_id")})
            log_ori = log_ori
        except json.JSONDecodeError:
            st.warning(f"Skipped invalid JSON in file: {blob.name}")
            continue
    return logs,log_ori

import streamlit as st
import global_set as gb
import json


bucket, services_initialized = gb.initialize_services()

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
        except Exception as e:
            st.error(f"Error reading user data: {e}")
    
    return users

def update_membership(bucket, username, new_membership):
    """
    Update the membership of a user in GCS
    """
    if bucket is None:
        st.error("Bucket is not initialized.")
        return

    blobs = bucket.list_blobs(prefix="users/")
    
    for blob in blobs:
        try:
            blob_content = blob.download_as_text()
            if not blob_content:
                # st.write(bucket.list_blobs)
                # st.error(f"Blob {bucket.list_blobs} is empty.")
                continue

            user_data = json.loads(blob_content)
            
            if user_data.get('username') == username:
                user_data['membership_type'] = new_membership
                blob.upload_from_string(json.dumps(user_data))
                st.success(f"Membership of {username} updated to {new_membership}.")
                return
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON from blob {blob.name}: {e}")
        except Exception as e:
            st.error(f"Error updating user data in blob {blob.name}: {e}")

    st.error(f"User {username} not found.")


def main():
    st.title("Query Data from GCS")
    
    if bucket is None:
        st.error("Failed to connect to Google Cloud Storage")
        return

    # Query Options
    st.header("Query Options")
    
    query_type = st.selectbox(
        "Select Query Type",
        ["User Data", "Reading Logs"]
    )
    
    if query_type == "User Data":
        # User query options
        user_query_type = st.selectbox(
            "Select User Query Type",
            ["All Users", "Filter by Membership", "Search by Name"]
        )
        
        if user_query_type == "All Users":
            results = query_users(bucket)
        elif user_query_type == "Filter by Membership":
            membership = st.selectbox(
                "Select Membership Type",
                ["MADT3", "MADT", "Non-MADT"]
            )
            results = query_users(bucket, {"membership_type": membership})
        elif user_query_type == "Search by Name":
            name = st.text_input("Enter Name to Search")
            if name:
                results = query_users(bucket, {"name": name})
            else:
                results = []
                
    elif query_type == "Reading Logs":  # Reading Logs
        # Log query options
        log_query_type = st.selectbox(
            "Select Log Query Type",
            ["All Logs", "Filter by Reading Type", "Filter by User ID", "Filter by Date"]
        )
        
        if log_query_type == "All Logs":
            results,_ = query_logs(bucket)
            
        elif log_query_type == "Filter by Reading Type":
            reading_type = st.selectbox(
                "Select Reading Type",
                ["daily", "year_ahead", "celtic_cross", "comparison","three_card","cross_spread","relationship","Horseshoe Spread","chance"]
            )
            results,table_log = query_logs(bucket, {"reading_type": reading_type}) 
            # st.download_button(label="download",data=table_log)
        elif log_query_type == "Filter by User ID":
            user_id = st.text_input("Enter User ID")
            if user_id:
                results,_ = query_logs(bucket, {"user_id": user_id})
            else:
                results = []
        elif log_query_type == "Filter by Date":
            date = st.date_input("Select Date")
            if date:
                date_str = date.strftime("%Y-%m-%d")
                st.write(f"Filtering logs for date: {date_str}")  # Optional for debugging
                
                # Modify filter to check if date_str is in the timestamp
                results,_ = query_logs(bucket, {"reading_timestamp": date_str})
                results = [
                    log for log in results
                    if log.get("reading_timestamp", "").startswith(date_str)
                ]
                
                if not results:
                    st.warning(f"No logs found for the selected date: {date_str}")
            else:
                results = []
        
   


    # Display Results
    st.header("Results")
    if not results:
        st.write("No data found matching the criteria.")
    else:
        st.write(f"Found {len(results)} records:")
        
        display_type = st.radio(
            "Display Format",
            ["Summary", "Full JSON", "Table"]
        )
        
        if display_type == "Summary":
            for item in results:
                if query_type == "User Data":
                    st.write(f"**{item.get('username')}** - {item.get('name')} {item.get('last_name')}")
                    st.write(f"Membership: {item.get('membership_type')}")
                else:  # Logs
                    st.write(f"**Reading Type:** {item.get('reading_type')}")
                    st.write(f"**User ID:** {item.get('user_id')}")
                    st.write(f"**Timestamp:** {item.get('reading_timestamp')}")
                st.write("---")
      
                
        elif display_type == "Full JSON":
            st.json(results)
            
        else:  # Table
            if query_type == "User Data":
                table_data = [{
                    "Username": item.get("username"),
                    "Name": f"{item.get('name')} {item.get('last_name')}",
                    "Email": item.get("email"),
                    "Membership": item.get("membership_type"),
                    "Created": item.get("created_at")
                } for item in results]
            else:  # Logs
                table_data = [{
                    "Reading Type": item.get("reading_type"),
                    "User ID": item.get("user_id"),
                    "Timestamp": item.get("reading_timestamp"),
                    "User input": item.get("user_input", {}),
                    "output": item.get("predictions", {})
                } for item in results]
            
            # Exclude specific user_id
            table_data = [item for item in table_data if item.get("User ID") != "24db0843-ff09-467d-bbe1-f5e013a41355"]
            df = pd.DataFrame(table_data)
            # st.table(df)
            ori_log = df.to_csv().encode("utf-8")
            st.download_button("Download CSV", data=ori_log, file_name='results.csv', mime='text/csv')

if __name__ == "__main__":
    main()