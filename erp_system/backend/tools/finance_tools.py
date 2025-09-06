from db import get_db

class FinanceTools:
    """Finance and accounting related tools"""
    
    def handle(self, text: str) -> str:
        """Handle finance-related requests"""
        text_lower = text.lower()
        
        if 'invoice' in text_lower:
            return self.get_invoices_summary()
        elif 'payment' in text_lower:
            return self.get_payments_summary()
        elif 'revenue' in text_lower or 'money' in text_lower:
            return self.get_revenue_summary()
        else:
            return "I can help you with invoices, payments, and revenue. What would you like to know?"
    
    def get_invoices_summary(self) -> str:
        """Get summary of invoices"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get invoice stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_invoices,
                    SUM(total_amount) as total_amount,
                    COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_count,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count
                FROM invoices
            """)
            stats = cursor.fetchone()
            
            # Get recent invoices
            cursor.execute("""
                SELECT invoice_number, total_amount, status, created_at
                FROM invoices
                ORDER BY created_at DESC LIMIT 5
            """)
            recent_invoices = cursor.fetchall()
            
            response = f"**Invoice Summary:**\n"
            response += f"Total invoices: {stats['total_invoices']}\n"
            response += f"Total amount: ${stats['total_amount']:.2f}\n"
            response += f"Paid: {stats['paid_count']} | Pending: {stats['pending_count']}\n\n"
            response += "Recent invoices:\n"
            
            for invoice in recent_invoices:
                response += f"• {invoice['invoice_number']} - ${invoice['total_amount']:.2f} ({invoice['status']})\n"
            
            return response
    
    def get_payments_summary(self) -> str:
        """Get summary of payments"""
        return "Payment tracking coming soon! Currently showing invoice data."
    
    def get_revenue_summary(self) -> str:
        """Get revenue summary"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN status = 'paid' THEN total_amount ELSE 0 END) as paid_revenue,
                    SUM(CASE WHEN status = 'pending' THEN total_amount ELSE 0 END) as pending_revenue
                FROM invoices
            """)
            revenue = cursor.fetchone()
            
            response = f"**Revenue Summary:**\n"
            response += f"Paid revenue: ${revenue['paid_revenue']:.2f}\n"
            response += f"Pending revenue: ${revenue['pending_revenue']:.2f}\n"
            response += f"Total revenue: ${(revenue['paid_revenue'] + revenue['pending_revenue']):.2f}\n"
            
            return response