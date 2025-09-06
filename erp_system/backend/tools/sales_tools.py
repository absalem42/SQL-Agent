import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from db import get_db
from mcp.mcp_adapter import mcp_registry

class SalesTools:
    """Sales & CRM Agent with SQL, RAG, and lead scoring capabilities"""
    
    def __init__(self):
        self.conversation_buffer = []  # Simple conversation memory
        self.entity_memory = {}  # Customer-specific memory
        self.max_buffer_size = 5
        self._register_tools()
        
    def _register_tools(self):
        """Register all sales tools with MCP"""
        mcp_registry.register_tool(
            'sales_sql_read',
            self.sales_sql_read,
            'Execute read-only SQL queries for sales data',
            {'query': 'SQL query string'}
        )
        
        mcp_registry.register_tool(
            'sales_sql_write', 
            self.sales_sql_write,
            'Execute write SQL queries for sales data',
            {'query': 'SQL query string', 'params': 'Query parameters'}
        )
        
        mcp_registry.register_tool(
            'sales_rag_search',
            self.sales_rag_search,
            'Search sales knowledge base using RAG',
            {'query': 'Search query string'}
        )
        
        mcp_registry.register_tool(
            'score_leads',
            self.score_leads,
            'Score leads using ML model',
            {}
        )
        
    def handle(self, text: str) -> str:
        """Main handler for sales-related requests"""
        text_lower = text.lower()
        
        # Store in conversation buffer
        self._add_to_buffer(text)
        
        # Route to appropriate tool based on keywords
        if any(word in text_lower for word in ['customer', 'customers', 'client', 'clients']):
            return self._handle_customer_query(text)
        elif any(word in text_lower for word in ['lead', 'leads', 'prospect']):
            return self._handle_lead_query(text)
        elif any(word in text_lower for word in ['order', 'orders', 'purchase']):
            return self._handle_order_query(text)
        elif any(word in text_lower for word in ['ticket', 'support', 'issue']):
            return self._handle_support_query(text)
        elif any(word in text_lower for word in ['score', 'scoring', 'qualify']):
            return self._handle_lead_scoring(text)
        else:
            return self._general_sales_help()
    
    def _add_to_buffer(self, text: str):
        """Add message to conversation buffer"""
        self.conversation_buffer.append({
            'timestamp': datetime.now().isoformat(),
            'message': text
        })
        if len(self.conversation_buffer) > self.max_buffer_size:
            self.conversation_buffer.pop(0)
    
    def _handle_customer_query(self, text: str) -> str:
        """Handle customer-related queries"""
        if 'add' in text.lower() or 'create' in text.lower():
            return self._suggest_add_customer()
        elif 'search' in text.lower() or 'find' in text.lower():
            return self._search_customers(text)
        elif 'summary' in text.lower() or 'stats' in text.lower():
            return self._customer_summary()
        else:
            return self._list_customers()
    
    def _handle_lead_query(self, text: str) -> str:
        """Handle lead-related queries"""
        if 'add' in text.lower() or 'create' in text.lower():
            return "To add a new lead, I need: name, email, phone, and source. Please provide these details."
        else:
            return self._list_leads()
    
    def _handle_order_query(self, text: str) -> str:
        """Handle order-related queries"""
        if 'add' in text.lower() or 'create' in text.lower():
            return "To create a new order, I need customer ID and product details. What would you like to order?"
        else:
            return self._list_recent_orders()
    
    def _handle_support_query(self, text: str) -> str:
        """Handle support ticket queries"""
        return self._list_tickets()
    
    def _handle_lead_scoring(self, text: str) -> str:
        """Handle lead scoring requests"""
        return self.score_leads()
    
    # SQL Tools
    def sales_sql_read(self, query: str) -> List[Dict]:
        """Execute read-only SQL queries for sales data"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]
    
    def sales_sql_write(self, query: str, params: tuple = ()) -> Dict:
        """Execute write SQL queries for sales data"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return {"success": True, "rowcount": cursor.rowcount}
        except Exception as e:
            return {"error": str(e)}
    
    # Customer Management
    def _customer_summary(self) -> str:
        """Get customer summary statistics"""
        try:
            total_customers = self.sales_sql_read("SELECT COUNT(*) as count FROM customers")[0]['count']
            recent_customers = self.sales_sql_read(
                "SELECT COUNT(*) as count FROM customers WHERE created_at >= date('now', '-30 days')"
            )[0]['count']
            
            # Get customer with most orders
            top_customer = self.sales_sql_read("""
                SELECT c.name, COUNT(o.id) as order_count 
                FROM customers c 
                LEFT JOIN orders o ON c.id = o.customer_id 
                GROUP BY c.id, c.name 
                ORDER BY order_count DESC 
                LIMIT 1
            """)
            
            result = f"""
📊 **Customer Summary:**
• Total customers: {total_customers}
• New this month: {recent_customers}
• Top customer: {top_customer[0]['name'] if top_customer else 'N/A'} ({top_customer[0]['order_count'] if top_customer else 0} orders)

💡 Use 'show customers' to see detailed list or 'find customer [name]' to search.
            """
            return result.strip()
            
        except Exception as e:
            return f"❌ Error getting customer summary: {str(e)}"
    
    def _list_customers(self) -> str:
        """List recent customers with details"""
        customers = self.sales_sql_read("""
            SELECT c.*, COUNT(o.id) as order_count, 
                   COALESCE(SUM(o.total_amount), 0) as total_spent
            FROM customers c 
            LEFT JOIN orders o ON c.id = o.customer_id 
            GROUP BY c.id 
            ORDER BY c.created_at DESC 
            LIMIT 10
        """)
        
        if not customers or (len(customers) == 1 and "error" in customers[0]):
            return "❌ No customers found or database error."
        
        result = "📋 **Recent Customers:**\n\n"
        for customer in customers:
            result += f"• **{customer['name']}** ({customer['email']})\n"
            result += f"  📞 {customer.get('phone', 'N/A')} | 📍 {customer.get('address', 'N/A')}\n"
            result += f"  📦 {customer['order_count']} orders | 💰 ${customer['total_spent']:.2f} total\n"
            result += f"  📅 Customer since: {customer['created_at']}\n\n"
        
        return result
    
    def _search_customers(self, text: str) -> str:
        """Search customers by name or email"""
        words = text.split()
        search_term = None
        for i, word in enumerate(words):
            if word.lower() in ['find', 'search'] and i + 1 < len(words):
                search_term = words[i + 1]
                break
        
        if not search_term:
            return "Please specify what to search for. Example: 'find customer john'"
        
        customers = self.sales_sql_read(f"""
            SELECT c.*, COUNT(o.id) as order_count 
            FROM customers c 
            LEFT JOIN orders o ON c.id = o.customer_id 
            WHERE c.name LIKE '%{search_term}%' OR c.email LIKE '%{search_term}%' 
            GROUP BY c.id 
            ORDER BY c.created_at DESC
        """)
        
        if not customers:
            return f"❌ No customers found matching '{search_term}'"
        
        result = f"🔍 **Search Results for '{search_term}':**\n\n"
        for customer in customers:
            result += f"• **{customer['name']}** - {customer['email']}\n"
            result += f"  📦 {customer['order_count']} orders | 📅 {customer['created_at']}\n\n"
        
        return result
    
    def _suggest_add_customer(self) -> str:
        """Suggest how to add a customer"""
        return """
        📝 **To add a new customer, I need:**
        - Full name
        - Email address
        - Phone number
        - Address
        """
    
    # Lead Management
    def _list_leads(self) -> str:
        """List recent leads from database"""
        leads = self.sales_sql_read("""
            SELECT * FROM leads 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        if not leads or (len(leads) == 1 and "error" in leads[0]):
            return "❌ No leads found or database error."
        
        result = "🎯 **Recent Leads:**\n\n"
        for lead in leads:
            status_emoji = "🟢" if lead.get('status') == 'qualified' else "🟡" if lead.get('status') == 'contacted' else "🔴"
            result += f"{status_emoji} **{lead.get('name', 'N/A')}** ({lead.get('email', 'N/A')})\n"
            result += f"  📞 {lead.get('phone', 'N/A')} | 🏢 {lead.get('company', 'N/A')}\n"
            result += f"  📊 Status: {lead.get('status', 'new')} | 💰 Value: ${lead.get('estimated_value', 0)}\n"
            result += f"  📅 Created: {lead.get('created_at', 'N/A')}\n\n"
        
        return result
    
    # Order Management  
    def _list_recent_orders(self) -> str:
        """List recent orders from database"""
        orders = self.sales_sql_read("""
            SELECT o.*, c.name as customer_name 
            FROM orders o 
            LEFT JOIN customers c ON o.customer_id = c.id 
            ORDER BY o.created_at DESC 
            LIMIT 10
        """)
        
        if not orders or (len(orders) == 1 and "error" in orders[0]):
            return "❌ No orders found or database error."
        
        result = "📦 **Recent Orders:**\n\n"
        for order in orders:
            status_emoji = "✅" if order.get('status') == 'completed' else "🟡" if order.get('status') == 'processing' else "🔴"
            result += f"{status_emoji} **Order #{order.get('id')}** - {order.get('customer_name', 'Unknown')}\n"
            result += f"  💰 ${order.get('total_amount', 0):.2f} | 📊 {order.get('status', 'pending')}\n"
            result += f"  📅 {order.get('created_at', 'N/A')}\n\n"
        
        return result
    
    # Support Tickets
    def _list_tickets(self) -> str:
        """List recent support tickets"""
        tickets = self.sales_sql_read("""
            SELECT t.*, c.name as customer_name 
            FROM tickets t 
            LEFT JOIN customers c ON t.customer_id = c.id 
            ORDER BY t.created_at DESC 
            LIMIT 10
        """)
        
        if not tickets or (len(tickets) == 1 and "error" in tickets[0]):
            return "❌ No tickets found or database error."
        
        result = "🎫 **Recent Support Tickets:**\n\n"
        for ticket in tickets:
            priority_emoji = "🔴" if ticket.get('priority') == 'high' else "🟡" if ticket.get('priority') == 'medium' else "🟢"
            result += f"{priority_emoji} **Ticket #{ticket.get('id')}** - {ticket.get('customer_name', 'Unknown')}\n"
            result += f"  📝 {ticket.get('subject', 'No subject')[:50]}...\n"
            result += f"  📊 {ticket.get('status', 'open')} | ⚡ {ticket.get('priority', 'low')} priority\n"
            result += f"  📅 {ticket.get('created_at', 'N/A')}\n\n"
        
        return result
    
    # Lead Scoring with real data
    def score_leads(self) -> str:
        """Score leads using actual database data"""
        try:
            leads = self.sales_sql_read("""
                SELECT *, 
                       CASE 
                           WHEN estimated_value > 10000 THEN 30
                           WHEN estimated_value > 5000 THEN 20
                           WHEN estimated_value > 1000 THEN 10
                           ELSE 5
                       END as value_score,
                       CASE 
                           WHEN source = 'referral' THEN 25
                           WHEN source = 'website' THEN 15
                           WHEN source = 'cold_call' THEN 10
                           ELSE 5
                       END as source_score
                FROM leads 
                ORDER BY (value_score + source_score) DESC 
                LIMIT 5
            """)
            
            if not leads:
                return "❌ No leads found for scoring."
            
            result = "🎯 **Lead Scoring Results:**\n\n"
            for lead in leads:
                total_score = lead['value_score'] + lead['source_score']
                score_emoji = "🟢" if total_score >= 40 else "🟡" if total_score >= 25 else "🔴"
                result += f"{score_emoji} **{lead['name']}** - Score: {total_score}/55\n"
                result += f"  💰 Value: ${lead.get('estimated_value', 0)} (+{lead['value_score']} pts)\n"
                result += f"  📍 Source: {lead.get('source', 'unknown')} (+{lead['source_score']} pts)\n"
                result += f"  📧 {lead.get('email', 'N/A')}\n\n"
            
            result += "💡 **Recommendation:** Focus on leads with 40+ score (🟢) for highest conversion."
            return result
            
        except Exception as e:
            return f"❌ Error in lead scoring: {str(e)}"
    
    # RAG Simulation
    def sales_rag_search(self, query: str) -> str:
        """Search sales knowledge base using RAG simulation"""
        # Try to search documents table first
        try:
            docs = self.sales_sql_read(f"""
                SELECT * FROM documents 
                WHERE content LIKE '%{query}%' 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            
            if docs and "error" not in docs[0]:
                result = f"📚 **Document Search Results for '{query}':**\n\n"
                for doc in docs:
                    result += f"• **{doc.get('title', 'Untitled')}**\n"
                    result += f"  📝 {doc.get('content', '')[:100]}...\n"
                    result += f"  📅 {doc.get('created_at', 'N/A')}\n\n"
                return result
        except:
            pass
        
        # Fallback to simulated knowledge base
        knowledge_base = {
            "pricing": "Standard pricing: 20% enterprise discount, 10% returning customers.",
            "warranty": "1-year warranty included, extended coverage available up to 3 years.",
            "shipping": "Free shipping on orders >$500. Express delivery +$25.",
            "returns": "30-day return policy for unused items in original packaging.",
            "support": "24/7 support via phone, email, and chat for all customers."
        }
        
        query_lower = query.lower()
        for topic, info in knowledge_base.items():
            if topic in query_lower:
                return f"📚 **Knowledge Base - {topic.title()}:**\n{info}"
        
        return "📚 **Available Topics:** pricing, warranty, shipping, returns, support"
    
    def _general_sales_help(self) -> str:
        """General sales help"""
        return """
💼 **Sales & CRM Assistant - Available Commands:**

**Customer Management:**
• "show customers" - List recent customers with order history
• "customer summary" - Get customer statistics 
• "find customer [name]" - Search for specific customer

**Lead Management:**
• "show leads" - List recent leads with scoring
• "score leads" - Run lead scoring analysis

**Order Management:**
• "show orders" - List recent orders with status

**Support:**
• "support tickets" - View recent support tickets

**Knowledge Search:**
• "search [topic]" - Search knowledge base

What would you like to do?
        """
    
    # Memory Management
    def get_entity_memory(self, customer_id: str) -> Dict:
        """Get stored memory for specific customer"""
        return self.entity_memory.get(customer_id, {})
    
    def update_entity_memory(self, customer_id: str, data: Dict):
        """Update memory for specific customer"""
        if customer_id not in self.entity_memory:
            self.entity_memory[customer_id] = {}
        self.entity_memory[customer_id].update(data)
