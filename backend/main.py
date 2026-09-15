import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import init_db, SessionLocal, Product
from backend.seed_data import seed_database
from backend.routers import dashboard, customers, inventory, sales, documents, ai_assistant, reports

# Initialize App & Tables
init_db()

# Check if seed needed
db = SessionLocal()
if db.query(Product).count() == 0:
    print("Database is empty. Auto-seeding initial business data...")
    seed_database()
db.close()

app = FastAPI(
    title="AI Business OS API",
    description="Full-stack AI Business Operating System with CRM, Inventory, Sales, Document Vault, AI Assistant, and Reports.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers first
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(documents.router)
app.include_router(ai_assistant.router)
app.include_router(reports.router)

@app.get("/api/health")
def health_check():
    return {"status": "online", "system": "AI Business OS", "theme": "White & Golden"}

# Mount Static Frontend at Root (must be after /api routes)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

