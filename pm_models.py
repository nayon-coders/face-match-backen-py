from sqlalchemy import Column, String, Float, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from mixins import AuditMixin
from datetime import datetime
import secrets
import string

def generate_api_key():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

class Client(Base, AuditMixin):
    __tablename__ = "clients"

    client_code = Column(String(50), unique=True, index=True)
    company_name = Column(String(255), nullable=True)
    client_name = Column(String(255))
    display_name = Column(String(255))
    client_type = Column(String(50)) # Individual, Company
    
    # API specific fields
    api_key = Column(String(255), unique=True, index=True, default=generate_api_key)
    
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50), nullable=True)
    
    industry = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    postal_code = Column(String(50), nullable=True)
    timezone = Column(String(50), nullable=True)
    currency = Column(String(50), nullable=True)
    language = Column(String(50), nullable=True)
    address_line_1 = Column(Text, nullable=True)
    address_line_2 = Column(Text, nullable=True)
    secondary_email = Column(String(255), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    preferred_contact_method = Column(String(50), nullable=True)
    
    status = Column(String(50), default="Active")
    notes = Column(Text, nullable=True)
    profile_photo = Column(String(255), nullable=True)
    company_logo = Column(String(255), nullable=True)

