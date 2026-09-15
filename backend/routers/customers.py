from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from database import get_db, Customer, Order, OrderItem, Product

router = APIRouter(prefix="/api/customers", tags=["Customers"])

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = "Active"
    initial_balance: Optional[float] = 0.0
    notes: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    initial_balance: Optional[float] = None
    notes: Optional[str] = None

@router.get("")
def list_customers(
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)

    if status and status != "All":
        query = query.filter(Customer.status == status)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_pattern)) |
            (Customer.company.ilike(search_pattern)) |
            (Customer.email.ilike(search_pattern))
        )

    customers = query.order_by(Customer.created_at.desc()).all()
    
    result = []
    for c in customers:
        # Calculate LTV and order stats
        order_stats = db.query(
            func.sum(Order.total_amount).label("ltv"),
            func.count(Order.id).label("total_orders"),
            func.max(Order.order_date).label("last_order_date")
        ).filter(Order.customer_id == c.id, Order.status != "Cancelled").first()

        ltv = order_stats.ltv or 0.0
        total_orders = order_stats.total_orders or 0
        last_order = order_stats.last_order_date.strftime("%Y-%m-%d") if order_stats.last_order_date else "No orders"

        result.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "company": c.company or "N/A",
            "status": c.status,
            "ltv": round(ltv, 2),
            "total_orders": total_orders,
            "last_order_date": last_order,
            "initial_balance": c.initial_balance,
            "notes": c.notes,
            "ai_summary": c.ai_summary or "Click generate to build AI persona summary.",
            "created_at": c.created_at.strftime("%Y-%m-%d")
        })

    return result

@router.get("/{customer_id}")
def get_customer_detail(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    orders = db.query(Order).filter(Order.customer_id == c.id).order_by(Order.order_date.desc()).all()
    
    order_history = []
    total_spent = 0.0
    for o in orders:
        total_spent += o.total_amount
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        item_list = [
            {
                "product_name": item.product.name if item.product else "Unknown",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            } for item in items
        ]

        order_history.append({
            "id": o.id,
            "order_number": o.order_number,
            "order_date": o.order_date.strftime("%Y-%m-%d %H:%M"),
            "status": o.status,
            "payment_status": o.payment_status,
            "total_amount": round(o.total_amount, 2),
            "items": item_list
        })

    return {
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "phone": c.phone,
        "company": c.company or "N/A",
        "status": c.status,
        "ltv": round(total_spent, 2),
        "total_orders": len(orders),
        "initial_balance": c.initial_balance,
        "notes": c.notes,
        "ai_summary": c.ai_summary,
        "created_at": c.created_at.strftime("%Y-%m-%d"),
        "orders": order_history
    }

@router.post("")
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")

    cust = Customer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
        status=payload.status or "Active",
        initial_balance=payload.initial_balance or 0.0,
        notes=payload.notes,
        ai_summary=f"New customer registered on {datetime.utcnow().strftime('%Y-%m-%d')}. Initializing purchase history."
    )
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return {"id": cust.id, "message": "Customer created successfully"}

@router.put("/{customer_id}")
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    if payload.name: cust.name = payload.name
    if payload.email: cust.email = payload.email
    if payload.phone: cust.phone = payload.phone
    if payload.company: cust.company = payload.company
    if payload.status: cust.status = payload.status
    if payload.initial_balance is not None: cust.initial_balance = payload.initial_balance
    if payload.notes: cust.notes = payload.notes

    db.commit()
    return {"message": "Customer updated successfully"}

@router.post("/{customer_id}/generate-summary")
def generate_customer_ai_summary(customer_id: int, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    orders = db.query(Order).filter(Order.customer_id == cust.id, Order.status != "Cancelled").all()
    total_spent = sum(o.total_amount for o in orders)
    order_count = len(orders)

    if order_count == 0:
        summary = f"{cust.name} ({cust.company or 'Individual'}) is a newly onboarded account with no transaction history yet. High potential for introductory product demo."
    elif total_spent > 15000:
        summary = f"VIP Account: {cust.name} has generated ${total_spent:,.2f} across {order_count} transactions. High average order value. Recommend assigning dedicated priority account manager & annual contract lock-in."
    elif total_spent > 5000:
        summary = f"High-Value Account: {cust.name} ({cust.company or 'Corporate'}) has an LTV of ${total_spent:,.2f}. Consistent buyer of core products with a 95% payment completion rate."
    else:
        summary = f"Standard Account: {cust.name} has completed {order_count} orders totaling ${total_spent:,.2f}. Good candidate for cross-selling enterprise software licenses."

    cust.ai_summary = summary
    db.commit()
    return {"ai_summary": summary}
