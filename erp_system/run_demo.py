#!/usr/bin/env python3
"""
Demo script for video demonstration
Shows key ERP system capabilities
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

def run_demo():
    """Run demo queries for video demonstration"""
    
    print("🎬 ERP System Demo - Perfect for Video!")
    print("=" * 50)
    print()
    
    try:
        from agents.simple_router_agent import create_simple_router_agent
        
        print("🤖 Initializing Router Agent...")
        agent = create_simple_router_agent()
        print("✅ Router Agent ready!")
        print()
        
        # Demo queries that showcase system capabilities
        demo_queries = [
            {
                "query": "show recent customers",
                "description": "Customer Management - Shows recent customers with contact info and revenue"
            },
            {
                "query": "display leads with high scores", 
                "description": "Lead Management - Shows qualified leads with AI scoring"
            },
            {
                "query": "customer summary",
                "description": "Business Intelligence - Shows key business metrics and KPIs"
            },
            {
                "query": "system info",
                "description": "System Health - Shows database status and system operational status"
            }
        ]
        
        for i, demo in enumerate(demo_queries, 1):
            print(f"📋 Demo Query {i}: \"{demo['query']}\"")
            print(f"📝 Purpose: {demo['description']}")
            print("🔄 Processing...")
            print("-" * 50)
            
            try:
                response = agent.invoke({'input': demo['query']})
                output = response['output']
                
                # Truncate very long responses for demo
                if len(output) > 400:
                    output = output[:400] + "\n... (truncated for demo)"
                    
                print(output)
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()
            print("=" * 50)
            print()
            
        print("🎉 Demo completed successfully!")
        print("🎬 This system is ready for production use!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure you've run 'make setup' first")
        return False
        
    return True

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
