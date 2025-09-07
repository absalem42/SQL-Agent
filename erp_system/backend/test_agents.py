#!/usr/bin/env python3
"""
Test script for ERP agents without requiring Ollama
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.sales_agent_simple import SimpleSalesAgent

def test_simple_sales_agent():
    """Test the simple sales agent"""
    print("🧪 Testing Simple Sales Agent...")
    
    agent = SimpleSalesAgent()
    
    test_cases = [
        "show customers",
        "customer summary", 
        "show leads",
        "show orders",
        "search customer john"
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case}")
        print("-" * 40)
        
        try:
            result = agent.invoke({"input": test_case})
            output = result['output']
            
            # Truncate long output for readability
            if len(output) > 300:
                print(output[:300] + "...")
            else:
                print(output)
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_simple_sales_agent()
