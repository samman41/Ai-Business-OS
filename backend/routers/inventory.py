from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from database import get_db, Product, Category, OrderItem, Order

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

class ProductCreate(BaseModel):
    category_id: int
    name: str
    sku: str
    stock_qty: int
    min_stock_threshold: int
    cost_price: float
    selling_price: float
    supplier: Optional[str] = "Standard Supplier"
    lead_time_days: Optional[int] = 7

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    sku: Optional[str] = None
    stock_qty: Optional[int] = None
    min_stock_threshold: Optional[int] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    supplier: Optional[str] = None
    lead_time_days: Optional[int] = None

@router.get("/products")
def list_products(
    category_id: Optional[int] = None,
    stock_status: Optional[str] = None, # Low, OutOfStock, Good
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_pattern)) |
            (Product.sku.ilike(search_pattern)) |
            (Product.supplier.ilike(search_pattern))
        )

    products = query.all()
    categories = {c.id: c.name for c in db.query(Category).all()}

    result = []
    for p in products:
        margin_amt = p.selling_price - p.cost_price
        margin_pct = (margin_amt / p.selling_price * 100) if p.selling_price > 0 else 0.0

        if p.stock_qty <= 0:
            status = "Out of Stock"
        elif p.stock_qty <= p.min_stock_threshold:
            status = "Low Stock"
        else:
            status = "In Stock"

        if stock_status and stock_status != "All":
            if stock_status == "Low" and status != "Low Stock": continue
            if stock_status == "OutOfStock" and status != "Out of Stock": continue
            if stock_status == "InStock" and status != "In Stock": continue

        result.append({
            "id": p.id,
            "category_id": p.category_id,
            "category_name": categories.get(p.category_id, "General"),
            "name": p.name,
            "sku": p.sku,
            "stock_qty": p.stock_qty,
            "min_stock_threshold": p.min_stock_threshold,
            "cost_price": round(p.cost_price, 2),
            "selling_price": round(p.selling_price, 2),
            "profit_margin": round(margin_amt, 2),
            "margin_pct": round(margin_pct, 1),
            "supplier": p.supplier,
            "lead_time_days": p.lead_time_days,
            "stock_status": status
        })

    return result

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).all()
    return [{"id": c.id, "name": c.name, "description": c.description} for c in cats]

@router.post("/products")
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product SKU already exists")

    prod = Product(
        category_id=payload.category_id,
        name=payload.name,
        sku=payload.sku,
        stock_qty=payload.stock_qty,
        min_stock_threshold=payload.min_stock_threshold,
        cost_price=payload.cost_price,
        selling_price=payload.selling_price,
        supplier=payload.supplier,
        lead_time_days=payload.lead_time_days
    )
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return {"id": prod.id, "message": "Product created successfully"}

@router.put("/products/{product_id}")
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.name: prod.name = payload.name
    if payload.sku: prod.sku = payload.sku
    if payload.stock_qty is not None: prod.stock_qty = payload.stock_qty
    if payload.min_stock_threshold is not None: prod.min_stock_threshold = payload.min_stock_threshold
    if payload.cost_price is not None: prod.cost_price = payload.cost_price
    if payload.selling_price is not None: prod.selling_price = payload.selling_price
    if payload.supplier: prod.supplier = payload.supplier
    if payload.lead_time_days is not None: prod.lead_time_days = payload.lead_time_days

    db.commit()
    return {"message": "Product updated successfully"}

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(prod)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.get("/reorder-suggestions")
def get_reorder_suggestions(db: Session = Depends(get_db)):
    # AI Reorder Recommendation Logic
    # 1. Identify low stock products (current stock <= min_threshold)
    # 2. Calculate 30-day historical sales velocity per product
    # 3. Calculate suggested reorder Qty = max(min_threshold * 2.5 - stock, 30_day_sales * (lead_time / 30) * 1.5)
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Query 30-day sales velocity per product
    sales_velocity = db.query(
        OrderItem.product_id,
        func.sum(OrderItem.quantity).label("units_sold_30d")
    ).join(Order).filter(Order.order_date >= thirty_days_ago, Order.status != "Cancelled").group_by(OrderItem.product_id).all()

    velocity_map = {row.product_id: row.units_sold_30d or 0 for row in sales_velocity}

    products = db.query(Product).all()
    suggestions = []

    for p in products:
        units_sold = velocity_map.get(p.id, 0)
        daily_velocity = units_sold / 30.0
        lead_time_demand = daily_velocity * (p.lead_time_days or 7)
        safety_stock = p.min_stock_threshold

        target_stock = max(safety_stock + (lead_time_demand * 1.5), p.min_stock_threshold * 2)
        deficit = target_stock - p.stock_qty

        if p.stock_qty <= p.min_stock_threshold or deficit > 5:
            reorder_qty = int(max(deficit, 10))
            est_cost = reorder_qty * p.cost_price

            if p.stock_qty <= 2:
                urgency = "Critical"
                reason = f"Stock level ({p.stock_qty} units) severely depleted! Lead time is {p.lead_time_days} days."
            elif p.stock_qty <= p.min_stock_threshold:
                urgency = "High"
                reason = f"Stock ({p.stock_qty}) is below safety threshold ({p.min_stock_threshold}). Sales velocity: {units_sold} units/month."
            else:
                urgency = "Medium"
                reason = f"Projected lead time demand requires stock replenishment to maintain optimal buffer."

            suggestions.append({
                "product_id": p.id,
                "product_name": p.name,
                "sku": p.sku,
                "current_stock": p.stock_qty,
                "min_threshold": p.min_stock_threshold,
                "sales_30d": units_sold,
                "lead_time_days": p.lead_time_days,
                "suggested_reorder_qty": reorder_qty,
                "unit_cost": p.cost_price,
                "est_total_cost": round(est_cost, 2),
                "supplier": p.supplier,
                "urgency": urgency,
                "reason": reason
            })

    # Sort suggestions by urgency (Critical -> High -> Medium)
    urgency_weights = {"Critical": 1, "High": 2, "Medium": 3}
    suggestions.sort(key=lambda x: urgency_weights.get(x["urgency"], 4))

    return suggestions
