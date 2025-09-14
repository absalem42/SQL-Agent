import streamlit as st
import sys
from pathlib import Path
import requests
import os

# API Configuration
API_URL = os.getenv("API_URL", "http://backend:8000")  # Use backend service name in docker

# Test API connection
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    if response.status_code == 200:
        AGENTS_AVAILABLE = True
        health_data = response.json()
    else:
        AGENTS_AVAILABLE = False
        health_data = None
except Exception as e:
    AGENTS_AVAILABLE = False
    health_data = None

st.set_page_config(
    page_title="ERP Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with better color contrast for messages
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        margin-left: 2rem;
        border-left: 4px solid #2196f3;
        font-weight: 500;
    }
    .assistant-message {
        background-color: #fff3e0; 
        color: #2e7d32;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        margin-right: 2rem;
        border-left: 4px solid #4caf50;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<h1 class="main-header">🚀 ERP Chat Assistant - Live Development!</h1>', unsafe_allow_html=True)

if not AGENTS_AVAILABLE:
    st.error("Agents not available. Please check the backend configuration.")
    if health_data:
        st.json(health_data)
    st.stop()

# Function to call API backend
def call_agent_api(message: str, agent_type: str) -> str:
    """Call the backend API to get agent response"""
    try:
        # Map frontend agent names to API agent names
        agent_mapping = {
            "Router Agent": "router",
            "Sales Agent": "sales", 
            "Analytics Agent": "analytics"
        }
        
        agent_name = agent_mapping.get(agent_type, "router")
        
        response = requests.post(
            f"{API_URL}/chat",
            json={"message": message, "agent": agent_name},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response received")
        else:
            return f"Error: API returned status {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to backend API."
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = "Router Agent"

# Agent Selection
st.sidebar.title("🎯 Select Agent")
agent_choice = st.sidebar.selectbox(
    "Choose an agent:",
    ["Router Agent", "Sales Agent", "Analytics Agent"],
    key="agent_selector"
)

# Update selected agent if changed
if agent_choice != st.session_state.selected_agent:
    st.session_state.selected_agent = agent_choice
    st.session_state.messages = []

# Sidebar controls
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Agent descriptions
agent_info = {
    "Router Agent": "🤖 Smart routing and system management",
    "Sales Agent": "🛍️ Customer and sales operations", 
    "Analytics Agent": "📊 Data analysis and reporting"
}

st.subheader(f"{agent_info[agent_choice]}")

# Display chat messages
if st.session_state.messages:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">👤 You: {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🤖 {agent_choice}: {message["content"]}</div>', unsafe_allow_html=True)

# Chat input
user_input = st.text_input("Ask a question:", key="chat_input", placeholder=f"Ask {agent_choice} something...")

if st.button("Send") and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response from selected agent via API
    with st.spinner(f"Getting response from {agent_choice}..."):
        response = call_agent_api(user_input, agent_choice)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Status - Show backend API health
if health_data:
    col1, col2, col3 = st.columns(3)
    with col1:
        router_status = health_data.get("agents", {}).get("router", "unavailable")
        if router_status == "available":
            st.success("✅ Router Ready")
        else:
            st.error("❌ Router Failed")

    with col2:
        sales_status = health_data.get("agents", {}).get("sales", "unavailable")
        if sales_status == "available":
            st.success("✅ Sales Ready")
        else:
            st.error("❌ Sales Failed")

    with col3:
        st.success(f"✅ API Connected")

# Footer info
st.markdown("---")
st.info(f"💬 Chat with {agent_choice} • {len(st.session_state.messages)} messages • API: {API_URL}")
