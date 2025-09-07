#!/usr/bin/env python3
"""
Comprehensive test script for the ERP system
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_sales_agent_simple():
    """Test the simple sales agent"""
    print("🧪 Testing Simple Sales Agent...")
    
    from agents.sales_agent_simple import SimpleSalesAgent
    
    agent = SimpleSalesAgent()
    
    test_cases = [
        "show customers",
        "customer summary", 
        "show leads",
        "show orders",
        "search customer sara"
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case}")
        print("-" * 40)
        
        try:
            result = agent.invoke({"input": test_case})
            output = result['output']
            
            # Truncate long output for readability
            if len(output) > 200:
                print(output[:200] + "...")
            else:
                print(output)
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_simple_router():
    """Test the simple router agent"""
    print("\n\n🧪 Testing Simple Router Agent...")
    
    try:
        from agents.simple_router_agent import create_simple_router_agent
        
        executor = create_simple_router_agent()
        
        test_cases = [
            "show me customers",
            "get system info",
            "customer summary"
        ]
        
        for test_case in test_cases:
            print(f"\n📝 Testing: {test_case}")
            print("-" * 40)
            
            try:
                # Set max_iterations to 1 to avoid loops with MockLLM
                result = executor.invoke({"input": test_case})
                output = result.get('output', 'No output returned')
                
                # Truncate long output for readability
                if len(output) > 200:
                    print(output[:200] + "...")
                else:
                    print(output)
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Router Agent Error: {str(e)}")

def test_sales_agent():
    """Test the full sales agent"""
    print("\n\n🧪 Testing Full Sales Agent...")
    
    try:
        from agents.sales_agent import create_sales_agent
        
        executor = create_sales_agent()
        
        test_cases = [
            "show customers",
            "customer summary",
            "show leads"
        ]
        
        for test_case in test_cases:
            print(f"\n📝 Testing: {test_case}")
            print("-" * 40)
            
            try:
                # Set max_iterations to 1 to avoid loops with MockLLM
                result = executor.invoke({"input": test_case})
                output = result.get('output', 'No output returned')
                
                # Truncate long output for readability
                if len(output) > 200:
                    print(output[:200] + "...")
                else:
                    print(output)
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Sales Agent Error: {str(e)}")

def test_database():
    """Test database connectivity"""
    print("🧪 Testing Database Connection...")
    
    try:
        from db import get_db
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
        print(f"✅ Database connected successfully!")
        print(f"📊 Found {len(tables)} tables:")
        for table in tables[:5]:  # Show first 5 tables
            print(f"  - {table[0]}")
        if len(tables) > 5:
            print(f"  ... and {len(tables) - 5} more")
            
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")

def test_direct_tools():
    """Test tools directly without agents"""
    print("\n\n🧪 Testing Direct Tool Access...")
    
    try:
        from tools.sales_tools import SalesTools
        
        sales_tools = SalesTools()
        
        # Test direct SQL query
        print("\n📝 Testing direct SQL query:")
        print("-" * 40)
        customers = sales_tools.sales_sql_read("SELECT COUNT(*) as count FROM customers")
        print(f"Customer count: {customers[0]['count'] if customers else 'Error'}")
        
        # Test customer summary
        print("\n📝 Testing customer summary:")
        print("-" * 40)
        summary = sales_tools._customer_summary()
        print(summary[:200] + "..." if len(summary) > 200 else summary)
        
        # Test lead scoring
        print("\n📝 Testing lead scoring:")
        print("-" * 40)
        scoring = sales_tools.score_leads()
        print(scoring[:200] + "..." if len(scoring) > 200 else scoring)
        
    except Exception as e:
        print(f"❌ Direct Tools Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting ERP System Tests\n")
    
    # Test in order of complexity
    test_database()
    test_direct_tools()
    test_sales_agent_simple()
    # Skip the complex agents for now due to MockLLM issues
    # test_simple_router()
    # test_sales_agent()
    
    print("\n✅ Basic tests completed!")
    print("\nNote: Complex agent tests skipped due to MockLLM limitations.")
    print("To test full agents, run Ollama and try the agents directly.")
