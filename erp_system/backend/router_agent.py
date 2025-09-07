import sys
from pathlib import Path

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent / 'agents'))

from agents.sales_agent_simple import SimpleSalesAgent

class RouterAgent:
    """Router agent that uses sales_agent_simple"""
    
    def __init__(self):
        self.sales_agent = SimpleSalesAgent()
    
    def handle_request(self, text: str) -> str:
        """Main entry point for handling user requests"""
        try:
            result = self.sales_agent.invoke({"input": text})
            return result.get('output', 'No response from sales agent')
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def route_request(self, text: str) -> str:
        """Legacy method for backward compatibility"""
        return "sales"  # Default routing for backward compatibility