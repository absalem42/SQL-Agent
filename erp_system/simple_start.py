#!/usr/bin/env python3
"""
Simple starter for ERP system without complex dependencies
"""
import subprocess
import sys
import os

def main():
    print("🏢 Helios Dynamics ERP - Simple Starter")
    print("=" * 45)
    
    print("\n📋 Available options:")
    print("1. Test the system")
    print("2. Run sales agent demo")
    print("3. Start API server")
    print("4. Test database")
    print("5. Install requirements")
    
    choice = input("\nChoose an option (1-5): ").strip()
    
    if choice == "1":
        print("🧪 Testing system...")
        subprocess.run([sys.executable, "backend/test_system.py"])
    
    elif choice == "2":
        print("🛍️ Running sales agent demo...")
        subprocess.run([sys.executable, "backend/agents/sales_agent_simple.py"])
    
    elif choice == "3":
        print("🌐 Starting API server...")
        print("API will be available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop")
        subprocess.run([sys.executable, "backend/api.py"])
    
    elif choice == "4":
        print("🗄️ Testing database...")
        try:
            sys.path.insert(0, "backend")
            from db import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM customers")
                count = cursor.fetchone()[0]
            print(f"✅ Database connection successful! Found {count} customers.")
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    elif choice == "5":
        print("📦 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
