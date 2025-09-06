import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router_agent import RouterAgent

def test_router_agent():
    print("🤖 Testing Router Agent...")
    router = RouterAgent()
    
    # Test routing decisions
    test_cases = [
        ("show me customers", "sales"),
        ("list all invoices", "finance"),
        ("check product inventory", "inventory"),
        ("add new customer", "sales"),
        ("payment status", "finance"),
        ("stock levels", "inventory"),
        ("hello world", "sales")  # default case
    ]
    
    print("\n📋 Testing routing decisions:")
    for text, expected in test_cases:
        result = router.route_request(text)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{text}' -> {result} (expected: {expected})")
    
    # Test actual request handling
    print("\n🎯 Testing request handling:")
    test_requests = [
        "show me all customers",
        "list products in stock", 
        "show pending invoices"
    ]
    
    for request in test_requests:
        try:
            response = router.handle_request(request)
            print(f"  ✅ '{request}' -> {response[:50]}...")
        except Exception as e:
            print(f"  ❌ '{request}' -> Error: {e}")
    
    print("\n🎉 Router tests completed!")

if __name__ == "__main__":
    test_router_agent()