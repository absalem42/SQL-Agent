from db import get_db

class InventoryTools:
    """Inventory and supply chain related tools"""
    
    def handle(self, text: str) -> str:
        """Handle inventory-related requests"""
        text_lower = text.lower()
        
        if 'product' in text_lower:
            return self.get_products_summary()
        elif 'stock' in text_lower or 'inventory' in text_lower:
            return self.get_stock_summary()
        elif 'low stock' in text_lower:
            return self.get_low_stock_alert()
        else:
            return "I can help you with products, stock levels, and inventory. What would you like to know?"
    
    def get_products_summary(self) -> str:
        """Get summary of products"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get product count
            cursor.execute("SELECT COUNT(*) as count FROM products")
            product_count = cursor.fetchone()['count']
            
            # Get recent products
            cursor.execute("SELECT sku, name, price FROM products ORDER BY created_at DESC LIMIT 5")
            recent_products = cursor.fetchall()
            
            response = f"**Product Summary:**\n"
            response += f"Total products: {product_count}\n\n"
            response += "Recent products:\n"
            
            for product in recent_products:
                response += f"• {product['sku']} - {product['name']} (${product['price']:.2f})\n"
            
            return response
    
    def get_stock_summary(self) -> str:
        """Get stock level summary"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(stock_quantity) as total_stock,
                    AVG(stock_quantity) as avg_stock
                FROM products
            """)
            stats = cursor.fetchone()
            
            response = f"**Stock Summary:**\n"
            response += f"Total products: {stats['total_products']}\n"
            response += f"Total stock: {stats['total_stock']} units\n"
            response += f"Average stock per product: {stats['avg_stock']:.1f} units\n"
            
            return response
    
    def get_low_stock_alert(self) -> str:
        """Get low stock alerts"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sku, name, stock_quantity
                FROM products
                WHERE stock_quantity < 20
                ORDER BY stock_quantity ASC
            """)
            low_stock_products = cursor.fetchall()
            
            if not low_stock_products:
                return "✅ All products have adequate stock levels!"
            
            response = f"🚨 **Low Stock Alert:**\n"
            response += f"Found {len(low_stock_products)} products with low stock:\n\n"
            
            for product in low_stock_products:
                response += f"• {product['sku']} - {product['name']} ({product['stock_quantity']} units)\n"
            
            return response