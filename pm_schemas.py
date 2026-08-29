from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Common Audit
class AuditResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Client Schemas
class ClientBase(BaseModel):
    company_name: Optional[str] = None
    client_name: str
    display_name: str
    client_type: str
    industry: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    email: str
    secondary_email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    status: str = "Active"

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    pass

class ClientResponse(ClientBase, AuditResponse):
    client_code: str
    api_key: str
    
    class Config:
        from_attributes = True

# Service Schemas
class ServiceBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    default_price: float = 0.0
    vat_percentage: float = 0.0
    billing_type: str
    status: str = "Active"

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    pass

class ServiceResponse(ServiceBase, AuditResponse):
    service_code: str
    
    class Config:
        from_attributes = True

# Project Schemas
class ProjectBase(BaseModel):
    project_title: str
    short_title: Optional[str] = None
    project_type: str
    department: Optional[str] = None
    project_priority: str = "Medium"
    project_level: str = "Medium"
    project_status: str = "Draft"
    description: Optional[str] = None
    client_id: Optional[int] = None
    project_manager_id: Optional[int] = None
    budget_type: str = "Fixed Budget"
    budget: float = 0.0
    currency: str = "USD"
    tax_mode: str = "VAT Excluded"
    vat_included: bool = False
    discount: float = 0.0
    additional_cost: float = 0.0
    project_start_date: Optional[datetime] = None
    expected_end_date: Optional[datetime] = None
    notes: Optional[str] = None
    document_path: Optional[str] = None

class ProjectCreate(ProjectBase):
    service_ids: List[int] = []

class ProjectUpdate(ProjectBase):
    service_ids: Optional[List[int]] = None

class ProjectServiceResponse(BaseModel):
    service_id: int
    unit_price: float
    total: float
    
    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase, AuditResponse):
    project_code: str
    slug: str
    budget: float
    estimated_cost: float
    estimated_revenue: float
    profit: float
    final_budget: float
    estimated_hours: float
    consumed_hours: float
    remaining_hours: float
    completion_percentage: float
    services: List[ProjectServiceResponse] = []
    
    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    task_title: str
    description: Optional[str] = None
    priority: str = "Medium"
    status: str = "Pending"
    assigned_employee_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: float = 0.0

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(TaskBase):
    pass

class TaskResponse(TaskBase, AuditResponse):
    project_id: int
    spent_hours: float
    progress: float
    
    class Config:
        from_attributes = True
