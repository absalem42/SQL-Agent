import re
from tools.sales_tools import SalesTools
from tools.finance_tools import FinanceTools  
from tools.inventory_tools import InventoryTools

class RouterAgent:
    """Router agent that decides which tool/agent to use based on user input"""
    
    def __init__(self):
        self.sales_tools = SalesTools()
        self.finance_tools = FinanceTools()
        self.inventory_tools = InventoryTools()
        
        # Simple keyword-based routing
        self.routing_patterns = {
            'sales': ['customer', 'lead', 'order', 'sale', 'crm', 'client'],
            'finance': ['invoice', 'payment', 'finance', 'accounting', 'ledger', 'money'],
            'inventory': ['product', 'stock', 'inventory', 'warehouse', 'supply']
        }
    
    def route_request(self, text: str) -> str:
        """Determine which domain the request belongs to"""
        text_lower = text.lower()
        
        scores = {}
        for domain, keywords in self.routing_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[domain] = score
        
        # Return domain with highest score, default to sales
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'sales'
    
    def handle_request(self, text: str) -> str:
        """Main entry point for handling user requests"""
        try:
            domain = self.route_request(text)
            
            # Route to appropriate tool
            if domain == 'sales':
                return self.sales_tools.handle(text)
            elif domain == 'finance':
                return self.finance_tools.handle(text)
            elif domain == 'inventory':
                return self.inventory_tools.handle(text)
            else:
                return "I'm not sure how to help with that. Try asking about customers, orders, invoices, or inventory."
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"