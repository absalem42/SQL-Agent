#!/usr/bin/env python3
"""
Quick Start Script for ERP System

This script provides a simple way to test the ERP system locally
without setting up the full web interface.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_system():
    """Test the core system components"""
    print("🏢 ERP System Quick Test")
    print("=" * 50)
    
    try:
        # Test database connection
        print("📊 Testing database connection...")
        from backend.db import get_db
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            customer_count = cursor.fetchone()[0]
            print(f"✅ Database connected: {customer_count} customers found")
        
        # Test LLM connection
        print("\n🤖 Testing LLM connection...")
        from backend.config.llm import get_llm
        llm = get_llm()
        print(f"✅ LLM initialized: {type(llm).__name__}")
        
        # Test router agent
        print("\n🔀 Testing router agent...")
        from backend.agents.simple_router_agent import create_simple_router_agent
        agent = create_simple_router_agent()
        
        # Test query
        test_query = "system info"
        print(f"🔍 Testing query: '{test_query}'")
        result = agent.invoke({"input": test_query})
        print(f"📋 Response: {result['output'][:200]}...")
        
        print("\n✅ All systems operational!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def interactive_mode():
    """Run interactive chat mode"""
    print("\n🎯 Interactive Mode")
    print("Type 'quit' to exit")
    print("-" * 30)
    
    try:
        from backend.agents.simple_router_agent import create_simple_router_agent
        agent = create_simple_router_agent()
        
        while True:
            query = input("\n💬 Your query: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if query:
                try:
                    result = agent.invoke({"input": query})
                    print(f"\n🤖 Response:\n{result['output']}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Failed to start interactive mode: {e}")

def main():
    """Main entry point"""
    print("🚀 ERP System Quick Start")
    print("Choose an option:")
    print("1. Run system test")
    print("2. Interactive chat mode")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_system()
    elif choice == "2":
        interactive_mode()
    elif choice == "3":
        if test_system():
            interactive_mode()
    else:
        print("Invalid choice. Running system test...")
        test_system()

if __name__ == "__main__":
    main()
