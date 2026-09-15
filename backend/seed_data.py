from datetime import datetime, timedelta
import random
from database import SessionLocal, init_db, Customer, Category, Product, Order, OrderItem, Document, Insight, SystemSetting

def seed_database():
    init_db()
    db = SessionLocal()

    # Clear existing data
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Product).delete()
    db.query(Category).delete()
    db.query(Customer).delete()
    db.query(Document).delete()
    db.query(Insight).delete()
    db.query(SystemSetting).delete()
    db.commit()

    print("Seeding Categories & Products...")
    categories_data = [
        {"name": "Electronics & Hardware", "description": "High-end computing hardware and smart devices"},
        {"name": "Enterprise Software", "description": "SaaS tools and AI productivity licenses"},
        {"name": "Office Luxury Furniture", "description": "Ergonomic seating and executive desks"},
        {"name": "Services & Consulting", "description": "Strategy, design, and custom implementation"}
    ]

    cats = []
    for c in categories_data:
        cat = Category(name=c["name"], description=c["description"])
        db.add(cat)
        cats.append(cat)
    db.commit()

    products_data = [
        # Electronics
        {"cat_idx": 0, "name": "AI Edge Workstation Pro", "sku": "EL-AIWS-01", "stock": 14, "min_stock": 5, "cost": 1800.0, "price": 3200.0, "supplier": "Aether Tech Supplies", "lead_time": 10},
        {"cat_idx": 0, "name": "4K Ultra-Wide Curved Monitor", "sku": "EL-MON-4K", "stock": 4, "min_stock": 10, "cost": 450.0, "price": 890.0, "supplier": "Visionary Displays", "lead_time": 5},
        {"cat_idx": 0, "name": "Smart Conference Hub X", "sku": "EL-CONF-HUB", "stock": 22, "min_stock": 8, "cost": 310.0, "price": 650.0, "supplier": "Aether Tech Supplies", "lead_time": 7},
        {"cat_idx": 0, "name": "Biometric Access Terminal", "sku": "EL-BIO-TERM", "stock": 2, "min_stock": 8, "cost": 190.0, "price": 420.0, "supplier": "SecureShield Tech", "lead_time": 12}, # Low stock
        
        # Enterprise Software
        {"cat_idx": 1, "name": "Business Intelligence Cloud - Annual", "sku": "SW-BI-ANN", "stock": 999, "min_stock": 10, "cost": 120.0, "price": 1200.0, "supplier": "Internal Systems", "lead_time": 1},
        {"cat_idx": 1, "name": "CyberGuard Security Suite", "sku": "SW-CG-SEC", "stock": 999, "min_stock": 10, "cost": 90.0, "price": 750.0, "supplier": "Internal Systems", "lead_time": 1},
        {"cat_idx": 1, "name": "Legacy Data Sync Module (Deprecating)", "sku": "SW-LEG-SYNC", "stock": 999, "min_stock": 10, "cost": 200.0, "price": 350.0, "supplier": "Internal Systems", "lead_time": 1}, # Low sales item

        # Office Furniture
        {"cat_idx": 2, "name": "Executive Leather Desk Chair", "sku": "FN-EXCH-GLD", "stock": 6, "min_stock": 8, "cost": 340.0, "price": 780.0, "supplier": "Aura Luxury Interiors", "lead_time": 14}, # Low stock
        {"cat_idx": 2, "name": "Motorized Standing Desk Gold Edition", "sku": "FN-STDSK-GLD", "stock": 18, "min_stock": 5, "cost": 620.0, "price": 1450.0, "supplier": "Aura Luxury Interiors", "lead_time": 14},
        {"cat_idx": 2, "name": "Acoustic Quiet Pod", "sku": "FN-POD-QT", "stock": 1, "min_stock": 3, "cost": 2400.0, "price": 4900.0, "supplier": "Aura Luxury Interiors", "lead_time": 21}, # Low stock

        # Services
        {"cat_idx": 3, "name": "Enterprise AI Strategy Workshop", "sku": "SV-AI-STRAT", "stock": 50, "min_stock": 5, "cost": 800.0, "price": 4500.0, "supplier": "In-house Experts", "lead_time": 2},
        {"cat_idx": 3, "name": "Custom ERP Integration Retainer", "sku": "SV-ERP-INT", "stock": 20, "min_stock": 2, "cost": 1500.0, "price": 6000.0, "supplier": "In-house Experts", "lead_time": 3}
    ]

    products = []
    for p in products_data:
        prod = Product(
            category_id=cats[p["cat_idx"]].id,
            name=p["name"],
            sku=p["sku"],
            stock_qty=p["stock"],
            min_stock_threshold=p["min_stock"],
            cost_price=p["cost"],
            selling_price=p["price"],
            supplier=p["supplier"],
            lead_time_days=p["lead_time"]
        )
        db.add(prod)
        products.append(prod)
    db.commit()

    print("Seeding Customers...")
    customers_data = [
        {
            "name": "Sophia Vance", "email": "sophia.vance@apexholdings.com", "phone": "+1 (555) 234-8901",
            "company": "Apex Holdings Corp", "status": "VIP",
            "notes": "Key account holder. Prefers annual invoicing and priority hardware support.",
            "ai_summary": "Top revenue contributor (LTV > $28,000). Highly responsive to software upgrade offers. High retention probability."
        },
        {
            "name": "Marcus Vance", "email": "marcus.v@luminartech.io", "phone": "+1 (555) 890-1234",
            "company": "Luminar Innovations", "status": "VIP",
            "notes": "Expanded office location last quarter. Expanding team.",
            "ai_summary": "VIP Client with frequent hardware purchases. Ideal candidate for custom ERP retainer."
        },
        {
            "name": "Elena Rostova", "email": "elena@vanguardventures.com", "phone": "+1 (555) 456-7890",
            "company": "Vanguard Ventures", "status": "Active",
            "notes": "Standard customer. Monthly SaaS licenses.",
            "ai_summary": "Consistent SaaS subscriber with low support ticket volume. Steady margin contributor."
        },
        {
            "name": "David Sterling", "email": "dsterling@sterlingfintech.net", "phone": "+1 (555) 678-9012",
            "company": "Sterling Fintech Group", "status": "Active",
            "notes": "Inquired about biometric access terminals.",
            "ai_summary": "Growing technology client. Likely to convert to Enterprise hardware packages in Q3."
        },
        {
            "name": "Chloe Zhao", "email": "chloe.zhao@nexusglobal.org", "phone": "+1 (555) 901-2345",
            "company": "Nexus Global", "status": "At-Risk",
            "notes": "No purchases in last 90 days. Account manager follow-up pending.",
            "ai_summary": "At-risk client (60+ days dormancy). Purchase volume declined by 40%. Recommend outreach with special renewal discount."
        },
        {
            "name": "Arthur Pendelton", "email": "arthur@pendeltonlaw.com", "phone": "+1 (555) 345-6789",
            "company": "Pendelton & Associates", "status": "Active",
            "notes": "Purchased executive furniture and workstation.",
            "ai_summary": "Medium-tier legal firm. High single-purchase value with low repeat frequency."
        }
    ]

    customers = []
    for c in customers_data:
        cust = Customer(
            name=c["name"], email=c["email"], phone=c["phone"],
            company=c["company"], status=c["status"], notes=c["notes"],
            ai_summary=c["ai_summary"]
        )
        db.add(cust)
        customers.append(cust)
    db.commit()

    print("Seeding Orders & Order Items...")
    # Generate past 6 months of historical orders
    now = datetime.utcnow()
    orders_created = 0

    # Historical order templates
    order_scenarios = [
        # Customer idx, days_ago, products indices & quantities
        (0, 5, [(0, 2), (4, 2), (10, 1)], "Paid", "Completed"),
        (0, 32, [(1, 3), (8, 1)], "Paid", "Completed"),
        (0, 75, [(0, 3), (7, 2)], "Paid", "Completed"),
        (1, 12, [(0, 1), (8, 2), (11, 1)], "Paid", "Completed"),
        (1, 45, [(2, 2), (5, 5)], "Paid", "Completed"),
        (2, 18, [(4, 5), (5, 5)], "Paid", "Completed"),
        (2, 60, [(4, 5)], "Paid", "Completed"),
        (3, 8, [(3, 4), (0, 1)], "Paid", "Completed"),
        (3, 40, [(2, 1), (4, 1)], "Paid", "Completed"),
        (4, 95, [(6, 2)], "Paid", "Completed"), # Old purchase, low item
        (5, 22, [(7, 2), (8, 1)], "Paid", "Completed"),
        (0, 2, [(10, 1)], "Pending", "Processing"),
        (1, 1, [(1, 2)], "Paid", "Processing")
    ]

    for idx, (c_idx, days_ago, item_list, pay_status, ord_status) in enumerate(order_scenarios):
        ord_date = now - timedelta(days=days_ago)
        order_num = f"INV-2026-{1000 + idx}"
        cust = customers[c_idx]

        total_amt = 0.0
        total_cogs = 0.0

        order = Order(
            customer_id=cust.id,
            order_number=order_num,
            order_date=ord_date,
            status=ord_status,
            payment_status=pay_status,
            shipping_address=f"100 Executive Blvd, Suite {10 + idx}, New York, NY",
            notes=f"Order generated for {cust.company}"
        )
        db.add(order)
        db.flush() # get order.id

        for prod_idx, qty in item_list:
            prod = products[prod_idx]
            line_total = prod.selling_price * qty
            line_cost = prod.cost_price * qty
            total_amt += line_total
            total_cogs += line_cost

            item = OrderItem(
                order_id=order.id,
                product_id=prod.id,
                quantity=qty,
                unit_price=prod.selling_price,
                unit_cost=prod.cost_price,
                total_price=line_total
            )
            db.add(item)

        order.total_amount = total_amt
        order.cogs_amount = total_cogs
        orders_created += 1

    db.commit()

    print("Seeding Documents...")
    documents_data = [
        {
            "filename": "Q2_Executive_Financial_Summary.pdf",
            "file_path": "uploads/Q2_Executive_Financial_Summary.pdf",
            "file_type": "application/pdf",
            "file_size": 420500,
            "category": "Financial",
            "summary": "Key financial results for Q2 showing 24.5% year-over-year revenue growth. Enterprise Software SaaS subscriptions led profit expansion with 78% gross margins.",
            "extracted_text": "Executive Summary Q2 Financial Performance. Total Revenue: $148,500. Net Operating Profit: $62,100. Operating Margin: 41.8%. Software subscription growth accelerated by 35%. Hardware fulfillment lead times reduced from 14 days to 7 days. Key Risks identified include supply chain bottlenecks for custom biometric sensors and rising shipping tariffs."
        },
        {
            "filename": "Aether_Tech_Master_Supplier_Agreement.pdf",
            "file_path": "uploads/Aether_Tech_Master_Supplier_Agreement.pdf",
            "file_type": "application/pdf",
            "file_size": 890120,
            "category": "Contract",
            "summary": "Master procurement contract with Aether Tech Supplies establishing 10-day lead time SLA and 15% volume discount for orders over 10 units.",
            "extracted_text": "Master Procurement Agreement between AI Business OS Corp and Aether Tech Supplies Inc. Terms: Net 30 payment terms. Lead Time SLA: 10 business days guaranteed. Volume Discounts: 10-25 units (15% discount), 25+ units (22% discount). Termination clause requires 60 days written notice."
        },
        {
            "filename": "Apex_Holdings_Enterprise_SLA_2026.pdf",
            "file_path": "uploads/Apex_Holdings_Enterprise_SLA_2026.pdf",
            "file_type": "application/pdf",
            "file_size": 310400,
            "category": "Contract",
            "summary": "VIP Service Level Agreement for Apex Holdings. Guarantees 24/7 dedicated support engineer and 99.9% hardware replacement response within 24 hours.",
            "extracted_text": "Enterprise Service Level Agreement (SLA). Client: Apex Holdings Corp. Dedicated Account Manager: Sarah Jenkins. Priority Support: 24/7 response within 15 minutes. On-site hardware replacement guaranteed within 24 hours. Annual Contract Value: $38,000."
        }
    ]

    for d in documents_data:
        doc = Document(
            filename=d["filename"], file_path=d["file_path"],
            file_type=d["file_type"], file_size=d["file_size"],
            category=d["category"], summary=d["summary"],
            extracted_text=d["extracted_text"]
        )
        db.add(doc)
    db.commit()

    print("Seeding AI Insights...")
    insights_data = [
        {
            "title": "Stock Alert: Biometric Terminals Critical",
            "category": "Inventory",
            "description": "Stock count for Biometric Access Terminal is down to 2 units (threshold: 8). 4 pending client quotes exist. Immediate reorder of 15 units recommended.",
            "severity": "High",
            "impact_score": 8.8
        },
        {
            "title": "VIP Customer Retention Alert: Chloe Zhao (Nexus Global)",
            "category": "Customer",
            "description": "Nexus Global has had no purchase activity in 95 days (historical cycle: 30 days). Estimated quarterly revenue at risk: $4,200. Account follow-up strongly advised.",
            "severity": "High",
            "impact_score": 8.5
        },
        {
            "title": "High Margin Opportunity: AI Strategy Workshops",
            "category": "Sales",
            "description": "Enterprise AI Strategy Workshops hold an 82% gross margin ($3,700 net per sale). Bundling this with hardware purchases could boost average order value by 28%.",
            "severity": "Positive",
            "impact_score": 9.2
        },
        {
            "title": "Slow Moving Product: Legacy Data Sync Module",
            "category": "Risk",
            "description": "Legacy Data Sync Module generated only 1 sale in the last 90 days. Consider sunsetting product or discounting package to migrate users to BI Cloud.",
            "severity": "Medium",
            "impact_score": 6.4
        }
    ]

    for i in insights_data:
        insight = Insight(
            title=i["title"], category=i["category"],
            description=i["description"], severity=i["severity"],
            impact_score=i["impact_score"]
        )
        db.add(insight)

    # Initial settings
    setting = SystemSetting(key="openai_api_key", value="")
    db.add(setting)

    db.commit()
    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
