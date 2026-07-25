from sqlalchemy import Column, String, Float, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from mixins import AuditMixin
from datetime import datetime

class Client(Base, AuditMixin):
    __tablename__ = "clients"

    client_code = Column(String(50), unique=True, index=True)
    company_name = Column(String(255), nullable=True)
    client_name = Column(String(255))
    display_name = Column(String(255))
    client_type = Column(String(50)) # Individual, Company
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(50), nullable=True)
    timezone = Column(String(100), nullable=True)
    currency = Column(String(10), nullable=True)
    language = Column(String(50), nullable=True)
    
    address_line_1 = Column(Text, nullable=True)
    address_line_2 = Column(Text, nullable=True)
    google_map_location = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    email = Column(String(255), unique=True, index=True)
    secondary_email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    telegram = Column(String(50), nullable=True)
    skype = Column(String(100), nullable=True)
    discord = Column(String(100), nullable=True)
    linkedin = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    twitter_x = Column(String(255), nullable=True)
    
    preferred_contact_method = Column(String(50), nullable=True)
    preferred_communication_time = Column(String(100), nullable=True)
    
    vat_number = Column(String(100), nullable=True)
    tin_number = Column(String(100), nullable=True)
    trade_license = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    
    payment_terms = Column(String(100), nullable=True)
    credit_limit = Column(Float, default=0.0)
    
    status = Column(String(50), default="Active")
    notes = Column(Text, nullable=True)
    
    profile_photo = Column(String(255), nullable=True)
    company_logo = Column(String(255), nullable=True)
    
    projects = relationship("Project", back_populates="client")

class Service(Base, AuditMixin):
    __tablename__ = "services"
    
    service_code = Column(String(50), unique=True, index=True)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    default_price = Column(Float, default=0.0)
    vat_percentage = Column(Float, default=0.0)
    tax_type = Column(String(50), nullable=True)
    estimated_duration = Column(String(100), nullable=True)
    billing_type = Column(String(50)) # Hourly, Fixed, Monthly, Yearly
    color = Column(String(20), nullable=True)
    icon = Column(String(50), nullable=True)
    status = Column(String(50), default="Active")

class Project(Base, AuditMixin):
    __tablename__ = "projects"
    
    project_code = Column(String(50), unique=True, index=True)
    project_title = Column(String(255))
    short_title = Column(String(100), nullable=True)
    slug = Column(String(255), unique=True)
    
    project_type = Column(String(50)) # Client Project, In-house, Internal
    department = Column(String(100), nullable=True)
    business_unit = Column(String(100), nullable=True)
    project_category = Column(String(100), nullable=True)
    
    project_priority = Column(String(50), default="Medium")
    project_level = Column(String(50), default="Medium")
    project_status = Column(String(50), default="Draft")
    
    description = Column(Text, nullable=True)
    objectives = Column(Text, nullable=True)
    scope = Column(Text, nullable=True)
    expected_deliverables = Column(Text, nullable=True)
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    
    project_manager_id = Column(Integer, nullable=True)
    team_leader_id = Column(Integer, nullable=True)
    project_coordinator_id = Column(Integer, nullable=True)
    
    budget_type = Column(String(50), default="Fixed Budget")
    budget = Column(Float, default=0.0)
    estimated_cost = Column(Float, default=0.0)
    estimated_revenue = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    
    tax_mode = Column(String(50), default="VAT Excluded")
    vat_included = Column(Boolean, default=False)
    discount = Column(Float, default=0.0)
    additional_cost = Column(Float, default=0.0)
    final_budget = Column(Float, default=0.0)
    
    invoice_number = Column(String(100), nullable=True)
    purchase_order_number = Column(String(100), nullable=True)
    contract_number = Column(String(100), nullable=True)
    contract_file = Column(String(255), nullable=True)
    nda_file = Column(String(255), nullable=True)
    
    project_start_date = Column(DateTime, nullable=True)
    expected_end_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    
    estimated_hours = Column(Float, default=0.0)
    consumed_hours = Column(Float, default=0.0)
    remaining_hours = Column(Float, default=0.0)
    completion_percentage = Column(Float, default=0.0)
    
    project_color = Column(String(20), nullable=True)
    project_icon = Column(String(50), nullable=True)
    tags = Column(String(255), nullable=True)
    labels = Column(String(255), nullable=True)
    risk_level = Column(String(50), nullable=True)
    dependencies = Column(Text, nullable=True)
    document_path = Column(String(255), nullable=True)
    
    technology_stack = Column(Text, nullable=True)
    repository_url = Column(String(255), nullable=True)
    github = Column(String(255), nullable=True)
    gitlab = Column(String(255), nullable=True)
    bitbucket = Column(String(255), nullable=True)
    production_url = Column(String(255), nullable=True)
    development_url = Column(String(255), nullable=True)
    staging_url = Column(String(255), nullable=True)
    api_url = Column(String(255), nullable=True)
    documentation_url = Column(String(255), nullable=True)
    figma_url = Column(String(255), nullable=True)
    drive_folder = Column(String(255), nullable=True)
    slack_channel = Column(String(255), nullable=True)
    discord_channel = Column(String(255), nullable=True)
    
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    client_visible_notes = Column(Text, nullable=True)
    
    client = relationship("Client", back_populates="projects")
    services = relationship("ProjectService", back_populates="project")
    members = relationship("ProjectMember", back_populates="project")
    files = relationship("ProjectFile", back_populates="project")
    tasks = relationship("ProjectTask", back_populates="project")
    milestones = relationship("ProjectMilestone", back_populates="project")
    activity_logs = relationship("ProjectActivityLog", back_populates="project")
    project_notes = relationship("ProjectNote", back_populates="project")

class ProjectService(Base, AuditMixin):
    __tablename__ = "project_services"
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    vat_percentage = Column(Float, default=0.0)
    discount_percentage = Column(Float, default=0.0)
    
    subtotal = Column(Float, default=0.0)
    vat_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    project = relationship("Project", back_populates="services")
    service = relationship("Service")

class ProjectMember(Base, AuditMixin):
    __tablename__ = "project_members"
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    role = Column(String(100))
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    allocation_percentage = Column(Float, default=100.0)
    hourly_rate = Column(Float, default=0.0)
    
    project = relationship("Project", back_populates="members")

class ProjectFile(Base, AuditMixin):
    __tablename__ = "project_files"
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    folder_name = Column(String(255), nullable=True)
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(String(50)) # Images, PDF, DOC, Excel, ZIP, Video, Design Files, Contracts, Invoices, Other
    file_size = Column(Integer, default=0) # Bytes
    version = Column(Integer, default=1)
    
    project = relationship("Project", back_populates="files")

class ProjectTask(Base, AuditMixin):
    __tablename__ = "project_tasks"
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    task_title = Column(String(255))
    description = Column(Text, nullable=True)
    priority = Column(String(50), default="Medium")
    status = Column(String(50), default="Pending")
    assigned_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    start_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    estimated_hours = Column(Float, default=0.0)
    spent_hours = Column(Float, default=0.0)
    progress = Column(Float, default=0.0)
    
    project = relationship("Project", back_populates="tasks")
    checklists = relationship("TaskChecklist", back_populates="task")
    comments = relationship("TaskComment", back_populates="task")

class TaskChecklist(Base, AuditMixin):
    __tablename__ = "task_checklists"
    
    task_id = Column(Integer, ForeignKey("project_tasks.id"))
    title = Column(String(255))
    is_completed = Column(Boolean, default=False)
    
    task = relationship("ProjectTask", back_populates="checklists")

class TaskComment(Base, AuditMixin):
    __tablename__ = "task_comments"
    
    task_id = Column(Integer, ForeignKey("project_tasks.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    comment = Column(Text)
    attachment_path = Column(String(500), nullable=True)
    
    task = relationship("ProjectTask", back_populates="comments")

class ProjectMilestone(Base, AuditMixin):
    __tablename__ = "project_milestones"
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    milestone_name = Column(String(255))
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="Pending")
    completion_percentage = Column(Float, default=0.0)
    
    project = relationship("Project", back_populates="milestones")

class ProjectNote(Base, AuditMixin):
    __tablename__ = "project_notes"
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    note = Column(Text)
    is_private = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    mentioned_employee_ids = Column(String(255), nullable=True) # comma separated IDs
    
    project = relationship("Project", back_populates="project_notes")

class ProjectActivityLog(Base, AuditMixin):
    __tablename__ = "project_activity_logs"
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    action_type = Column(String(100))
    description = Column(Text)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    project = relationship("Project", back_populates="activity_logs")

# Supporting tables for dropdowns / configs (Tags, Labels, Categories, Status History)
class ProjectTag(Base, AuditMixin):
    __tablename__ = "project_tags"
    name = Column(String(100), unique=True)
    color = Column(String(20), nullable=True)

class ProjectLabel(Base, AuditMixin):
    __tablename__ = "project_labels"
    name = Column(String(100), unique=True)
    color = Column(String(20), nullable=True)

class ProjectCategory(Base, AuditMixin):
    __tablename__ = "project_categories"
    name = Column(String(100), unique=True)
    description = Column(Text, nullable=True)

class ProjectStatusHistory(Base, AuditMixin):
    __tablename__ = "project_status_history"
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    status = Column(String(50))
    reason = Column(Text, nullable=True)
