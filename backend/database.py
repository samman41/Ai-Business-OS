import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_PATH = os.path.join(os.path.dirname(__file__), "business_os.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(30))
    company = Column(String(100))
    status = Column(String(20), default="Active") # Active, VIP, At-Risk, Inactive
    notes = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    initial_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))

    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(100), nullable=False)
    sku = Column(String(50), unique=True, index=True)
    stock_qty = Column(Integer, default=0)
    min_stock_threshold = Column(Integer, default=10)
    cost_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    supplier = Column(String(100))
    lead_time_days = Column(Integer, default=7)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_number = Column(String(50), unique=True, index=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="Completed") # Completed, Pending, Processing, Cancelled
    payment_status = Column(String(20), default="Paid") # Paid, Pending, Refunded
    total_amount = Column(Float, default=0.0)
    cogs_amount = Column(Float, default=0.0) # Cost of goods sold
    shipping_address = Column(String(255))
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer) # in bytes
    category = Column(String(50), default="General") # Contract, Invoice, Financial, Report, General
    summary = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(50)) # Risk, Opportunity, Inventory, Sales, Customer
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="Medium") # High, Medium, Low, Positive
    impact_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
