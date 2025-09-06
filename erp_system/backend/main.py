from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import get_db
from router_agent import RouterAgent

app = FastAPI(
    title="Agent-Driven ERP Backend", 
    description="AI-powered ERP system with intelligent routing",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router_agent = RouterAgent()

class ChatMessage(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "ERP Backend is running 🚀", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint for Docker"""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1").fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

@app.post("/chat")
def chat(message: ChatMessage):
    """Main chat endpoint for agent interaction"""
    try:
        response = router_agent.handle_request(message.text)
        return {"response": response, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/customers")
def get_customers():
    """Get all customers"""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM customers LIMIT 50").fetchall()
        return {"customers": [dict(row) for row in rows]}

@app.get("/products")
def get_products():
    """Get all products"""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM products LIMIT 50").fetchall()
        return {"products": [dict(row) for row in rows]}

@app.get("/invoices")
def get_invoices():
    """Get recent invoices"""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM invoices ORDER BY created_at DESC LIMIT 20").fetchall()
        return {"invoices": [dict(row) for row in rows]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)