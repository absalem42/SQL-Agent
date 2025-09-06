import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sales_tools import SalesTools

def test_sales_tools():
    tools = SalesTools()
    response = tools.handle("show customers")
    assert isinstance(response, str)
    assert "customer" in response.lower()