import streamlit as st

def test_secrets():
    if "mutelu_worldth" in st.secrets:
        st.write("✅ Found mutelu_worldth section")
        creds = st.secrets["mutelu_worldth"]
        for key in creds:
            if key != "private_key":  # Don't show private key
                st.write(f"✅ {key} is present")
    else:
        st.error("❌ mutelu_worldth section not found")

test_secrets()