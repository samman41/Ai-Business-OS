from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db, Order, OrderItem, Customer, Product

router = APIRouter(prefix="/api/sales", tags=["Sales"])

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]
    shipping_address: Optional[str] = None
    notes: Optional[str] = None

@router.get("/orders")
def list_orders(
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Order)

    if status and status != "All":
        query = query.filter(Order.status == status)

    if payment_status and payment_status != "All":
        query = query.filter(Order.payment_status == payment_status)

    orders = query.order_by(Order.order_date.desc()).all()

    result = []
    for o in orders:
        cust = db.query(Customer).filter(Customer.id == o.customer_id).first()
        item_count = db.query(func.sum(OrderItem.quantity)).filter(OrderItem.order_id == o.id).scalar() or 0
        profit = o.total_amount - o.cogs_amount

        result.append({
            "id": o.id,
            "order_number": o.order_number,
            "customer_id": o.customer_id,
            "customer_name": cust.name if cust else "Unknown",
            "company": cust.company if cust else "N/A",
            "order_date": o.order_date.strftime("%Y-%m-%d %H:%M"),
            "status": o.status,
            "payment_status": o.payment_status,
            "total_amount": round(o.total_amount, 2),
            "cogs_amount": round(o.cogs_amount, 2),
            "net_profit": round(profit, 2),
            "item_count": item_count
        })

    return result

@router.get("/orders/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")

    cust = db.query(Customer).filter(Customer.id == o.customer_id).first()
    items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()

    item_lines = []
    for item in items:
        p = db.query(Product).filter(Product.id == item.product_id).first()
        item_lines.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": p.name if p else "Product",
            "sku": p.sku if p else "N/A",
            "quantity": item.quantity,
            "unit_price": round(item.unit_price, 2),
            "total_price": round(item.total_price, 2)
        })

    return {
        "id": o.id,
        "order_number": o.order_number,
        "order_date": o.order_date.strftime("%Y-%m-%d %H:%M"),
        "status": o.status,
        "payment_status": o.payment_status,
        "total_amount": round(o.total_amount, 2),
        "cogs_amount": round(o.cogs_amount, 2),
        "net_profit": round(o.total_amount - o.cogs_amount, 2),
        "shipping_address": o.shipping_address or "100 Executive Blvd, NY",
        "notes": o.notes,
        "customer": {
            "id": cust.id,
            "name": cust.name,
            "email": cust.email,
            "phone": cust.phone,
            "company": cust.company or "Individual"
        } if cust else None,
        "items": item_lines
    }

@router.post("/orders")
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one product line item")

    # Generate Order Number
    order_count = db.query(func.count(Order.id)).scalar() or 0
    order_num = f"INV-2026-{1001 + order_count}"

    order = Order(
        customer_id=cust.id,
        order_number=order_num,
        order_date=datetime.utcnow(),
        status="Completed",
        payment_status="Paid",
        shipping_address=payload.shipping_address or f"{cust.company or 'Corporate Headquarters'}, New York, NY",
        notes=payload.notes
    )
    db.add(order)
    db.flush()

    total_amount = 0.0
    total_cogs = 0.0

    for item_data in payload.items:
        prod = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product ID {item_data.product_id} not found")
        
        if prod.stock_qty < item_data.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {prod.name}. Available: {prod.stock_qty}")

        # Decrement stock
        prod.stock_qty -= item_data.quantity

        line_total = prod.selling_price * item_data.quantity
        line_cogs = prod.cost_price * item_data.quantity

        total_amount += line_total
        total_cogs += line_cogs

        item = OrderItem(
            order_id=order.id,
            product_id=prod.id,
            quantity=item_data.quantity,
            unit_price=prod.selling_price,
            unit_cost=prod.cost_price,
            total_price=line_total
        )
        db.add(item)

    order.total_amount = total_amount
    order.cogs_amount = total_cogs

    db.commit()
    db.refresh(order)

    return {"id": order.id, "order_number": order.order_number, "message": "Order created successfully"}

@router.get("/profit-report")
def get_profit_report(db: Session = Depends(get_db)):
    completed_orders = db.query(Order).filter(Order.status != "Cancelled").all()
    
    total_revenue = sum(o.total_amount for o in completed_orders)
    total_cogs = sum(o.cogs_amount for o in completed_orders)
    gross_profit = total_revenue - total_cogs
    margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    avg_order_val = total_revenue / len(completed_orders) if completed_orders else 0.0

    # Top selling product by profit
    top_products_query = db.query(
        Product.name,
        func.sum(OrderItem.total_price).label("revenue"),
        func.sum(OrderItem.quantity).label("total_qty")
    ).join(OrderItem).group_by(Product.id).order_by(func.sum(OrderItem.total_price).desc()).limit(5).all()

    top_products = [
        {"name": row.name, "revenue": round(row.revenue, 2), "total_qty": row.total_qty}
        for row in top_products_query
    ]

    return {
        "total_revenue": round(total_revenue, 2),
        "total_cogs": round(total_cogs, 2),
        "gross_profit": round(gross_profit, 2),
        "margin_pct": round(margin_pct, 1),
        "total_orders": len(completed_orders),
        "avg_order_value": round(avg_order_val, 2),
        "top_products": top_products
    }
