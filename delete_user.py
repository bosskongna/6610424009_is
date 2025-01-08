import streamlit as st
from google.cloud import storage
import json
import global_set as gb

gb.initialize_vertexai()  # Initialize Vertex
bucket = gb.initialize_gcs()  # Initialize GC AI


def list_users(bucket):
    """List all users in the system"""
    users = []
    if bucket:
        blobs = bucket.list_blobs(prefix="users/")
        for blob in blobs:
            try:
                user_data = json.loads(blob.download_as_text())
                users.append({
                    "username": user_data.get("username"),
                    "email": user_data.get("email"),
                    "blob_name": blob.name,
                    "user_id": user_data.get("user_id")
                })
            except json.JSONDecodeError:
                st.warning(f"Skipped invalid JSON in file: {blob.name}")
    return users

def delete_user(bucket, blob_name):
    """Delete a specific user by blob name"""
    try:
        blob = bucket.blob(blob_name)
        blob.delete()
        return True
    except Exception as e:
        st.error(f"Error deleting user: {str(e)}")
        return False

def delete_all_users(bucket):
    """Delete all users from the system"""
    success_count = 0
    error_count = 0
    
    blobs = bucket.list_blobs(prefix="users/")
    for blob in blobs:
        try:
            blob.delete()
            success_count += 1
        except Exception as e:
            st.error(f"Error deleting {blob.name}: {str(e)}")
            error_count += 1
    
    return success_count, error_count

def main():
    st.title("User Deletion Utility")
    st.warning("⚠️ Warning: Deleting users is a permanent action and cannot be undone!")
    
    if bucket is None:
        st.error("Failed to connect to Google Cloud Storage")
        return

    # Get current users
    users = list_users(bucket)
    st.write(f"Currently there are {len(users)} users in the system.")

    # Delete Options
    st.header("Delete Options")
    delete_option = st.radio(
        "Choose deletion method:",
        ["Delete All Users", "Delete Specific Users"]
    )

    if delete_option == "Delete All Users":
        st.subheader("Delete All Users")
        st.error("⚠️ This will permanently delete ALL users from the system!")
        
        # Multiple confirmation steps
        confirm_text = st.text_input("Type 'DELETE ALL USERS' to confirm:")
        confirm_checkbox = st.checkbox("I understand this action cannot be undone")
        
        if st.button("Delete All Users", type="primary"):
            if confirm_text == "DELETE ALL USERS" and confirm_checkbox:
                success_count, error_count = delete_all_users(bucket)
                st.success(f"Successfully deleted {success_count} users")
                if error_count > 0:
                    st.error(f"Failed to delete {error_count} users")
                # Clear session state and cache
                st.experimental_rerun()
            else:
                st.error("Please provide proper confirmation to delete all users")

    else:  # Delete Specific Users
        st.subheader("Delete Specific Users")
        
        # Show user list with delete buttons
        for user in users:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**Username:** {user['username']}")
                st.write(f"Email: {user['email']}")
            
            with col2:
                st.write(f"ID: {user['user_id']}")
            
            with col3:
                if st.button("Delete", key=user['blob_name']):
                    if delete_user(bucket, user['blob_name']):
                        st.success(f"Deleted user {user['username']}")
                        st.experimental_rerun()
                    else:
                        st.error(f"Failed to delete user {user['username']}")
            
            st.markdown("---")

if __name__ == "__main__":
    main()