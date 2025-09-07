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

# Initialize the tool registry and sales agent
tool_registry = ToolRegistry()
sales_agent = SimpleSalesAgent()

@tool
def execute_with_sales_agent(user_request: str) -> str:
    """Route requests to the Sales Agent for customer, lead, and order management"""
    print(f"🛍️ Routing to Sales Agent: {user_request}")
    try:
        result = sales_agent.invoke({"input": user_request})
        response = result['output']
        print(f"Sales Agent Response: {response[:200]}...")  # Log first 200 chars
        return response  # Return the actual response, not a wrapper message
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

# Register tools with the registry
tool_registry.register_tool(execute_with_sales_agent)
tool_registry.register_tool(get_system_info)

# Create the router agent
def create_simple_router_agent():
    llm = get_llm()
    
    # Get tools from registry
    tools = tool_registry.get_tools()
    
    # Enhanced prompt that focuses on returning the actual content
    prompt_template = """You are a Router Agent for Helios Dynamics ERP system.

Your job is to route user requests to the appropriate agent and return their EXACT response.

Available tools:
{tools}

Tool descriptions:
{tool_names_and_descriptions}

IMPORTANT INSTRUCTIONS:
1. If the user asks about customers, leads, orders, sales, or CRM - use execute_with_sales_agent
2. If the user asks about system info, health, or status - use get_system_info  
3. When you get a response from a tool, return EXACTLY what the tool returned
4. Do NOT add "Sales Agent Response:" or any wrapper text
5. Do NOT say "Here is the information you requested" - just return the actual data
"""
    prompt = PromptTemplate.from_template(prompt_template)
    
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
