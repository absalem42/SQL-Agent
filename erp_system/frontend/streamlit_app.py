import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from agents.simple_router_agent import create_simple_router_agent
    from agents.sales_agent_simple import SimpleSalesAgent
    from agents.AnalyticsAgent import create_analytics_agent
    AGENTS_AVAILABLE = True
except Exception as e:
    AGENTS_AVAILABLE = False

st.set_page_config(
    page_title="ERP System - 3 Agent Demo",
    page_icon="🏢",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-section {
        border: 2px solid #e0e0e0;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<h1 class="main-header">🏢 ERP System - 3 Agent Architecture</h1>', unsafe_allow_html=True)

if not AGENTS_AVAILABLE:
    st.error("Agents not available. Please check the backend configuration.")
    st.stop()

# Initialize agents
@st.cache_resource
def load_agents():
    try:
        router = create_simple_router_agent()
        sales = SimpleSalesAgent()
        analytics = create_analytics_agent()
        return router, sales, analytics
    except Exception as e:
        st.error(f"Failed to load agents: {e}")
        return None, None, None

router_agent, sales_agent, analytics_agent = load_agents()

if not all([router_agent, sales_agent, analytics_agent]):
    st.error("Failed to initialize agents")
    st.stop()

# Agent Selection
st.sidebar.title("🎯 Select Agent")
agent_choice = st.sidebar.radio(
    "Choose an agent to interact with:",
    ["🤖 Router Agent (Smart Routing)", "🛍️ Sales & CRM Agent", "📊 Analytics Agent"]
)

# Main Chat Interface
st.markdown("---")

if agent_choice == "🤖 Router Agent (Smart Routing)":
    st.markdown('<div class="agent-section">', unsafe_allow_html=True)
    st.header("🤖 Router Agent")
    st.write("**Intelligent query routing** - Automatically routes your queries to the appropriate specialized agent")
    
    query = st.text_input("Ask anything (will be routed automatically):", placeholder="e.g., 'show customers', 'what's our revenue?', 'system status'")
    
    if st.button("Send to Router", type="primary"):
        if query:
            with st.spinner("Router processing..."):
                try:
                    result = router_agent.invoke({"input": query})
                    st.success("✅ Router Response:")
                    st.write(result['output'])
                except Exception as e:
                    st.error(f"Router Error: {e}")
        else:
            st.warning("Please enter a query")
    st.markdown('</div>', unsafe_allow_html=True)

elif agent_choice == "🛍️ Sales & CRM Agent":
    st.markdown('<div class="agent-section">', unsafe_allow_html=True)
    st.header("🛍️ Sales & CRM Agent")
    st.write("**Direct sales operations** - Customer management, orders, leads")
    
    query = st.text_input("Sales/CRM Query:", placeholder="e.g., 'show recent customers', 'list leads', 'customer summary'")
    
    if st.button("Send to Sales Agent", type="primary"):
        if query:
            with st.spinner("Sales agent processing..."):
                try:
                    # Use router to execute with sales agent
                    result = router_agent.invoke({"input": query})
                    st.success("✅ Sales Agent Response:")
                    st.write(result['output'])
                except Exception as e:
                    st.error(f"Sales Agent Error: {e}")
        else:
            st.warning("Please enter a query")
    st.markdown('</div>', unsafe_allow_html=True)

elif agent_choice == "📊 Analytics Agent":
    st.markdown('<div class="agent-section">', unsafe_allow_html=True)
    st.header("📊 Analytics Agent")
    st.write("**Data analysis and reporting** - SQL queries, revenue analysis, business intelligence")
    
    query = st.text_input("Analytics Query:", placeholder="e.g., 'total revenue', 'customer analytics', 'how many orders'")
    
    if st.button("Send to Analytics Agent", type="primary"):
        if query:
            with st.spinner("Analytics processing..."):
                try:
                    result = analytics_agent.invoke({"input": query})
                    st.success("✅ Analytics Response:")
                    st.write(result['output'])
                except Exception as e:
                    st.error(f"Analytics Agent Error: {e}")
        else:
            st.warning("Please enter a query")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("**System Status:** ✅ All 3 agents loaded and ready")
st.markdown("**Architecture:** Router Agent + Sales Agent + Analytics Agent")
