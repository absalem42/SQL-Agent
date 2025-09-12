import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fix: Import from db module instead of config.database
from db import get_db
from tools.sales_tools import SalesTools
from memory.base_memory import SalesEntityMemory, RouterGlobalState
from langchain.memory import ConversationBufferMemory

class SimpleSalesAgent:
    """Working sales agent that uses the actual database schema"""
    
    def __init__(self):
        self.sales_tools = SalesTools()
        self.entity_memory = SalesEntityMemory()
        self.conversation_memory = ConversationBufferMemory(return_messages=True)
        self.global_state = RouterGlobalState()
    
    def _get_customers(self) -> str:
        """Get customers list with their order information"""
        try:
            # Query using the correct schema
            results = self.sales_tools.sales_sql_read("""
                SELECT c.*, COUNT(o.id) as order_count,
                       COALESCE(SUM(o.total), 0) as total_spent
                FROM customers c 
                LEFT JOIN orders o ON c.id = o.customer_id 
                GROUP BY c.id 
                ORDER BY c.created_at DESC 
                LIMIT 10
            """)
            
            if not results or "error" in str(results).lower():
                # Fallback - simple customer list
                results = self.sales_tools.sales_sql_read("""
                    SELECT * FROM customers 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                
                if results and "error" not in str(results).lower():
                    result = "📋 **Recent Customers:**\n\n"
                    for customer in results:
                        result += f"• **{customer.get('name', 'N/A')}** ({customer.get('email', 'N/A')})\n"
                        result += f"  📞 {customer.get('phone', 'N/A')}\n\n"
                    return result
                else:
                    return "❌ No customers found"
            
            result = "📋 **Recent Customers:**\n\n"
            for customer in results:
                result += f"• **{customer['name']}** ({customer['email']})\n"
                result += f"  📞 {customer.get('phone', 'N/A')}\n"
                result += f"  📦 {customer['order_count']} orders | 💰 ${customer['total_spent']:.2f}\n"
                result += f"  📅 Customer since: {customer.get('created_at', 'N/A')}\n\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error getting customers: {str(e)}"
    
    def _get_customer_summary(self) -> str:
        """Get customer summary statistics"""
        try:
            # Get total customer count
            total_count = self.sales_tools.sales_sql_read("SELECT COUNT(*) as count FROM customers")
            count = total_count[0]['count'] if total_count else 0
            
            # Get new customers this month
            new_customers = self.sales_tools.sales_sql_read("""
                SELECT COUNT(*) as count FROM customers
                WHERE created_at >= date('now', 'start of month')
            """)
            new_count = new_customers[0]['count'] if new_customers else 0
            
            # Get customer spending data
            customer_data = self.sales_tools.sales_sql_read("""
                SELECT 
                    COUNT(DISTINCT c.id) as customer_count,
                    COUNT(o.id) as order_count,
                    COALESCE(SUM(o.total), 0) as total_revenue,
                    COALESCE(AVG(o.total), 0) as avg_order_value
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id
            """)
            
            result = "📊 **Customer Summary:**\n\n"
            result += f"Total Customers: {count}\n"
            result += f"New This Month: {new_count}\n"
            
            if customer_data and len(customer_data) > 0:
                data = customer_data[0]
                result += f"Total Orders: {data.get('order_count', 0)}\n"
                result += f"Total Revenue: ${data.get('total_revenue', 0):.2f}\n"
                result += f"Average Order Value: ${data.get('avg_order_value', 0):.2f}\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting customer summary: {str(e)}"
    
    def _get_leads(self) -> str:
        """Get a list of leads with their status"""
        try:
            leads = self.sales_tools.sales_sql_read("""
                SELECT customer_name, contact_email, status, score, created_at 
                FROM leads
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            if not leads or len(leads) == 0:
                return "No leads found in the system."
            
            result = "🎯 **Recent Leads:**\n\n"
            for lead in leads:
                result += f"• **{lead['customer_name']}** ({lead['contact_email']})\n"
                result += f"  Status: {lead['status']}\n"
                if lead.get('score'):
                    result += f"  Score: {lead['score']:.1f}/10\n"
                result += f"  Created: {lead.get('created_at', 'N/A')}\n\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting leads: {str(e)}"
    
    def _get_orders(self) -> str:
        """Get a list of recent orders"""
        try:
            orders = self.sales_tools.sales_sql_read("""
                SELECT o.id, o.total, o.status, o.created_at,
                       c.name as customer_name
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                ORDER BY o.created_at DESC
                LIMIT 10
            """)
            
            if not orders or len(orders) == 0:
                return "No orders found in the system."
            
            result = "📦 **Recent Orders:**\n\n"
            for order in orders:
                result += f"Order #{order['id']} - {order['status']}\n"
                result += f"Customer: {order['customer_name']}\n"
                result += f"Total: ${order['total']:.2f}\n"
                result += f"Date: {order['created_at']}\n\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting orders: {str(e)}"
    
    def _search_customers(self, search_term: str) -> str:
        """Search for customers by name or email"""
        if not search_term or len(search_term) < 3:
            return "Please provide a search term with at least 3 characters."
        
        try:
            # Extract actual search term if it includes "find customer"
            if "find customer" in search_term.lower():
                search_term = search_term.lower().replace("find customer", "").strip()
            
            results = self.sales_tools.sales_sql_read(f"""
                SELECT c.id, c.name, c.email, c.phone, c.created_at
                FROM customers c 
                WHERE c.name LIKE '%{search_term}%' OR c.email LIKE '%{search_term}%'
                ORDER BY c.name
                LIMIT 5
            """)
            
            if not results or len(results) == 0:
                return f"No customers found matching '{search_term}'."
            
            result = f"🔍 **Search Results for '{search_term}':**\n\n"
            for customer in results:
                result += f"• **{customer['name']}** ({customer['email']})\n"
                result += f"  📞 {customer.get('phone', 'N/A')}\n"
                result += f"  📅 Customer since: {customer.get('created_at', 'N/A')}\n\n"
            
            return result
        except Exception as e:
            return f"❌ Error searching customers: {str(e)}"
    
    def invoke(self, request_data: Dict) -> Dict:
        """Main entry point that processes user requests"""
        user_input = request_data.get('input', '').lower()
        
        try:
            # Simple keyword-based routing
            if 'search' in user_input or 'find' in user_input:
                response = self._search_customers(user_input)
            elif 'lead' in user_input:
                response = self._get_leads()
            elif 'order' in user_input:
                response = self._get_orders()
            elif 'summary' in user_input:
                response = self._get_customer_summary()
            elif 'customer' in user_input:
                response = self._get_customers()
            else:
                response = self._get_help()
            
            return {'output': response}
            
        except Exception as e:
            return {'output': f"❌ Error processing request: {str(e)}"}
    
    def chat(self, message: str) -> str:
        """Chat interface that mimics other agents"""
        try:
            result = self.invoke({"input": message})
            return result.get('output', str(result))
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _get_help(self) -> str:
        """Return help message"""
        return """
🛍️ **Sales Agent - Available Commands:**

**Customer Management:**
• "show customers" - List recent customers with order history
• "customer summary" - Customer statistics  
• "search customer [name]" - Find specific customer

**Sales Operations:**
• "show leads" - Recent leads with status
• "show orders" - Recent orders

**Examples:**
• "Show me customers"
• "Customer summary"
• "Search customer smith"
• "Show me leads"

What would you like to know?
        """

# Create the simple executor
class SimpleExecutor:
    def __init__(self):
        self.agent = SimpleSalesAgent()
    
    def invoke(self, request_data: Dict) -> Dict:
        return self.agent.invoke(request_data)

# Export the executor
executor = SimpleExecutor()

if __name__ == "__main__":
    print("🛍️ Helios Dynamics - Simple Sales Agent Ready!")
    
    agent = SimpleSalesAgent()
    
    try:
        while True:
            user_input = input("Sales > ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            result = agent.invoke({"input": user_input})
            print(f"\n{result['output']}\n")
                
    except KeyboardInterrupt:
        print("\nGoodbye!")
