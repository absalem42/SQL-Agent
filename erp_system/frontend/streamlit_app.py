import streamlit as st
import sys
from pathlib import Path
import json
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Import agents directly for local mode
try:
    from agents.smart_router_agent import executor as router_executor
    from agents.sales_agent_simple import SimpleSalesAgent
    LOCAL_MODE = True
except:
    LOCAL_MODE = False

st.set_page_config(
    page_title="Helios Dynamics ERP",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🏢 Helios Dynamics ERP System</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/white?text=Helios+Dynamics", width=200)
        
        page = st.selectbox(
            "Navigate to:",
            ["🏠 Dashboard", "🤖 Chat Interface", "📊 Analytics", "👥 Sales", "💰 Finance", "📦 Inventory", "⚙️ Admin"]
        )
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("📈 Generate Report"):
            st.success("Report generation requested!")

    # Main content based on page selection
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🤖 Chat Interface":
        show_chat_interface()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "👥 Sales":
        show_sales()
    elif page == "💰 Finance":
        show_finance()
    elif page == "📦 Inventory":
        show_inventory()
    elif page == "⚙️ Admin":
        show_admin()

def show_dashboard():
    st.header("📊 Executive Dashboard")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>130</h3>
            <p>Total Customers</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>$310K</h3>
            <p>Total Revenue</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>260</h3>
            <p>Total Orders</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>42</h3>
            <p>Active Leads</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        # Sample data for demo
        revenue_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [45000, 52000, 48000, 61000, 55000, 67000]
        })
        fig = px.line(revenue_data, x='Month', y='Revenue', title="Monthly Revenue")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Sales Pipeline")
        pipeline_data = pd.DataFrame({
            'Stage': ['Leads', 'Qualified', 'Proposals', 'Closed'],
            'Count': [42, 28, 15, 8]
        })
        fig = px.funnel(pipeline_data, x='Count', y='Stage', title="Sales Funnel")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity
    st.subheader("🔔 Recent Activity")
    activity_data = [
        {"Time": "2 minutes ago", "Event": "New order from Sara Fathy Inc", "Amount": "$3,967.47"},
        {"Time": "15 minutes ago", "Event": "Lead scored: Mohamed Adel Corp", "Score": "8.2/10"},
        {"Time": "1 hour ago", "Event": "Payment received from Omar Ali Co", "Amount": "$1,540.70"},
        {"Time": "3 hours ago", "Event": "New customer registered: Mina Adel Systems", "Amount": ""},
    ]
    
    for activity in activity_data:
        with st.container():
            col1, col2, col3 = st.columns([2, 4, 2])
            with col1:
                st.text(activity["Time"])
            with col2:
                st.text(activity["Event"])
            with col3:
                if activity["Amount"]:
                    st.text(activity["Amount"])
                elif "Score" in activity:
                    st.text(activity["Score"])

def show_chat_interface():
    st.header("🤖 AI Assistant Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Helios Dynamics ERP assistant. I can help you with sales, analytics, finance, and inventory management. What would you like to know?"}
        ]
    
    # Agent selection
    col1, col2 = st.columns([3, 1])
    with col2:
        agent_mode = st.selectbox(
            "Agent Mode:",
            ["🤖 Auto-Route", "👥 Sales Only", "📊 Analytics Only"]
        )
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your business..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_agent_response(prompt, agent_mode)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

def get_agent_response(prompt: str, agent_mode: str) -> str:
    """Get response from appropriate agent"""
    try:
        if LOCAL_MODE:
            if agent_mode == "👥 Sales Only":
                sales_agent = SimpleSalesAgent()
                result = sales_agent.invoke({"input": prompt})
                return result['output']
            else:
                # Use router for auto-routing
                result = router_executor.invoke({"input": prompt})
                return result['output']
        else:
            # Fallback to mock response
            return f"Mock response for: {prompt}\n\nI can help you with customer data, sales analytics, and business insights. This is a demonstration response."
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}\n\nPlease try rephrasing your question or contact support."

def show_analytics():
    st.header("📊 Analytics & Reporting")
    
    # Quick metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", "$310,898", "+15%")
    with col2:
        st.metric("Average Order Value", "$1,196", "+8%")
    with col3:
        st.metric("Customer Retention", "87%", "+3%")
    
    # Analytics queries
    st.subheader("🔍 Quick Analytics")
    
    query_options = [
        "Top 10 customers by revenue",
        "Monthly sales trend",
        "Lead conversion rates",
        "Product performance analysis",
        "Customer acquisition cost",
        "Revenue by region"
    ]
    
    selected_query = st.selectbox("Select a report:", query_options)
    
    if st.button("Generate Report"):
        with st.spinner("Generating analytics..."):
            # Simulate analytics generation
            if "Top 10 customers" in selected_query:
                # Sample customer data
                customer_data = pd.DataFrame({
                    'Customer': ['Sara Fathy Inc', 'Mohamed Hussein Systems', 'Hassan Samir Inc', 
                               'Hassan Mostafa Co', 'Sara Ibrahim Corp', 'Omar Ali Co',
                               'Laila Ibrahim Corp', 'Fatma Younes Corp', 'Ahmed Ali LLC', 'Nour Khalil Corp'],
                    'Revenue': [3967, 3950, 3248, 2533, 1819, 1540, 1304, 137, 2100, 1890],
                    'Orders': [2, 3, 2, 2, 3, 3, 1, 1, 2, 2]
                })
                
                fig = px.bar(customer_data, x='Customer', y='Revenue', 
                           title="Top 10 Customers by Revenue")
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(customer_data, use_container_width=True)
            
            elif "Monthly sales" in selected_query:
                # Sample monthly data
                monthly_data = pd.DataFrame({
                    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                    'Sales': [45000, 52000, 48000, 61000, 55000, 67000, 58000],
                    'Orders': [38, 43, 40, 51, 46, 56, 48]
                })
                
                fig = px.line(monthly_data, x='Month', y='Sales', 
                            title="Monthly Sales Trend", markers=True)
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(monthly_data, use_container_width=True)

def show_sales():
    st.header("👥 Sales & CRM")
    
    # Sales metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", "130", "+5")
    with col2:
        st.metric("Active Leads", "42", "+8")
    with col3:
        st.metric("Conversion Rate", "18.5%", "+2.1%")
    with col4:
        st.metric("Avg Deal Size", "$1,196", "+$134")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 View All Customers"):
            if LOCAL_MODE:
                sales_agent = SimpleSalesAgent()
                result = sales_agent.invoke({"input": "show customers"})
                st.text_area("Customer List:", result['output'], height=300)
    
    with col2:
        if st.button("🎯 Show Leads"):
            if LOCAL_MODE:
                sales_agent = SimpleSalesAgent()
                result = sales_agent.invoke({"input": "show leads"})
                st.text_area("Lead List:", result['output'], height=300)
    
    with col3:
        if st.button("📊 Customer Summary"):
            if LOCAL_MODE:
                sales_agent = SimpleSalesAgent()
                result = sales_agent.invoke({"input": "customer summary"})
                st.text_area("Summary:", result['output'], height=300)

def show_finance():
    st.header("💰 Finance & Accounting")
    st.info("🚧 Finance module coming soon! Your friend can integrate the Finance Agent here.")
    
    # Placeholder finance metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", "$310,898", "+15%")
    with col2:
        st.metric("Outstanding Invoices", "$45,230", "-5%")
    with col3:
        st.metric("Profit Margin", "23.4%", "+1.2%")
    with col4:
        st.metric("Cash Flow", "$89,450", "+12%")

def show_inventory():
    st.header("📦 Inventory & Supply Chain")
    st.info("🚧 Inventory module coming soon! This can be integrated with an Inventory Agent.")
    
    # Placeholder inventory metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products", "1,247", "+23")
    with col2:
        st.metric("Low Stock Items", "8", "-2")
    with col3:
        st.metric("Avg Inventory Value", "$125K", "+8%")
    with col4:
        st.metric("Supplier Performance", "94.2%", "+2.1%")

def show_admin():
    st.header("⚙️ System Administration")
    
    # System status
    st.subheader("🔧 System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <h4>🤖 Router Agent</h4>
            <p>Status: Active ✅</p>
            <p>Requests: 1,247</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <h4>👥 Sales Agent</h4>
            <p>Status: Active ✅</p>
            <p>Queries: 834</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="agent-card">
            <h4>📊 Analytics Agent</h4>
            <p>Status: Active ✅</p>
            <p>Reports: 156</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Database info
    st.subheader("🗄️ Database Information")
    if LOCAL_MODE:
        try:
            from db import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
            
            st.success(f"Database connected successfully! Found {len(tables)} tables.")
            
            # Show table list
            table_names = [table[0] for table in tables]
            st.multiselect("Database Tables:", table_names, default=table_names[:5])
            
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
    else:
        st.info("Database connection unavailable in demo mode.")

if __name__ == "__main__":
    main()
