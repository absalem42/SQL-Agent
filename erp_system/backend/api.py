from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
from pathlib import Path
import json
import asyncio

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import agents with error handling
try:
    from agents.simple_router_agent import executor as router_executor
    ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Router agent not available: {e}")
    router_executor = None
    ROUTER_AVAILABLE = False

try:
    from agents.sales_agent_simple import SimpleSalesAgent
    sales_agent = SimpleSalesAgent()
    SALES_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Sales agent not available: {e}")
    sales_agent = None
    SALES_AGENT_AVAILABLE = False

from db import get_db
from tools.sales_tools import SalesTools

app = FastAPI(
    title="Helios Dynamics ERP API",
    description="Agent-driven ERP system API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
if (frontend_path.exists()):
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    agent: Optional[str] = "router"

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    execution_time: float

class QueryRequest(BaseModel):
    query: str
    table: Optional[str] = None

# Global instances
sales_tools = SalesTools()

@app.get("/")
async def root():
    """Serve the main application"""
    if frontend_path.exists() and (frontend_path / "index.html").exists():
        return FileResponse(str(frontend_path / "index.html"))
    else:
        return {
            "message": "Helios Dynamics ERP API",
            "version": "1.0.0",
            "status": "active",
            "frontend": "not_found",
            "note": "Frontend files not found. API endpoints available at /docs"
        }

@app.get("/api")
async def api_root():
    return {
        "message": "Helios Dynamics ERP API",
        "version": "1.0.0",
        "status": "active",
        "agents": {
            "router": "available" if ROUTER_AVAILABLE else "unavailable",
            "sales": "available" if SALES_AGENT_AVAILABLE else "unavailable"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            customer_count = cursor.fetchone()[0]
        
        return {
            "status": "healthy",
            "database": "connected",
            "customer_count": customer_count,
            "agents": {
                "router": "available" if ROUTER_AVAILABLE else "unavailable",
                "sales": "available" if SALES_AGENT_AVAILABLE else "unavailable"
            },
            "frontend": "available" if frontend_path.exists() else "unavailable"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with the ERP agents"""
    import time
    start_time = time.time()
    
    try:
        print(f"Received chat request: agent={request.agent}, message='{request.message}'")
        
        # Handle different agent types
        if request.agent == "sales" and SALES_AGENT_AVAILABLE:
            print("Using Sales Agent directly")
            result = sales_agent.invoke({"input": request.message})
            response = result['output']
            agent_used = "sales"
            
        elif request.agent == "analytics":
            response = "Analytics Agent is coming soon! For now, you can ask sales-related questions."
            agent_used = "analytics"
            
        elif request.agent == "finance":
            response = "Finance Agent is coming soon! For now, you can ask sales-related questions."
            agent_used = "finance"
            
        elif request.agent == "inventory":
            response = "Inventory Agent is coming soon! For now, you can ask sales-related questions."
            agent_used = "inventory"
            
        elif ROUTER_AVAILABLE:
            print("Using Router Agent")
            result = router_executor.invoke({"input": request.message})
            response = result['output']
            agent_used = "router"
            
        elif SALES_AGENT_AVAILABLE:
            print("Fallback to Sales Agent")
            result = sales_agent.invoke({"input": request.message})
            response = result['output']
            agent_used = "sales"
            
        else:
            response = "Sorry, no agents are currently available. Please check the system configuration."
            agent_used = "none"
        
        execution_time = time.time() - start_time
        print(f"Response generated in {execution_time:.2f}s by {agent_used} agent")
        
        return ChatResponse(
            response=response,
            agent_used=agent_used,
            execution_time=execution_time
        )
    
    except Exception as e:
        print(f"Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List available agents and their status"""
    agents = []
    
    if SALES_AGENT_AVAILABLE:
        agents.append({
            "name": "sales",
            "description": "Sales and CRM management agent",
            "status": "active",
            "capabilities": ["customer_management", "lead_scoring", "order_tracking"]
        })
    
    if ROUTER_AVAILABLE:
        agents.append({
            "name": "router",
            "description": "Smart router that routes requests to appropriate agents",
            "status": "active",
            "capabilities": ["routing", "logging", "approvals"]
        })
    
    return {"agents": agents}

@app.get("/customers")
async def get_customers(limit: int = 10):
    """Get customer list"""
    try:
        if SALES_AGENT_AVAILABLE:
            result = sales_agent.invoke({"input": "show customers"})
            return {"data": result['output'], "limit": limit}
        else:
            # Direct database query fallback
            customers = sales_tools.sales_sql_read(f"SELECT * FROM customers LIMIT {limit}")
            return {"data": str(customers), "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customers: {str(e)}")

@app.get("/customers/summary")
async def get_customer_summary():
    """Get customer summary statistics"""
    try:
        if SALES_AGENT_AVAILABLE:
            result = sales_agent.invoke({"input": "customer summary"})
            return {"summary": result['output']}
        else:
            # Direct summary
            summary = sales_tools._customer_summary()
            return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customer summary: {str(e)}")

@app.get("/leads")
async def get_leads():
    """Get leads list"""
    try:
        if SALES_AGENT_AVAILABLE:
            result = sales_agent.invoke({"input": "show leads"})
            return {"data": result['output']}
        else:
            # Direct database query
            leads = sales_tools.sales_sql_read("SELECT * FROM leads LIMIT 10")
            return {"data": str(leads)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting leads: {str(e)}")

@app.post("/leads/score")
async def score_leads():
    """Score all leads"""
    try:
        result = sales_tools.score_leads()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring leads: {str(e)}")

@app.get("/orders")
async def get_orders():
    """Get orders list"""
    try:
        if SALES_AGENT_AVAILABLE:
            result = sales_agent.invoke({"input": "show orders"})
            return {"data": result['output']}
        else:
            # Direct database query
            orders = sales_tools.sales_sql_read("SELECT * FROM orders LIMIT 10")
            return {"data": str(orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting orders: {str(e)}")

@app.post("/query", response_model=Dict)
async def execute_query(request: QueryRequest):
    """Execute SQL query"""
    try:
        if not request.query.strip().upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
        
        results = sales_tools.sales_sql_read(request.query)
        return {"results": results, "row_count": len(results)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/database/tables")
async def get_database_tables():
    """Get list of database tables"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
        
        return {"tables": tables, "count": len(tables)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/database/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            stats = {}
            tables = ["customers", "orders", "leads", "products", "invoices"]
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[table] = count
                except:
                    stats[table] = 0
        
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database stats error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Helios Dynamics ERP API Server...")
    print("📊 Frontend available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print(f"🤖 Sales Agent: {'✅ Available' if SALES_AGENT_AVAILABLE else '❌ Unavailable'}")
    print(f"🔀 Router Agent: {'✅ Available' if ROUTER_AVAILABLE else '❌ Unavailable'}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
