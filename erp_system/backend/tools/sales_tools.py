from db import get_db

class SalesTools:
    """Sales and CRM related tools"""
    
    def handle(self, text: str) -> str:
        """Handle sales-related requests"""
        text_lower = text.lower()
        
        if 'customer' in text_lower:
            return self.get_customers_summary()
        elif 'order' in text_lower:
            return self.get_orders_summary()
        elif 'lead' in text_lower:
            return self.get_leads_summary()
        else:
            return "I can help you with customers, orders, and leads. What would you like to know?"
    
    def get_customers_summary(self) -> str:
        """Get summary of customers"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get customer count
            cursor.execute("SELECT COUNT(*) as count FROM customers")
            customer_count = cursor.fetchone()['count']
            
            # Get recent customers
            cursor.execute("SELECT name, email FROM customers ORDER BY created_at DESC LIMIT 5")
            recent_customers = cursor.fetchall()
            
            response = f"**Customer Summary:**\n"
            response += f"Total customers: {customer_count}\n\n"
            response += "Recent customers:\n"
            
            for customer in recent_customers:
                response += f"• {customer['name']} ({customer['email']})\n"
            
            return response
    
    def get_orders_summary(self) -> str:
        """Get summary of orders"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get order stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_revenue
                FROM orders
            """)
            stats = cursor.fetchone()
            
            # Get recent orders
            cursor.execute("""
                SELECT o.order_number, c.name, o.total_amount, o.status
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                ORDER BY o.created_at DESC LIMIT 5
            """)
            recent_orders = cursor.fetchall()
            
            response = f"**Orders Summary:**\n"
            response += f"Total orders: {stats['total_orders']}\n"
            response += f"Total revenue: ${stats['total_revenue']:.2f}\n\n"
            response += "Recent orders:\n"
            
            for order in recent_orders:
                response += f"• {order['order_number']} - {order['name']} - ${order['total_amount']:.2f} ({order['status']})\n"
            
            return response
    
    def get_leads_summary(self) -> str:
        """Get summary of leads"""
        return "Lead management coming soon! Currently showing customer and order data."