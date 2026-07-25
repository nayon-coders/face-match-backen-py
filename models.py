from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    phone = Column(String(50))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255), nullable=True) # Hashed password for the account
    designation = Column(String(255))
    salary = Column(Float)
    salary_type = Column(String(50)) # 'Daily', 'Hourly', 'Monthly'
    nid_front_path = Column(String(500), nullable=True)
    nid_back_path = Column(String(500), nullable=True)
    
    face_encoding = Column(Text, nullable=True) # Storing json string of encoding array
    dynamic_data = Column(Text, nullable=True) # JSON string for custom field values
    created_at = Column(DateTime, default=datetime.utcnow)

    attendance_logs = relationship("AttendanceLog", back_populates="employee")

class EmployeeField(Base):
    __tablename__ = "employee_fields"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String(255))
    field_type = Column(String(50)) # text, select, checkbox, radio, image
    options = Column(Text, nullable=True) # JSON array of options if applicable
    is_required = Column(Boolean, default=False)
    order = Column(Integer, default=0)

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(DateTime, default=datetime.utcnow) # Represents the specific workday
    clock_in_time = Column(DateTime, nullable=True)
    clock_out_time = Column(DateTime, nullable=True)
    status = Column(String(50)) # 'Present', 'Late', 'Absent'
    working_hours = Column(Float, default=0.0)
    latitude_in = Column(Float, nullable=True)
    longitude_in = Column(Float, nullable=True)
    latitude_out = Column(Float, nullable=True)
    longitude_out = Column(Float, nullable=True)
    
    employee = relationship("Employee", back_populates="attendance_logs")

class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True)
    office_start_time = Column(String(50), default="09:00:00")
    office_end_time = Column(String(50), default="17:00:00")
    late_after_minutes = Column(Integer, default=15)
    early_leave_minutes = Column(Integer, default=15)
    overtime_multiplier = Column(Float, default=1.5)
    weekly_holiday = Column(String(50), default="Sunday")
    face_match_tolerance = Column(Float, default=0.6)
    attendance_radius_meters = Column(Float, default=100.0)
    working_days = Column(String(255), default="Mon,Tue,Wed,Thu,Fri,Sat")
    currency = Column(String(10), default="USD")

class SMTPSettings(Base):
    __tablename__ = "smtp_settings"

    id = Column(Integer, primary_key=True, index=True)
    host = Column(String(255), nullable=True)
    port = Column(Integer, default=587)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    sender_email = Column(String(255), nullable=True)
    use_tls = Column(Boolean, default=True)
