import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sales_tools import SalesTools

def test_sales_tools():
    print("💼 Testing Sales Tools...")
    sales = SalesTools()
    
    # Test different sales queries
    test_queries = [
        "show me customers",
        "list all customers", 
        "find customer john",
        "show customer details",
        "add new customer",
        "customer statistics",
        "recent orders"
    ]
    
    print("\n📋 Testing sales queries:")
    for query in test_queries:
        try:
            response = sales.handle(query)
            print(f"  ✅ '{query}' -> {response[:60]}...")
        except Exception as e:
            print(f"  ❌ '{query}' -> Error: {e}")
    
    # Test specific methods if they exist
    print("\n🔍 Testing specific methods:")
    try:
        if hasattr(sales, 'get_customers'):
            customers = sales.get_customers()
            print(f"  ✅ get_customers() -> Found {len(customers) if customers else 0} customers")
        else:
            print("  ⚠️  get_customers() method not found")
            
        if hasattr(sales, 'search_customers'):
            results = sales.search_customers("john")
            print(f"  ✅ search_customers('john') -> Found {len(results) if results else 0} results")
        else:
            print("  ⚠️  search_customers() method not found")
            
    except Exception as e:
        print(f"  ❌ Method test error: {e}")
    
    print("\n🎉 Sales tools tests completed!")

if __name__ == "__main__":
    test_sales_tools()