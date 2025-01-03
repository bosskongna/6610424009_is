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
import global_set as gb

gb.logo()

# gb.api_key()

if st.button("log out"):
    st.switch_page('pages/login.py')



# Function to generate random numbers
def generate_random_numbers(count, range_end):
    return random.sample(range(0, range_end + 1), count)

# Initialize session state for chat history, active button, and user input
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_button" not in st.session_state:
    st.session_state.active_button = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Function to display chat history
def display_chat_history():
    st.write("## Chat History")
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.write(f"**You:** {chat['message']}")
        elif chat["role"] == "bot":
            st.write(f"**Lucky:** {chat['message']}")

# Improved Layout for Buttons and Descriptions

gb.ohm()
st.markdown("#### เลือกรูปแบบการเปิดไพ่")
# for i, (button_text, description) in enumerate(
#     [
#         # ("แบบที่ 1", "เปิดไพ่ 1 ใบ เพื่ออ่านไพ่รายวัน"),
#         ("แบบที่ 2", "เปิดไพ่ 1 ใบ เพื่อตอบคำถาม ใช่/ไม่ใช่ หรือโอกาสที่จะเกิด (คำถามปลายปิด)"),
#         ("แบบที่ 3", "เปิดไพ่ 3 ใบ เพื่อตอบคำถามต่างๆ (คำถามปลายเปิด)"),
#         ("แบบที่ 4", "เปิดไพ่ 5 ใบ เพื่อวิเคราะห์สถานการณ์"),
#         ("แบบที่ 5", "เปิดไพ่ 6 ใบ เพื่อเพื่อดูการขับเคลื่อนระหว่างคนสองคน ความรู้สึก และทิศทางของความสัมพันธ์"),
#         # ("แบบที่ 6", "เปิดไพ่ 7 ใบ เพื่อดูอดีต ปัจจุบัน อิทธิพลที่ซ่อนอยู่ อุปสรรค อิทธิพลภายนอก คำแนะนำ และผลลัพธ์ที่น่าจะเกิดขึ้น"),
#         # ("แบบที่ 7", "เปิดไพ่ 10 ใบ การทำนายด้วยไพ่ 10 ใบ แสดงถึงสถานการณ์ปัจจุบัน สิ่งที่ท้าทาย เป้าหมาย รากฐาน อดีต อนาคต ตัวคุณ สิ่งรอบตัว ความหวัง และผลลัพธ์"),
#         # ("แบบที่ 8", "เปิดไพ่ 13 ใบ เพื่อทำนายอนาคตแต่ละเดือน 12 เดือน "),
#         ("แบบที่ 9", "เปืดไพ่ เพื่อให้ไพ่ช่วยเลือก")
#     ]
# ):
#     col1, col2 = st.columns([1, 5])  # Adjust width of columns for better alignment
#     with col1:
#         if st.button(button_text, key=f"button_{i+1}"):
#             st.session_state.active_button = f"button{i+1}"
#             if button_text == "แบบที่ 1":  
#                 st.switch_page("pages/daily.py")
#             elif button_text == "แบบที่ 2": 
#                 st.switch_page("pages/chance.py")
#             elif button_text == "แบบที่ 3": 
#                 st.switch_page("pages/type3.py")
#             elif button_text == "แบบที่ 4": 
#                 st.switch_page("pages/type4.py")
#             elif button_text == "แบบที่ 5": 
#                 st.switch_page("pages/type5.py")
#             elif button_text == "แบบที่ 6": 
#                 st.switch_page("pages/type6.py")
#             elif button_text == "แบบที่ 7": 
#                 st.switch_page("pages/type7.py")
#             elif button_text == "แบบที่ 8": 
#                 st.switch_page("pages/type8.py")
#             elif button_text == "แบบที่ 9": 
#                 st.switch_page("pages/type9.py")
#     with col2:
#         st.write(description)

for i, (button_text, description) in enumerate(
    [
        # ("แบบที่ 1", "เปิดไพ่ 1 ใบ เพื่ออ่านไพ่รายวัน"),
        ("แบบที่ 1", "เปิดไพ่ 1 ใบ เพื่อตอบคำถาม ใช่/ไม่ใช่ หรือโอกาสที่จะเกิด (คำถามปลายปิด)"),
        ("แบบที่ 2", "เปิดไพ่ 3 ใบ เพื่อตอบคำถามต่างๆ (คำถามปลายเปิด)"),
        ("แบบที่ 3", "เปิดไพ่ 5 ใบ เพื่อวิเคราะห์สถานการณ์"),
        ("แบบที่ 4", "เปิดไพ่ 6 ใบ เพื่อเพื่อดูการขับเคลื่อนระหว่างคนสองคน ความรู้สึก และทิศทางของความสัมพันธ์"),
        # ("แบบที่ 6", "เปิดไพ่ 7 ใบ เพื่อดูอดีต ปัจจุบัน อิทธิพลที่ซ่อนอยู่ อุปสรรค อิทธิพลภายนอก คำแนะนำ และผลลัพธ์ที่น่าจะเกิดขึ้น"),
        # ("แบบที่ 7", "เปิดไพ่ 10 ใบ การทำนายด้วยไพ่ 10 ใบ แสดงถึงสถานการณ์ปัจจุบัน สิ่งที่ท้าทาย เป้าหมาย รากฐาน อดีต อนาคต ตัวคุณ สิ่งรอบตัว ความหวัง และผลลัพธ์"),
        # ("แบบที่ 8", "เปิดไพ่ 13 ใบ เพื่อทำนายอนาคตแต่ละเดือน 12 เดือน "),
        ("แบบที่ 5", "เปืดไพ่ เพื่อให้ไพ่ช่วยเลือก")
    ]
):
    col1, col2 = st.columns([1, 5])  # Adjust width of columns for better alignment
    with col1:
        if st.button(button_text, key=f"button_{i+1}"):
            st.session_state.active_button = f"button{i+1}"
            # if button_text == "แบบที่ 1":  
            #     st.switch_page("pages/daily.py")
            if button_text == "แบบที่ 1": 
                st.switch_page("pages/chance.py")
            elif button_text == "แบบที่ 2": 
                st.switch_page("pages/type3.py")
            elif button_text == "แบบที่ 3": 
                st.switch_page("pages/type4.py")
            elif button_text == "แบบที่ 4": 
                st.switch_page("pages/type5.py")
            # elif button_text == "แบบที่ 6": 
            #     st.switch_page("pages/type6.py")
            # elif button_text == "แบบที่ 7": 
            #     st.switch_page("pages/type7.py")
            # elif button_text == "แบบที่ 8": 
            #     st.switch_page("pages/type8.py")
            elif button_text == "แบบที่ 5": 
                st.switch_page("pages/type9.py")
    with col2:
        st.write(description)

st.markdown("#### นัดดูดวงออนไลน์")
st.markdown("##### Function นี้ยังไม่เปิดให้บริการ")
# st.link_button(
#     label="Go to make appointment",
#     url="https://calendar.app.google/SLRFcxXXd77sFQPv5",
#     type="primary",
#     use_container_width=True
# )

# if st.button("นัดหมาย"):
    # st.switch_page("app.py")

# Handle User Input for Buttons 1 and 2
# if st.session_state.active_button == "button2":
#     user_input = st.text_input("You: ", key="input1", placeholder="Type your message here...")
#     if user_input:
#         random_number = random.randint(0, 72)
#         response = f"คำถามของคุณ: {user_input}\n คุณได้ไพ่: {random_number}"
#         st.session_state.chat_history.append({"role": "user", "message": user_input})
#         st.session_state.chat_history.append({"role": "bot", "message": response})
#         st.session_state.user_input = ""  # Reset the input field
#         st.session_state.active_button = None

# elif st.session_state.active_button == "button3":
#     user_input = st.text_input("You: ", key="input2", placeholder="Type your message here...")
#     if user_input:
#         random_numbers = generate_random_numbers(3, 72)
#         response = (
#             f"คำถามของคุณ: {user_input}\n"
#             f"คุณได้ไพ่: {random_numbers[0]}, {random_numbers[1]}, {random_numbers[2]}"
#         )
#         st.session_state.chat_history.append({"role": "user", "message": user_input})
#         st.session_state.chat_history.append({"role": "bot", "message": response})
#         st.session_state.user_input = ""  # Reset the input field
#         st.session_state.active_button = None

# Display Chat History
# display_chat_history()