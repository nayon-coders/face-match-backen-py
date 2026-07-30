from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EmployeeBase(BaseModel):
    name: str
    phone: str
    email: str
    designation: Optional[str] = ""
    salary: Optional[float] = 0.0
    salary_type: Optional[str] = ""

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    nid_front_path: Optional[str] = None
    nid_back_path: Optional[str] = None
    face_registered: Optional[bool] = False
    dynamic_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EmployeeFieldBase(BaseModel):
    field_name: str
    field_type: str
    options: Optional[str] = None
    is_required: bool = False
    order: int = 0

class EmployeeFieldCreate(EmployeeFieldBase):
    pass

class EmployeeFieldResponse(EmployeeFieldBase):
    id: int

    class Config:
        from_attributes = True

class AttendanceLogBase(BaseModel):
    employee_id: Optional[int] = None
    date: datetime
    clock_in_time: Optional[datetime] = None
    clock_out_time: Optional[datetime] = None
    status: Optional[str] = "Present"
    working_hours: Optional[float] = 0.0
    latitude_in: Optional[float] = None
    longitude_in: Optional[float] = None
    latitude_out: Optional[float] = None
    longitude_out: Optional[float] = None

class AttendanceLogCreate(AttendanceLogBase):
    pass

class AttendanceLogResponse(AttendanceLogBase):
    id: int
    employee: Optional[EmployeeResponse] = None

    class Config:
        from_attributes = True

class FaceVerifyResponse(BaseModel):
    match: bool
    employee_id: int
    employee_name: str = ""

class CompanySettingsBase(BaseModel):
    office_start_time: str
    office_end_time: str
    late_after_minutes: int
    early_leave_minutes: int
    overtime_multiplier: float
    weekly_holiday: str
    face_match_tolerance: float
    attendance_radius_meters: float
    office_latitude: Optional[float] = None
    office_longitude: Optional[float] = None
    working_days: str
    currency: str = "USD"

class CompanySettingsCreate(CompanySettingsBase):
    pass

class CompanySettingsResponse(CompanySettingsBase):
    id: int

    class Config:
        from_attributes = True

class SMTPSettingsBase(BaseModel):
    host: Optional[str] = None
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    sender_email: Optional[str] = None
    use_tls: bool = True

class SMTPSettingsCreate(SMTPSettingsBase):
    pass

class SMTPSettingsResponse(SMTPSettingsBase):
    id: int

    class Config:
        from_attributes = True
