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
import global_set as gb
import streamlit as st

gb.logo()
st.markdown("#### กดปุ่มเพื่อเริ่มใช้งาน")
st.switch_page('pages/login.py')