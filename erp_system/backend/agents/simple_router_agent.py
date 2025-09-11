"""
Simple Router Agent - Intelligent Query Routing for ERP System

This module implements the main router agent that intelligently routes user queries
to appropriate specialized agents based on the request content and context.

Key Features:
- Natural language understanding for query classification
- Intelligent routing to specialized agents (Sales, Finance, Inventory)
- System status monitoring and health checks
- Error handling and fallback responses
- Memory management for conversation context

Architecture:
- Uses LangChain ReAct pattern for reasoning and action selection
- Integrates with MCP (Model Context Protocol) for tool management
- Supports multiple LLM providers (Google Gemini, Ollama)
- Implements conversation memory for context awareness
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from config.llm import get_llm
from mcp.tool_registry import ToolRegistry
from agents.sales_agent_simple import SimpleSalesAgent
from agents.AnalyticsAgent import create_analytics_agent

# Initialize the tool registry and agents
# The tool registry manages all available tools across agents
tool_registry = ToolRegistry()
sales_agent = SimpleSalesAgent()
analytics_agent = create_analytics_agent()

@tool
def execute_with_sales_agent(user_request: str) -> str:
    """
    Route requests to the Sales Agent for customer, lead, and order management.
    
    This tool handles all customer-related queries including:
    - Customer information retrieval and management
    - Lead tracking and scoring
    - Order history and analysis
    - Revenue reporting and analytics
    
    Args:
        user_request (str): The user's natural language request
        
    Returns:
        str: Formatted response from the Sales Agent with business data
        
    Example queries:
        - "show recent customers"
        - "display leads with high scores"
        - "customer summary report"
    """
    print(f"🛍️ Routing to Sales Agent: {user_request}")
    try:
        # Invoke the sales agent with the user request
        result = sales_agent.invoke({"input": user_request})
        response = result['output']
        print(f"Sales Agent Response: {response[:200]}...")  # Log first 200 chars for debugging
        return response  # Return the actual response content
    except Exception as e:
        return f"Sales Agent Error: {str(e)}"

@tool
def get_system_info() -> str:
    """Get system information and health status"""
    try:
        from db import get_db
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get basic counts
            cursor.execute("SELECT COUNT(*) FROM customers")
            customers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM orders")
            orders = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM leads")
            leads = cursor.fetchone()[0]
            
        return f"""📊 **System Status:**
• Database: Connected ✅
• Total Customers: {customers}
• Total Orders: {orders}
• Active Leads: {leads}
• System Health: Operational
"""
    except Exception as e:
        return f"System Info Error: {str(e)}"

@tool
def execute_with_analytics_agent(user_request: str) -> str:
    """
    Route analytics, reporting, and data analysis queries to the Analytics Agent
    
    Use this for:
    - SQL queries and data analysis  
    - Revenue/financial reporting
    - Business metrics and KPIs
    - Data visualization requests
    - Executive dashboard queries
    - Natural language to SQL conversion
    
    Args:
        user_request (str): The user's analytics or reporting request
        
    Returns:
        str: Formatted response from the Analytics Agent with data insights
        
    Example queries:
        - "What's our total revenue this month?"
        - "Show me top performing customers"
        - "Analyze sales trends"
        - "Create a chart of monthly orders"
    """
    print(f"📊 Routing to Analytics Agent: {user_request}")
    try:
        # Invoke the analytics agent with the user request
        result = analytics_agent.invoke({"input": user_request})
        response = result['output']
        print(f"Analytics Agent Response: {response[:200]}...")  # Log first 200 chars for debugging
        return response
    except Exception as e:
        return f"Analytics Agent Error: {str(e)}"

# Register tools with the registry
tool_registry.register_tool(execute_with_sales_agent)
tool_registry.register_tool(execute_with_analytics_agent)
tool_registry.register_tool(get_system_info)

# Create the router agent
def create_simple_router_agent():
    llm = get_llm()
    
    # Get tools from registry
    tools = tool_registry.get_tools()
    
    # ReAct prompt template with required variables
    prompt_template = """You are a Router Agent for Helios Dynamics ERP system.

Your job is to route user requests to the appropriate agent and return their EXACT response.

TOOLS:
------
You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT INSTRUCTIONS:
1. If the user asks about customers, leads, orders, sales, or CRM - use execute_with_sales_agent
2. If the user asks about analytics, reports, revenue, metrics, SQL queries, or data analysis - use execute_with_analytics_agent
3. If the user asks about system info, health, or status - use get_system_info  
4. When you get a response from a tool, return EXACTLY what the tool returned in your Final Answer
5. Do NOT add "Agent Response:" or any wrapper text in your Final Answer
6. Do NOT say "Here is the information you requested" - just return the actual data

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["input", "agent_scratchpad"],
        partial_variables={
            "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
            "tool_names": ", ".join([tool.name for tool in tools])
        }
    )
    
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )
    
    return executor

def run_simple_router_agent():
    """Interactive simple router agent"""
    print("\n🤖 Simple Router Agent Ready! I route your requests to the Sales Agent.")
    print("Examples:")
    print("- 'Show me top 5 customers'")
    print("- 'Last month sales data'")
    print("- 'Customer summary'")
    print("- 'Show recent leads'")
    print("- Type 'quit' to exit\n")
    
    executor = create_simple_router_agent()
    
    try:
        while True:
            user_input = input("Router > ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            try:
                result = executor.invoke({"input": user_input})
                print(f"\n{result['output']}\n")
            except Exception as e:
                print(f"Error: {str(e)}")
                
    except KeyboardInterrupt:
        print("\nGoodbye!")

# Export the executor
executor = create_simple_router_agent()

if __name__ == "__main__":
    run_simple_router_agent()
