#!/usr/bin/env python3
"""
Quick Sales Agent Test
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from agents.sales_agent_simple import SimpleSalesAgent

def main():
    print("🛍️ Testing Sales Agent")
    print("=" * 40)
    
    # Initialize Sales Agent
    try:
        sales_agent = SimpleSalesAgent()
        print("✅ Sales Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Sales Agent: {e}")
        return
    
    # Test questions
    test_questions = [
        "show customers",
        "Show me all customers", 
        "How many customers do we have?",
        "Show recent orders"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 30)
        try:
            response = sales_agent.chat(question)
            print(f"Response: {response[:300]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
