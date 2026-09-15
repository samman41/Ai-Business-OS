import io
import csv
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db, Customer, Product, Order, OrderItem, SystemSetting, Insight

router = APIRouter(prefix="/api/reports", tags=["Reports & Settings"])

class APIKeyPayload(BaseModel):
    openai_api_key: str

@router.get("/business-summary")
def get_executive_business_summary(db: Session = Depends(get_db)):
    now = datetime.utcnow()

    # Revenue metrics
    rev_query = db.query(
        func.sum(Order.total_amount).label("rev"),
        func.sum(Order.cogs_amount).label("cogs"),
        func.count(Order.id).label("count")
    ).filter(Order.status != "Cancelled").first()

    rev = rev_query.rev or 0.0
    cogs = rev_query.cogs or 0.0
    net_profit = rev - cogs
    margin = (net_profit / rev * 100) if rev > 0 else 0.0

    cust_count = db.query(func.count(Customer.id)).scalar() or 0
    prod_count = db.query(func.count(Product.id)).scalar() or 0
    low_stock = db.query(func.count(Product.id)).filter(Product.stock_qty <= Product.min_stock_threshold).scalar() or 0

    top_customers = db.query(
        Customer.name, Customer.company, func.sum(Order.total_amount).label("spent")
    ).join(Order).group_by(Customer.id).order_by(func.sum(Order.total_amount).desc()).limit(5).all()

    top_products = db.query(
        Product.name, Product.sku, func.sum(OrderItem.quantity).label("sold"), func.sum(OrderItem.total_price).label("rev")
    ).join(OrderItem).group_by(Product.id).order_by(func.sum(OrderItem.total_price).desc()).limit(5).all()

    insights = db.query(Insight).all()

    return {
        "generated_at": now.strftime("%B %d, %Y - %H:%M UTC"),
        "company_name": "AI Business Operating System",
        "financials": {
            "total_revenue": round(rev, 2),
            "cogs": round(cogs, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin_pct": round(margin, 1),
            "total_orders": rev_query.count or 0
        },
        "kpis": {
            "active_customers": cust_count,
            "product_skus": prod_count,
            "low_stock_alerts": low_stock
        },
        "top_customers": [
            {"name": c.name, "company": c.company or "N/A", "spent": round(c.spent, 2)} for c in top_customers
        ],
        "top_products": [
            {"name": p.name, "sku": p.sku, "units_sold": p.sold, "revenue": round(p.rev, 2)} for p in top_products
        ],
        "insights": [
            {"title": i.title, "severity": i.severity, "description": i.description} for i in insights
        ]
    }

@router.get("/export-csv/{entity_type}")
def export_csv_report(entity_type: str, db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)

    if entity_type == "customers":
        writer.writerow(["ID", "Name", "Email", "Phone", "Company", "Status", "Notes", "Created Date"])
        customers = db.query(Customer).all()
        for c in customers:
            writer.writerow([c.id, c.name, c.email, c.phone, c.company, c.status, c.notes, c.created_at.strftime("%Y-%m-%d")])
        filename = "customers_report.csv"

    elif entity_type == "products":
        writer.writerow(["ID", "SKU", "Product Name", "Category ID", "Stock Qty", "Min Threshold", "Cost Price", "Selling Price", "Supplier"])
        products = db.query(Product).all()
        for p in products:
            writer.writerow([p.id, p.sku, p.name, p.category_id, p.stock_qty, p.min_stock_threshold, p.cost_price, p.selling_price, p.supplier])
        filename = "products_inventory.csv"

    elif entity_type == "orders":
        writer.writerow(["Order Number", "Customer ID", "Order Date", "Status", "Payment Status", "Total Amount ($)", "COGS ($)", "Net Profit ($)"])
        orders = db.query(Order).all()
        for o in orders:
            writer.writerow([o.order_number, o.customer_id, o.order_date.strftime("%Y-%m-%d %H:%M"), o.status, o.payment_status, o.total_amount, o.cogs_amount, o.total_amount - o.cogs_amount])
        filename = "sales_orders_report.csv"
    else:
        raise HTTPException(status_code=400, detail="Invalid entity type. Use 'customers', 'products', or 'orders'.")

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/settings/openai-key")
def save_openai_api_key(payload: APIKeyPayload, db: Session = Depends(get_db)):
    setting = db.query(SystemSetting).filter(SystemSetting.key == "openai_api_key").first()
    if not setting:
        setting = SystemSetting(key="openai_api_key", value=payload.openai_api_key)
        db.add(setting)
    else:
        setting.value = payload.openai_api_key

    db.commit()
    return {"message": "OpenAI API Key setting updated successfully"}

@router.get("/settings/openai-key")
def get_openai_api_key_status(db: Session = Depends(get_db)):
    setting = db.query(SystemSetting).filter(SystemSetting.key == "openai_api_key").first()
    has_key = bool(setting and setting.value and len(setting.value.strip()) > 5)
    masked_key = f"{setting.value[:7]}...{setting.value[-4:]}" if has_key else "Not Configured"
    return {"configured": has_key, "masked_key": masked_key}
