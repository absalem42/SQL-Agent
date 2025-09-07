import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
# Fix: Import memory from langchain package, not langchain_core
from langchain.memory import ConversationBufferMemory
from config.llm import get_llm
# Fix: Import get_db instead of get_db_connection
from db import get_db
from tools.sales_tools import SalesTools

# Initialize sales tools
sales_tools_instance = SalesTools()

# -------- Sales Agent Tools --------

@tool
def sales_sql_read(sql_query: str) -> List[Dict]:
    """
    Execute a read-only SQL query on the sales database tables.
    Input: SQL SELECT query (must start with SELECT)
    """
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed for read operations."
    
    try:
        return sales_tools_instance.sales_sql_read(sql_query)
    except Exception as e:
        return f"SQL Error: {str(e)}"

@tool
def get_customers() -> str:
    """
    Get a list of customers with their order history and spending details.
    No input required.
    """
    try:
        results = sales_sql_read("""
            SELECT c.id, c.name, c.email, c.phone, c.created_at,
                   COUNT(o.id) as order_count,
                   COALESCE(SUM(o.total), 0) as total_spent
            FROM customers c 
            LEFT JOIN orders o ON c.id = o.customer_id 
            GROUP BY c.id 
            ORDER BY c.created_at DESC 
            LIMIT 10
        """)
        
        if not results or "error" in str(results).lower():
            return "No customers found or error retrieving customers."
        
        result = "📋 **Recent Customers:**\n\n"
        for customer in results:
            result += f"• **{customer['name']}** ({customer['email']})\n"
            result += f"  📞 {customer.get('phone', 'N/A')}\n"
            result += f"  📦 {customer['order_count']} orders | 💰 ${customer['total_spent']:.2f}\n"
            result += f"  📅 Customer since: {customer.get('created_at', 'N/A')}\n\n"
        
        return result
    except Exception as e:
        return f"Error getting customers: {str(e)}"

@tool
def search_customers(search_term: str) -> str:
    """
    Search for customers by name or email.
    Input: search term (name or email to search for)
    """
    if not search_term or len(search_term) < 3:
        return "Please provide a search term with at least 3 characters."
    
    try:
        results = sales_sql_read(f"""
            SELECT c.id, c.name, c.email, c.phone, c.created_at,
                   COUNT(o.id) as order_count,
                   COALESCE(SUM(o.total), 0) as total_spent
            FROM customers c 
            LEFT JOIN orders o ON c.id = o.customer_id 
            WHERE c.name LIKE '%{search_term}%' OR c.email LIKE '%{search_term}%'
            GROUP BY c.id 
            ORDER BY c.name
            LIMIT 5
        """)
        
        if not results or len(results) == 0:
            return f"No customers found matching '{search_term}'."
        
        result = f"🔍 **Search Results for '{search_term}':**\n\n"
        for customer in results:
            result += f"• **{customer['name']}** ({customer['email']})\n"
            result += f"  📞 {customer.get('phone', 'N/A')}\n"
            result += f"  📦 {customer['order_count']} orders | 💰 ${customer['total_spent']:.2f}\n"
            result += f"  📅 Customer since: {customer.get('created_at', 'N/A')}\n\n"
            
            # Get customer preferences from customer_kv
            try:
                preferences = sales_sql_read(f"""
                    SELECT key, value FROM customer_kv
                    WHERE customer_id = {customer['id']}
                    AND key IN ('preferred_contact', 'notes', 'sentiment')
                """)
                
                if preferences and len(preferences) > 0:
                    result += "  **Customer Preferences/Notes:**\n"
                    for pref in preferences:
                        result += f"  • {pref['key']}: {pref['value']}\n"
                    result += "\n"
            except:
                pass
        
        return result
    except Exception as e:
        return f"Error searching customers: {str(e)}"

@tool
def get_customer_summary() -> str:
    """
    Get customer summary statistics including total count and top customers.
    No input required.
    """
    try:
        # Get total customer count
        total_count = sales_sql_read("SELECT COUNT(*) as count FROM customers")
        count = total_count[0]['count'] if total_count else 0
        
        # Get new customers this month
        new_customers = sales_sql_read("""
            SELECT COUNT(*) as count FROM customers
            WHERE created_at >= date('now', 'start of month')
        """)
        new_count = new_customers[0]['count'] if new_customers else 0
        
        # Get top 3 customers by revenue
        top_customers = sales_sql_read("""
            SELECT c.name, COUNT(o.id) as order_count, COALESCE(SUM(o.total), 0) as total_spent
            FROM customers c 
            JOIN orders o ON c.id = o.customer_id 
            GROUP BY c.id, c.name 
            ORDER BY total_spent DESC 
            LIMIT 3
        """)
        
        result = "📊 **Customer Summary:**\n\n"
        result += f"Total Customers: {count}\n"
        result += f"New This Month: {new_count}\n\n"
        
        if top_customers and len(top_customers) > 0:
            result += "**Top 3 Customers by Revenue:**\n"
            for i, customer in enumerate(top_customers, 1):
                result += f"{i}. {customer['name']}: ${customer['total_spent']:.2f} ({customer['order_count']} orders)\n"
        
        return result
    except Exception as e:
        return f"Error getting customer summary: {str(e)}"

@tool
def get_top_customers() -> str:
    """
    Get the top 5 customers by order count and total spending.
    No input required.
    """
    try:
        results = sales_tools_instance.sales_sql_read("""
            SELECT c.name, c.email, 
                   COUNT(o.id) as order_count,
                   COALESCE(SUM(o.total_amount), 0) as total_spent
            FROM customers c 
            LEFT JOIN orders o ON c.id = o.customer_id 
            GROUP BY c.id, c.name, c.email 
            ORDER BY total_spent DESC, order_count DESC 
            LIMIT 5
        """)
        
        if not results or "error" in str(results):
            return "❌ Error getting top customers data."
        
        result = "🏆 **Top 5 Customers (by spending):**\n\n"
        for i, customer in enumerate(results, 1):
            result += f"{i}. **{customer['name']}** ({customer['email']})\n"
            result += f"   📦 {customer['order_count']} orders | 💰 ${customer['total_spent']:.2f}\n\n"
        
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"

@tool
def get_last_month_sales() -> str:
    """
    Get sales data from the last 30 days.
    No input required.
    """
    try:
        # Get orders from last 30 days
        results = sales_tools_instance.sales_sql_read("""
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(AVG(total_amount), 0) as avg_order_value
            FROM orders 
            WHERE created_at >= date('now', '-30 days')
        """)
        
        # Get top customers from last month
        top_customers = sales_tools_instance.sales_sql_read("""
            SELECT c.name, COUNT(o.id) as orders, SUM(o.total_amount) as spent
            FROM customers c 
            JOIN orders o ON c.id = o.customer_id 
            WHERE o.created_at >= date('now', '-30 days')
            GROUP BY c.id, c.name 
            ORDER BY spent DESC 
            LIMIT 3
        """)
        
        if not results:
            return "❌ No sales data found for the last month."
        
        data = results[0]
        result = "📈 **Last 30 Days Sales Summary:**\n\n"
        result += f"💰 Total Revenue: ${data['total_revenue']:.2f}\n"
        result += f"📦 Total Orders: {data['total_orders']}\n"
        result += f"📊 Average Order Value: ${data['avg_order_value']:.2f}\n\n"
        
        if top_customers:
            result += "🏆 **Top Customers This Month:**\n"
            for customer in top_customers:
                result += f"• {customer['name']}: {customer['orders']} orders, ${customer['spent']:.2f}\n"
        
        return result
    except Exception as e:
        return f"❌ Error getting last month sales: {str(e)}"

@tool
def get_leads() -> str:
    """
    Get a list of recent leads with their status and estimated value.
    No input required.
    """
    try:
        results = sales_sql_read("""
            SELECT customer_name, contact_email, message, score, status, created_at
            FROM leads
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        if not results or len(results) == 0:
            return "No leads found."
        
        result = "🎯 **Recent Leads:**\n\n"
        for lead in results:
            result += f"• **{lead['customer_name']}** ({lead['contact_email']})\n"
            result += f"  Status: {lead['status']}\n"
            if lead['score']:
                result += f"  Score: {lead['score']:.1f}/10\n"
            result += f"  Created: {lead['created_at']}\n"
            result += f"  Message: {lead['message'][:100]}...\n\n"
        
        return result
    except Exception as e:
        return f"Error getting leads: {str(e)}"

@tool
def score_leads() -> str:
    """
    Run lead scoring analysis to prioritize leads based on value and source.
    No input required.
    """
    try:
        # Update lead scores based on keywords and other factors
        leads = sales_sql_read("""
            SELECT id, message, customer_name, contact_email
            FROM leads
            WHERE status = 'new'
        """)
        
        if not leads or len(leads) == 0:
            return "No new leads to score."
        
        # Simple keyword-based scoring logic
        high_value_keywords = ['urgent', 'asap', 'interested', 'buy', 'purchase', 'demo', 'immediately']
        email_domains_weight = {'gmail.com': 0.5, 'hotmail.com': 0.5, 'yahoo.com': 0.5}  # Lower scores for personal emails
        
        scored_leads = []
        
        for lead in leads:
            base_score = 5.0  # Start with mid-range score
            
            # Check for high-value keywords
            message = lead['message'].lower() if lead['message'] else ""
            keyword_matches = sum(1 for kw in high_value_keywords if kw in message)
            base_score += keyword_matches * 0.8
            
            # Check email domain
            email = lead['contact_email'].lower() if lead['contact_email'] else ""
            domain = email.split('@')[-1] if '@' in email else ""
            
            # Reduce score for personal email domains
            if domain in email_domains_weight:
                base_score -= email_domains_weight[domain]
            else:
                # Business domain is better
                base_score += 1.0
                
            # Cap score between 1-10
            final_score = max(1.0, min(10.0, base_score))
            
            # Update score in database
            sales_tools_instance.sales_sql_write(f"""
                UPDATE leads 
                SET score = {final_score:.1f}
                WHERE id = {lead['id']}
            """)
            
            scored_leads.append({
                'id': lead['id'],
                'name': lead['customer_name'],
                'score': final_score
            })
        
        # Sort leads by score
        scored_leads.sort(key=lambda x: x['score'], reverse=True)
        
        # Generate report
        result = "✅ **Lead Scoring Complete**\n\n"
        result += f"Processed {len(scored_leads)} leads\n\n"
        
        result += "**Top Leads:**\n"
        for i, lead in enumerate(scored_leads[:5], 1):
            result += f"{i}. {lead['name']} - Score: {lead['score']:.1f}/10\n"
        
        return result
    except Exception as e:
        return f"Error scoring leads: {str(e)}"

@tool
def get_orders() -> str:
    """
    Get a list of recent orders with customer information and status.
    No input required.
    """
    try:
        results = sales_sql_read("""
            SELECT o.id, o.total, o.status, o.created_at,
                   c.name as customer_name, c.email as customer_email
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.created_at DESC
            LIMIT 10
        """)
        
        if not results or len(results) == 0:
            return "No orders found."
        
        result = "📦 **Recent Orders:**\n\n"
        for order in results:
            result += f"Order #{order['id']} - {order['status']}\n"
            result += f"Customer: {order['customer_name']} ({order['customer_email']})\n"
            result += f"Total: ${order['total']:.2f}\n"
            result += f"Date: {order['created_at']}\n\n"
            
            # Get order items
            try:
                items = sales_sql_read(f"""
                    SELECT oi.quantity, oi.price, p.name as product_name
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = {order['id']}
                """)
                
                if items and len(items) > 0:
                    result += "  Items:\n"
                    for item in items:
                        result += f"  • {item['quantity']}x {item['product_name']} @ ${item['price']:.2f}\n"
                    result += "\n"
            except:
                pass
        
        return result
    except Exception as e:
        return f"Error getting orders: {str(e)}"

@tool
def sales_rag_search(query: str) -> str:
    """
    Search the sales knowledge base for information about policies, pricing, etc.
    Input: search query (topic to search for like 'pricing', 'warranty', 'shipping')
    """
    try:
        if not query or len(query) < 3:
            return "Please provide a search query with at least 3 characters."
        
        # For this implementation, we'll simulate the RAG search with simple document lookup
        # Normally, this would use a vector database with embeddings
        
        # Simulate some document matches based on keywords
        documents = []
        query_lower = query.lower()
        
        # Simple document retrieval simulation
        sales_docs = [
            {
                "title": "Pricing Policy",
                "content": "Our standard pricing model includes volume discounts starting at 100 units (5%), 500 units (10%), and 1000+ units (15%). Custom quotes available for enterprise clients.",
                "keywords": ["price", "pricing", "discount", "volume", "quote"]
            },
            {
                "title": "Returns & Warranty",
                "content": "Products have a 30-day money-back guarantee and a 12-month limited warranty covering manufacturing defects. Extended warranties available for purchase.",
                "keywords": ["return", "warranty", "guarantee", "defect", "refund"]
            },
            {
                "title": "Shipping Options",
                "content": "Standard shipping (3-5 business days): Free for orders over $100. Express shipping (1-2 business days): $25 flat rate. International shipping available to select countries.",
                "keywords": ["ship", "shipping", "delivery", "express", "international"]
            },
            {
                "title": "Lead Management Process",
                "content": "New leads should be scored within 24 hours and assigned to a sales rep within 48 hours. High-value leads (score 8+) require follow-up within 4 business hours.",
                "keywords": ["lead", "scoring", "follow-up", "prospect", "assignment"]
            }
        ]
        
        # Find matching documents
        for doc in sales_docs:
            if any(kw in query_lower for kw in doc["keywords"]) or query_lower in doc["title"].lower():
                documents.append(doc)
        
        if not documents:
            return f"No information found for query: '{query}'. Try different keywords or contact the sales manager."
        
        # Format the response
        result = f"📚 **Knowledge Base Results for '{query}':**\n\n"
        for doc in documents:
            result += f"**{doc['title']}**\n{doc['content']}\n\n"
        
        return result
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

@tool
def get_support_tickets() -> str:
    """
    Get a list of recent support tickets with priority and status.
    No input required.
    """
    try:
        results = sales_sql_read("""
            SELECT t.id, t.subject, t.status, t.created_at, c.name as customer_name
            FROM tickets t
            JOIN customers c ON t.customer_id = c.id
            ORDER BY t.created_at DESC
            LIMIT 10
        """)
        
        if not results or len(results) == 0:
            return "No support tickets found."
        
        result = "🎫 **Recent Support Tickets:**\n\n"
        for ticket in results:
            result += f"#{ticket['id']} - {ticket['subject']}\n"
            result += f"Customer: {ticket['customer_name']}\n"
            result += f"Status: {ticket['status']}\n"
            result += f"Created: {ticket['created_at']}\n\n"
        
        return result
    except Exception as e:
        return f"Error getting support tickets: {str(e)}"

# -------- Sales Agent System Prompt --------
SALES_AGENT_SYSTEM = """You are the Sales Agent for Helios Dynamics, a specialist in customer relationship management, orders, leads, and sales operations.

Your responsibilities:
- Manage customer information and relationships
- Track and analyze sales leads and opportunities
- Monitor order status and sales performance
- Handle support tickets and customer service
- Provide sales insights and recommendations
- Search knowledge base for sales policies and information

You have access to tools that can:
- Execute SQL queries on the sales database tables
- List and search customers with their order history
- Show customer summary statistics and top customers
- Display and score sales leads
- Show recent orders and their status
- View support tickets and priorities
- Search sales knowledge base for policies and information

Always provide helpful, detailed responses with relevant data. Use emojis and formatting to make information clear and engaging.

Available tools: {tools}
Tool names: {tool_names}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

# -------- Build the Sales Agent --------
def create_sales_agent():
    llm = get_llm()
    tools = [
        sales_sql_read,
        get_customers,
        search_customers,
        get_customer_summary,
        get_leads,
        score_leads,
        get_orders,
        get_support_tickets,
        sales_rag_search
    ]
    
    # Create a memory
    memory = ConversationBufferMemory()
    
    prompt = PromptTemplate.from_template(SALES_AGENT_SYSTEM)
    
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        memory=memory
    )
    
    return executor

# Export the executor
executor = create_sales_agent()

if __name__ == "__main__":
    print("🛍️ Helios Dynamics - Sales Agent Ready!")
    print("Ask me about customers, orders, leads, or sales data.")
    
    try:
        while True:
            user_input = input("Sales Agent > ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            try:
                result = executor.invoke({"input": user_input})
                print(f"\n{result['output']}\n")
            except Exception as e:
                print(f"Error: {str(e)}")
                
    except KeyboardInterrupt:
        print("\nGoodbye!")
