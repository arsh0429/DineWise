"""Database models for DineWise reservation system"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    neighborhood = Column(String, nullable=False)
    city = Column(String, default="Bangalore")
    cuisines = Column(JSON, nullable=False)  # ["North Indian", "Chinese"]
    price_range = Column(String, nullable=False)  # "₹400-600"
    seating_capacity = Column(Integer, default=50)
    available_slots = Column(JSON, nullable=False)  # ["12:30 PM", "7:30 PM"]
    rating = Column(Float, default=4.0)
    amenities = Column(JSON, default=list)
    ambiance = Column(JSON, default=list)
    description = Column(String)

class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        UniqueConstraint('restaurant_id', 'date', 'time', 'status', name='uq_no_double_booking'),
    )
    
    id = Column(String, primary_key=True)  # "DW-2024-ABC123"
    restaurant_id = Column(String, nullable=False)
    restaurant_name = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_email = Column(String)
    party_size = Column(Integer, nullable=False)
    date = Column(String, nullable=False)  # "February 11, 2026"
    time = Column(String, nullable=False)  # "7:30 PM"
    special_requests = Column(String)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.now)

# Database setup
engine = create_engine("sqlite:///data/dinewise.db")
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return SessionLocal()
