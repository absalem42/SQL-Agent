import streamlit as st
import sys
from pathlib import Path

# Add backend to path - Docker container path
sys.path.insert(0, "/app/backend")

try:
    from agents.simple_router_agent import RouterAgent
    from agents.sales_agent_simple import SimpleSalesAgent
    from agents.AnalyticsAgent import create_analytics_agent_with_chat
    from memory.base_memory import RouterGlobalState, SalesEntityMemory, AnalyticsReportMemory
    AGENTS_AVAILABLE = True
except Exception as e:
    AGENTS_AVAILABLE = False
    st.error(f"Import error: {e}")

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
    st.stop()

# Initialize agents with caching
@st.cache_resource
def load_agents():
    try:
        router_state = RouterGlobalState()
        router = RouterAgent(router_state)
        sales = SimpleSalesAgent()
        analytics = create_analytics_agent_with_chat()
        return router, sales, analytics
    except Exception as e:
        st.error(f"Failed to load agents: {e}")
        return None, None, None

router_agent, sales_agent, analytics_agent = load_agents()

if not all([router_agent, sales_agent, analytics_agent]):
    st.error("Failed to initialize agents")
    st.stop()

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
    
    # Get response from selected agent
    with st.spinner(f"Getting response from {agent_choice}..."):
        try:
            if agent_choice == "Router Agent":
                response = router_agent.chat(user_input)
            elif agent_choice == "Sales Agent":
                response = sales_agent.chat(user_input)
            elif agent_choice == "Analytics Agent":
                response = analytics_agent.chat(user_input)
            else:
                response = "Unknown agent selected."
        except Exception as e:
            response = f"Error: {str(e)}"
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Status
col1, col2, col3 = st.columns(3)
with col1:
    if router_agent:
        st.success("✅ Router Ready")
    else:
        st.error("❌ Router Failed")

with col2:
    if sales_agent:
        st.success("✅ Sales Ready")
    else:
        st.error("❌ Sales Failed")

with col3:
    if analytics_agent:
        st.success("✅ Analytics Ready")
    else:
        st.error("❌ Analytics Failed")

# Footer info
st.markdown("---")
st.info(f"💬 Chat with {agent_choice} • {len(st.session_state.messages)} messages")
