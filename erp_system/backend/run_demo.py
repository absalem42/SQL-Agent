#!/usr/bin/env python3
"""
Demo script for the ERP system that works without complex agents
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def demo_simple_sales_agent():
    """Demo the simple sales agent with interactive mode"""
    print("🛍️ Helios Dynamics ERP - Sales Agent Demo")
    print("=" * 50)
    
    from agents.sales_agent_simple import SimpleSalesAgent
    
    agent = SimpleSalesAgent()
    
    demo_queries = [
        "show customers",
        "customer summary", 
        "show leads",
        "show orders",
        "search customer sara"
    ]
    
    print("\n📋 Demo Queries:")
    for i, query in enumerate(demo_queries, 1):
        print(f"{i}. {query}")
    
    print("\nRunning demo queries...\n")
    
    for query in demo_queries:
        print(f"🔍 Query: {query}")
        print("-" * 30)
        
        try:
            result = agent.invoke({"input": query})
            output = result['output']
            
            # Show truncated output
            if len(output) > 300:
                print(output[:300] + "...\n")
            else:
                print(output + "\n")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
    
    # Interactive mode
    print("🎮 Interactive Mode (type 'quit' to exit):")
    try:
        while True:
            user_input = input("Sales Agent > ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            try:
                result = agent.invoke({"input": user_input})
                print(f"\n{result['output']}\n")
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")
                
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")

def demo_database_access():
    """Demo direct database access"""
    print("\n📊 Database Access Demo")
    print("=" * 30)
    
    try:
        from tools.sales_tools import SalesTools
        
        sales_tools = SalesTools()
        
        # Show some quick stats
        print("📈 Quick Stats:")
        
        customers = sales_tools.sales_sql_read("SELECT COUNT(*) as count FROM customers")
        print(f"Total Customers: {customers[0]['count'] if customers else 'Error'}")
        
        orders = sales_tools.sales_sql_read("SELECT COUNT(*) as count FROM orders")
        print(f"Total Orders: {orders[0]['count'] if orders else 'Error'}")
        
        leads = sales_tools.sales_sql_read("SELECT COUNT(*) as count FROM leads")
        print(f"Total Leads: {leads[0]['count'] if leads else 'Error'}")
        
        # Show recent activity
        print("\n💼 Recent Activity:")
        recent_customers = sales_tools.sales_sql_read("""
            SELECT name, email, created_at 
            FROM customers 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        
        if recent_customers:
            print("Recent Customers:")
            for customer in recent_customers:
                print(f"  • {customer['name']} ({customer['email']}) - {customer['created_at']}")
        
    except Exception as e:
        print(f"❌ Database Demo Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Helios Dynamics ERP System Demo\n")
    
    # Run database demo first
    demo_database_access()
    
    # Run sales agent demo
    demo_simple_sales_agent()
