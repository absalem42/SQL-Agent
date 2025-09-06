import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router_agent import RouterAgent

def test_router_classification():
    router = RouterAgent()
    
    assert router.route_request("show me customers") == "sales"
    assert router.route_request("list invoices") == "finance"  
    assert router.route_request("check inventory") == "inventory"

def test_router_handle():
    router = RouterAgent()
    response = router.handle_request("what can you do?")
    assert isinstance(response, str)