#!/usr/bin/env python3
"""
Comprehensive Agent Testing Script
Tests all sample questions against the database
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from agents.simple_router_agent import RouterAgent
from agents.sales_agent_simple import SimpleSalesAgent
from agents.AnalyticsAgent import create_analytics_agent_with_chat
from memory.base_memory import RouterGlobalState

def test_agent(agent, agent_name, questions):
    """Test an agent with a list of questions"""
    print(f"\n🧪 Testing {agent_name}")
    print("=" * 50)
    
    results = []
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 40)
        try:
            if hasattr(agent, 'chat'):
                response = agent.chat(question)
            else:
                response = agent.invoke({"input": question})
                response = response.get('output', str(response))
            
            print(f"✅ Response: {response[:200]}...")
            results.append({"question": question, "status": "SUCCESS", "response": response})
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}...")
            results.append({"question": question, "status": "ERROR", "error": str(e)})
    
    return results

def main():
    print("🚀 Comprehensive Agent Testing")
    print("=" * 60)
    
    # Initialize agents
    try:
        router_state = RouterGlobalState()
        router_agent = RouterAgent(router_state)
        sales_agent = SimpleSalesAgent()
        analytics_agent = create_analytics_agent_with_chat()
        print("✅ All agents initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        return
    
    # Sales Agent Test Questions
    sales_questions = [
        "Show me all customers",
        "Find customers with email containing 'gmail'",
        "How many customers do we have?",
        "Show me all leads",
        "List leads with score above 80",
        "Show recent orders",
        "Find orders above $500",
        "Who are our top 5 customers by revenue?",
        "Search for customer 'Mohamed'",
        "Find all orders for customer ID 1"
    ]
    
    # Analytics Agent Test Questions
    analytics_questions = [
        "What's our total revenue?",
        "Show revenue by month",
        "Calculate average revenue per customer",
        "How many orders do we have?",
        "What's the average order value?",
        "How many customers do we have?",
        "Show customer acquisition rate",
        "Run a query to show top customers",
        "Calculate total sales for this year",
        "Create a report for customer trends"
    ]
    
    # Router Agent Test Questions
    router_questions = [
        "What's our system status?",
        "Show me our top customers",
        "What's our revenue?",
        "List all customers",
        "How many orders do we have?",
        "Show me analytics data",
        "Give me sales information",
        "Show system information"
    ]
    
    # Test all agents
    all_results = {}
    
    # Test Sales Agent
    all_results['sales'] = test_agent(sales_agent, "Sales Agent", sales_questions)
    
    # Test Analytics Agent  
    all_results['analytics'] = test_agent(analytics_agent, "Analytics Agent", analytics_questions)
    
    # Test Router Agent
    all_results['router'] = test_agent(router_agent, "Router Agent", router_questions)
    
    # Summary
    print("\n📊 TESTING SUMMARY")
    print("=" * 60)
    
    for agent_name, results in all_results.items():
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        total_count = len(results)
        print(f"{agent_name.upper()}: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")
        
        # Show failed tests
        failed_tests = [r for r in results if r['status'] == 'ERROR']
        if failed_tests:
            print(f"  ❌ Failed tests:")
            for test in failed_tests[:3]:  # Show first 3 failures
                print(f"    • {test['question']}")
                print(f"      Error: {test['error'][:100]}...")

if __name__ == "__main__":
    main()
