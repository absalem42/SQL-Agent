import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
# Fix: Import memory from langchain package, not langchain_core
from langchain.memory import ConversationBufferWindowMemory
from config.llm import get_llm
from db import get_db

# Import specialized agents
from agents.sales_agent import executor as sales_executor
# from agents.finance_agent import executor as finance_executor  
# from agents.inventory_agent import executor as inventory_executor
# from agents.analytics_agent import executor as analytics_executor

# -------- Smart Router Tools --------

@tool
def execute_with_sales_agent(user_request: str) -> str:
    """
    Execute a request using the Sales Agent for customer, order, and lead management.
    Input: user's request/question about sales, customers, orders, or leads
    """
    try:
        # Log the tool call
        log_tool_call("router", "execute_with_sales_agent", user_request)
        
        print(f"🛍️ Routing to Sales Agent: {user_request}")
        result = sales_executor.invoke({"input": user_request})
        return f"Sales Agent Response: {result['output']}"
    except Exception as e:
        return f"Sales Agent Error: {str(e)}"

@tool
def get_system_info() -> str:
    """
    Get information about the ERP system and available agents.
    No input required.
    """
    try:
        # Log the tool call
        log_tool_call("router", "get_system_info", "")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get table counts
            cursor.execute("SELECT COUNT(*) FROM customers")
            customer_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM leads")
            lead_count = cursor.fetchone()[0]
            
            # Try to get pending approvals, but handle if table doesn't exist
            try:
                cursor.execute("SELECT COUNT(*) FROM approvals WHERE status = 'pending'")
                pending_approvals = cursor.fetchone()[0]
            except:
                pending_approvals = 0
        
        info = {
            "system": "Helios Dynamics ERP System",
            "available_agents": [
                "Sales Agent - Customer management, orders, leads (active)",
                "Finance Agent - Invoices, payments, accounting (coming soon)",
                "Inventory Agent - Stock management, products (coming soon)",
                "Analytics Agent - Reports and business intelligence (coming soon)"
            ],
            "database_stats": {
                "customers": customer_count,
                "orders": order_count,
                "leads": lead_count
            },
            "pending_approvals": pending_approvals
        }
        
        return f"""
Helios Dynamics ERP System Information:
- System: {info['system']}
- Database Stats: {info['database_stats']['customers']} customers, {info['database_stats']['orders']} orders, {info['database_stats']['leads']} leads
- Pending Approvals: {info['pending_approvals']}

Available Agents:
{chr(10).join('- ' + agent for agent in info['available_agents'])}

I automatically route your requests to the right specialist based on keywords in your question.
Just ask naturally about customers, finances, inventory, or analytics!
        """.strip()
        
    except Exception as e:
        return f"Error getting system info: {str(e)}"

@tool
def classify_and_route(user_request: str) -> str:
    """
    Automatically classify the user request and route it to the appropriate specialist agent.
    Input: user's request/question
    """
    # Log the tool call
    log_tool_call("router", "classify_and_route", user_request)
    
    request_lower = user_request.lower()
    
    # Define keywords for each domain
    sales_keywords = ['customer', 'lead', 'prospect', 'sale', 'order', 'crm', 'contact', 'deal', 'client']
    finance_keywords = ['invoice', 'payment', 'finance', 'accounting', 'revenue', 'expense', 'budget', 'financial', 'money', 'cost']
    inventory_keywords = ['stock', 'inventory', 'product', 'warehouse', 'supply', 'procurement', 'vendor', 'item']
    analytics_keywords = ['report', 'analytics', 'dashboard', 'metrics', 'analysis', 'trend', 'chart', 'insight']
    
    # Calculate scores
    scores = {
        'sales': sum(1 for kw in sales_keywords if kw in request_lower),
        'finance': sum(1 for kw in finance_keywords if kw in request_lower),
        'inventory': sum(1 for kw in inventory_keywords if kw in request_lower),
        'analytics': sum(1 for kw in analytics_keywords if kw in request_lower)
    }
    
    # Find the best match
    best_domain = max(scores.items(), key=lambda x: x[1])
    
    if best_domain[1] == 0:
        return f"I can help you with various ERP tasks. Please specify if you need help with customers/sales, financial data, inventory/products, or analytics/reports. Your request: {user_request}"
    
    # Route to the appropriate agent
    domain = best_domain[0]
    confidence = best_domain[1]
    
    print(f"🎯 Auto-routing to {domain} agent (confidence: {confidence} keyword matches)")
    
    # Save the current domain in the conversation memory
    save_to_conversation_memory("router", f"Auto-routed to {domain} agent")
    
    if domain == 'sales':
        return execute_with_sales_agent(user_request)
    else:
        return f"Currently, I can only route to the Sales agent. Support for finance, inventory, and analytics agents coming soon!"

@tool
def get_pending_approvals() -> str:
    """
    Get a list of pending approvals that need human review.
    No input required.
    """
    try:
        # Log the tool call
        log_tool_call("router", "get_pending_approvals", "")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if approvals table exists
            try:
                cursor.execute("""
                    SELECT id, module, payload_json, requested_by, created_at 
                    FROM approvals 
                    WHERE status = 'pending' 
                    ORDER BY created_at DESC
                """)
                
                approvals = cursor.fetchall()
                
                if not approvals:
                    return "No pending approvals found."
                
                result = "📋 **Pending Approvals:**\n\n"
                
                for approval in approvals:
                    result += f"ID: {approval[0]} | Module: {approval[1]} | Requested by: {approval[3]}\n"
                    result += f"Created at: {approval[4]}\n"
                    result += f"Payload: {approval[2][:100]}...\n\n"
                
                return result
            except:
                return "Approvals system not yet configured."
                
    except Exception as e:
        return f"Error getting pending approvals: {str(e)}"

@tool
def submit_for_approval(module: str, action: str, payload: str, requested_by: str) -> str:
    """
    Submit a request for human approval.
    Input: JSON string with module, action, payload, and requested_by fields
    """
    try:
        # Log the tool call
        log_tool_call("router", "submit_for_approval", f"module={module}, action={action}")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            try:
                # Create the payload JSON
                payload_json = json.dumps({
                    "action": action,
                    "data": payload
                })
                
                # Insert into approvals table
                cursor.execute("""
                    INSERT INTO approvals (module, payload_json, status, requested_by, created_at)
                    VALUES (?, ?, 'pending', ?, datetime('now'))
                """, (module, payload_json, requested_by))
                
                approval_id = cursor.lastrowid
                conn.commit()
                
                return f"✅ Approval request submitted successfully. Approval ID: {approval_id}"
            except:
                return "Approvals system not yet configured."
                
    except Exception as e:
        return f"Error submitting approval request: {str(e)}"

# -------- Helper Functions --------

def log_tool_call(agent: str, tool_name: str, input_data: str) -> None:
    """Log a tool call to the database for audit purposes"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if tool_calls table exists
            try:
                # Truncate input if too long
                input_json = json.dumps({"input": input_data})[:1000]
                output_json = "{}"  # Empty output initially
                
                cursor.execute("""
                    INSERT INTO tool_calls (agent, tool_name, input_json, output_json, created_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                """, (agent, tool_name, input_json, output_json))
                
                conn.commit()
            except Exception:
                # Table doesn't exist - just log to console
                print(f"[LOG] Agent: {agent}, Tool: {tool_name}, Input: {input_data[:50]}...")
    except Exception as e:
        print(f"Error logging tool call: {str(e)}")

def save_to_conversation_memory(sender: str, content: str) -> None:
    """Save a message to the conversation history"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Try to insert in conversations/messages tables
            try:
                # Check if there's an active conversation
                cursor.execute("SELECT id FROM conversations ORDER BY started_at DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    conversation_id = result[0]
                else:
                    # Create a new conversation
                    cursor.execute("""
                        INSERT INTO conversations (user_id, started_at)
                        VALUES ('system', datetime('now'))
                    """)
                    conversation_id = cursor.lastrowid
                
                # Save the message
                cursor.execute("""
                    INSERT INTO messages (conversation_id, sender, content, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                """, (conversation_id, sender, content))
                
                conn.commit()
            except Exception:
                # Tables don't exist - just log to console
                print(f"[MEMORY] {sender}: {content[:50]}...")
    except Exception as e:
        print(f"Error saving to conversation memory: {str(e)}")

# -------- Smart Router System Prompt --------
SMART_ROUTER_SYSTEM = """You are the Smart Router Agent for Helios Dynamics, an intelligent coordinator that automatically routes requests to specialized agents.

Your main responsibilities:
1. Automatically classify user requests and route them to the appropriate specialist
2. Execute requests with the right agent and return their results
3. Provide system information when requested
4. Handle general queries and provide guidance
5. Manage approval workflows for sensitive operations

You have access to tools that can:
- Automatically classify and route requests to specialist agents
- Execute requests with Sales, Finance, Inventory, or Analytics agents
- Provide system information and capabilities
- Submit requests for human approval
- Check pending approvals

IMPORTANT ROUTING LOGIC:
- For questions about customers, orders, leads, sales → Use execute_with_sales_agent
- For questions about finances, invoices, payments, money → Use execute_with_finance_agent (coming soon)
- For questions about products, stock, inventory, warehouse → Use execute_with_inventory_agent (coming soon)
- For questions about reports, analytics, insights, trends → Use execute_with_analytics_agent (coming soon)
- For unclear requests → Use classify_and_route to auto-determine the best agent

For security and governance:
- Any financial operation exceeding $10,000 requires human approval
- Inventory adjustments over 100 units require approval
- New user account creation requires approval
- Always log sensitive operations to maintain an audit trail

Always try to automatically route and execute the request rather than just providing guidance."""

# -------- Build the Smart Router Agent --------
def create_smart_router_agent():
    llm = get_llm()
    tools = [
        classify_and_route,
        execute_with_sales_agent,
        # execute_with_finance_agent,
        # execute_with_inventory_agent,
        # execute_with_analytics_agent,
        get_system_info,
        get_pending_approvals,
        submit_for_approval
    ]
    
    # Create a memory with window size 5
    memory = ConversationBufferWindowMemory(k=5)
    
    agent = create_react_agent(llm=llm, tools=tools, prompt=PromptTemplate.from_template(SMART_ROUTER_SYSTEM))
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        early_stopping_method="generate",
        memory=memory
    )
    
    return executor

def run_smart_router_agent():
    """Interactive smart router agent"""
    print("\n🤖 Helios Dynamics ERP - Smart Router Agent Ready!")
    print("I automatically route your requests to the right specialist.")
    print("Examples:")
    print("- 'Show me customers' → Auto-routes to Sales Agent")
    print("- 'Check system status' → Shows system info")
    print("- 'Get pending approvals' → Shows approval requests")
    print("- Type 'quit' to exit\n")
    
    executor = create_smart_router_agent()
    
    try:
        while True:
            user_input = input("Helios ERP > ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            try:
                # Save user input to conversation memory
                save_to_conversation_memory("user", user_input)
                
                # Process the request
                result = executor.invoke({"input": user_input})
                print(f"\n{result['output']}\n")
                
                # Save agent response to conversation memory
                save_to_conversation_memory("router", result['output'])
                
            except Exception as e:
                print(f"Error: {str(e)}")
                
    except KeyboardInterrupt:
        print("\nGoodbye!")

# Export the tools and executor
SMART_ROUTER_TOOLS = [
    classify_and_route,
    execute_with_sales_agent,
    # execute_with_finance_agent,
    # execute_with_inventory_agent,
    # execute_with_analytics_agent,
    get_system_info,
    get_pending_approvals,
    submit_for_approval
]

# Initialize the executor
executor = create_smart_router_agent()

if __name__ == "__main__":
    run_smart_router_agent()
