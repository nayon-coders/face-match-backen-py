from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from typing import List, Optional

import secrets
import string
import smtplib
import os
import uuid
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import models, schemas, database, face_service
from database import get_db

import pm_models # Import PM models to register them with Base
models.Base.metadata.create_all(bind=database.engine)

from routers import clients, services, projects

app = FastAPI(title="FaceAttend API")
import os
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Setup CORS for the Admin Panel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(projects.router, prefix="/api")


def send_email_task(host, port, username, password, sender_email, use_tls, to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(host, port, timeout=10)
        if use_tls:
            server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(msg)
        server.quit()
        print(f"DEBUG: Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.on_event("startup")

def startup_event():
    print("DEBUG: Running startup event...")
    face_service.preload_models()

@app.post("/api/employees", response_model=schemas.EmployeeResponse)
def create_employee(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    designation: str = Form(...),
    salary: float = Form(...),
    salary_type: str = Form(...),
    nid_front: UploadFile = File(None),
    nid_back: UploadFile = File(None),
    face_image: UploadFile = File(None),
    dynamic_data: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    existing_employee = db.query(models.Employee).filter(models.Employee.email == email).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Email already registered")

    encoding_json = None
    if face_image:
        image_bytes = face_image.file.read()
        encoding_json = face_service.get_face_encoding(image_bytes)
        if not encoding_json:
            raise HTTPException(status_code=400, detail="Could not detect a face in the image")
            
    # Save NID images
    os.makedirs("uploads", exist_ok=True)
    nid_front_path = None
    if nid_front:
        nid_front_path = f"uploads/{uuid.uuid4()}_{nid_front.filename}"
        with open(nid_front_path, "wb") as buffer:
            shutil.copyfileobj(nid_front.file, buffer)
            
    nid_back_path = None
    if nid_back:
        nid_back_path = f"uploads/{uuid.uuid4()}_{nid_back.filename}"
        with open(nid_back_path, "wb") as buffer:
            shutil.copyfileobj(nid_back.file, buffer)
            
    raw_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    hashed_password = pwd_context.hash(raw_password)

    db_employee = models.Employee(
        name=name,
        password=hashed_password,
        phone=phone,
        email=email,
        designation=designation,
        salary=salary,
        salary_type=salary_type,
        nid_front_path=nid_front_path,
        nid_back_path=nid_back_path,
        face_encoding=encoding_json,
        dynamic_data=dynamic_data
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    # Send email
    smtp_settings = db.query(models.SMTPSettings).first()
    if smtp_settings and smtp_settings.host and smtp_settings.sender_email:
        subject = "Welcome to MY HRM - Account Created"
        body = f"Hello {name},\n\nYour account has been created successfully.\nEmail: {email}\nPassword: {raw_password}\n\nPlease log in and change your password.\n\nBest Regards,\nHR Team"
        background_tasks.add_task(
            send_email_task,
            smtp_settings.host,
            smtp_settings.port,
            smtp_settings.username,
            smtp_settings.password,
            smtp_settings.sender_email,
            smtp_settings.use_tls,
            email,
            subject,
            body
        )

    return {
        "id": db_employee.id,
        "name": db_employee.name,
        "phone": db_employee.phone,
        "email": db_employee.email,
        "designation": db_employee.designation,
        "salary": db_employee.salary,
        "salary_type": db_employee.salary_type,
        "nid_front_path": db_employee.nid_front_path,
        "nid_back_path": db_employee.nid_back_path,
        "face_registered": bool(db_employee.face_encoding),
        "dynamic_data": db_employee.dynamic_data,
        "created_at": db_employee.created_at
    }

@app.get("/api/employees", response_model=List[schemas.EmployeeResponse])
def get_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = db.query(models.Employee).offset(skip).limit(limit).all()
    # Map to schema response
    return [{
        "id": e.id,
        "name": e.name,
        "phone": e.phone,
        "email": e.email,
        "designation": e.designation,
        "salary": e.salary,
        "salary_type": e.salary_type,
        "nid_front_path": e.nid_front_path,
        "nid_back_path": e.nid_back_path,
        "face_registered": bool(e.face_encoding),
        "dynamic_data": e.dynamic_data,
        "created_at": e.created_at
    } for e in employees]

@app.post("/api/attendance/test-face")
def test_face(image: UploadFile = File(...)):
    print(f"DEBUG: test-face endpoint called for file: {image.filename}")
    image_bytes = image.file.read()
    result = face_service.extract_face_base64(image_bytes)
    return result

@app.post("/api/attendance/verify-face", response_model=schemas.FaceVerifyResponse)
def verify_face(
    employee_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print(f"DEBUG: verify-face endpoint called for employee_id: {employee_id}")
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        print("DEBUG: Employee not found in DB")
        raise HTTPException(status_code=404, detail="Employee not found")
        
    if not employee.face_encoding:
        print("DEBUG: Employee has no face_encoding in DB")
        raise HTTPException(status_code=400, detail="Employee has no registered face data")

    image_bytes = image.file.read()
    print(f"DEBUG: Image received, size: {len(image_bytes)} bytes")
    is_match = face_service.verify_face(employee.face_encoding, image_bytes)
    
    print(f"DEBUG: verify_face returning match: {is_match}")
    return {"match": is_match, "employee_id": employee_id, "employee_name": employee.name}

from datetime import date, datetime
import math

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000 # Radius of earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.post("/api/attendance/clock", response_model=schemas.AttendanceLogResponse)
async def clock_in_out(
    employee_id: int = Form(...),
    type: str = Form(...), # 'clock_in' or 'clock_out'
    latitude: float = Form(None),
    longitude: float = Form(None),
    db: Session = Depends(get_db)
):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    settings = db.query(models.CompanySettings).first()
    if not settings:
        settings = models.CompanySettings() # Default settings
        db.add(settings)
        db.commit()
        db.refresh(settings)

    if settings.office_latitude is not None and settings.office_longitude is not None:
        if latitude is None or longitude is None:
            raise HTTPException(status_code=400, detail="GPS location is required for clocking in/out (Geofencing enabled)")
        dist = calculate_haversine_distance(latitude, longitude, settings.office_latitude, settings.office_longitude)
        if dist > (settings.attendance_radius_meters or 100.0):
            raise HTTPException(status_code=403, detail=f"You are {int(dist)}m away from office. Permitted radius is {int(settings.attendance_radius_meters or 100)}m.")

    today = date.today()
    now = datetime.now()

    if type == 'clock_in':
        active_log = db.query(models.AttendanceLog).filter(
            models.AttendanceLog.employee_id == employee_id,
            models.AttendanceLog.date >= datetime(today.year, today.month, today.day),
            models.AttendanceLog.clock_out_time == None
        ).first()

        if active_log:
            raise HTTPException(status_code=400, detail="Already clocked in. Please clock out first.")
            
        start_time_str = settings.office_start_time
        time_parts = start_time_str.split(':')
        start_hour = int(time_parts[0]) if len(time_parts) > 0 else 9
        start_minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        expected_start = datetime(today.year, today.month, today.day, start_hour, start_minute)
        
        from datetime import timedelta
        grace_period = timedelta(minutes=settings.late_after_minutes)
        
        status = "Late" if now > (expected_start + grace_period) else "Present"
        
        new_log = models.AttendanceLog(
            employee_id=employee_id,
            date=datetime(today.year, today.month, today.day),
            clock_in_time=now,
            status=status,
            latitude_in=latitude,
            longitude_in=longitude
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log
        
    elif type == 'clock_out':
        active_log = db.query(models.AttendanceLog).filter(
            models.AttendanceLog.employee_id == employee_id,
            models.AttendanceLog.date >= datetime(today.year, today.month, today.day),
            models.AttendanceLog.clock_out_time == None
        ).first()

        if not active_log:
            raise HTTPException(status_code=400, detail="No active clock-in found. Please clock in first.")
            
        active_log.clock_out_time = now
        active_log.latitude_out = latitude
        active_log.longitude_out = longitude
        
        diff = active_log.clock_out_time - active_log.clock_in_time
        active_log.working_hours = diff.total_seconds() / 3600.0
        
        db.commit()
        db.refresh(active_log)
        return active_log
    else:
        raise HTTPException(status_code=400, detail="Invalid clock type")

@app.get("/api/employee/{employee_id}/dashboard")
def get_employee_dashboard(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    today = date.today()
    active_log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.employee_id == employee_id,
        models.AttendanceLog.date >= datetime(today.year, today.month, today.day),
        models.AttendanceLog.clock_out_time == None
    ).first()
    log = active_log or db.query(models.AttendanceLog).filter(
        models.AttendanceLog.employee_id == employee_id,
        models.AttendanceLog.date >= datetime(today.year, today.month, today.day)
    ).order_by(models.AttendanceLog.date.desc()).first()

    status = "Absent"
    clock_in = None
    clock_out = None
    working_hours = 0.0

    if log:
        status = log.status
        clock_in = log.clock_in_time.strftime("%I:%M %p") if log.clock_in_time else None
        clock_out = log.clock_out_time.strftime("%I:%M %p") if log.clock_out_time else None
        working_hours = round(log.working_hours, 2)
        if log.clock_in_time and not log.clock_out_time:
            # Calculate current working hours if still clocked in
            diff = datetime.now() - log.clock_in_time
            working_hours = round(diff.total_seconds() / 3600.0, 2)

    return {
        "employee_name": employee.name,
        "designation": employee.designation,
        "status": status,
        "has_active_clock_in": bool(log and log.clock_in_time and not log.clock_out_time),
        "clock_in_time": clock_in,
        "clock_out_time": clock_out,
        "working_hours": working_hours,
        "leave_balance": 14
    }

@app.get("/api/employee/{employee_id}/attendance/history")
def get_attendance_history(employee_id: int, db: Session = Depends(get_db)):
    logs = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.employee_id == employee_id
    ).order_by(models.AttendanceLog.date.desc()).limit(30).all()
    
    return [{
        "date": log.date.strftime("%Y-%m-%d"),
        "status": log.status,
        "clock_in_time": log.clock_in_time.strftime("%I:%M %p") if log.clock_in_time else None,
        "clock_out_time": log.clock_out_time.strftime("%I:%M %p") if log.clock_out_time else None,
        "working_hours": round(log.working_hours, 2)
    } for log in logs]

@app.get("/api/attendance/status/{employee_id}")
def get_attendance_status(employee_id: int, db: Session = Depends(get_db)):
    today = date.today()
    
    log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.employee_id == employee_id,
        models.AttendanceLog.date >= datetime(today.year, today.month, today.day)
    ).first()
    
    has_active_clock_in = False
    if log and log.clock_in_time and not log.clock_out_time:
        has_active_clock_in = True
        
    return {"has_active_clock_in": has_active_clock_in}

@app.get("/api/attendance", response_model=List[schemas.AttendanceLogResponse])
def get_attendance_logs(
    employee_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    query = db.query(models.AttendanceLog)
    
    if employee_id:
        query = query.filter(models.AttendanceLog.employee_id == employee_id)
    if start_date:
        query = query.filter(models.AttendanceLog.date >= start_date)
    if end_date:
        query = query.filter(models.AttendanceLog.date <= end_date)
        
    return query.order_by(models.AttendanceLog.date.desc()).offset(skip).limit(limit).all()

@app.post("/api/attendance/manual", response_model=schemas.AttendanceLogResponse)
def create_manual_attendance(log_data: schemas.AttendanceLogCreate, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == log_data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    new_log = models.AttendanceLog(**log_data.dict())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@app.put("/api/attendance/{log_id}", response_model=schemas.AttendanceLogResponse)
def update_attendance_log(log_id: int, log_data: schemas.AttendanceLogCreate, db: Session = Depends(get_db)):
    log = db.query(models.AttendanceLog).filter(models.AttendanceLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Attendance log not found")
    for key, val in log_data.dict(exclude_unset=True).items():
        setattr(log, key, val)
    db.commit()
    db.refresh(log)
    return log

@app.get("/api/dashboard/admin-stats")
def get_admin_dashboard_stats(db: Session = Depends(get_db)):
    total_employees = db.query(models.Employee).count()
    face_registered_employees = db.query(models.Employee).filter(models.Employee.face_encoding != None).count()
    
    today = date.today()
    today_start = datetime(today.year, today.month, today.day)
    today_logs = db.query(models.AttendanceLog).filter(models.AttendanceLog.date >= today_start).all()
    
    total_present = sum(1 for l in today_logs if l.status == "Present")
    total_late = sum(1 for l in today_logs if l.status == "Late")
    total_absent = max(0, total_employees - (total_present + total_late))
    
    active_clock_ins = sum(1 for l in today_logs if l.clock_in_time and not l.clock_out_time)
    
    total_clients = db.query(pm_models.Client).filter(pm_models.Client.deleted_at == None).count()
    total_projects = db.query(pm_models.Project).filter(pm_models.Project.deleted_at == None).count()
    total_services = db.query(pm_models.Service).filter(pm_models.Service.deleted_at == None).count()
    
    # Project status counts
    all_projects = db.query(pm_models.Project).filter(pm_models.Project.deleted_at == None).all()
    project_status_counts = {}
    for p in all_projects:
        st = p.project_status or "Not Started"
        project_status_counts[st] = project_status_counts.get(st, 0) + 1
        
    # Recent projects
    recent_projects = db.query(pm_models.Project).filter(pm_models.Project.deleted_at == None).order_by(pm_models.Project.id.desc()).limit(5).all()
    recent_projects_data = [{
        "id": p.id,
        "project_code": p.project_code,
        "project_title": p.project_title,
        "status": p.project_status,
        "start_date": p.project_start_date.strftime("%Y-%m-%d") if p.project_start_date else "N/A",
        "deadline": p.expected_end_date.strftime("%Y-%m-%d") if p.expected_end_date else "N/A",
        "total_budget": p.budget or 0,
        "client_id": p.client_id
    } for p in recent_projects]
    
    # Recent clients
    recent_clients = db.query(pm_models.Client).filter(pm_models.Client.deleted_at == None).order_by(pm_models.Client.id.desc()).limit(5).all()
    recent_clients_data = [{
        "id": c.id,
        "client_code": c.client_code,
        "display_name": c.display_name,
        "email": c.email,
        "client_type": c.client_type,
        "status": c.status
    } for c in recent_clients]

    # Recent attendance logs today
    recent_logs_data = []
    for l in sorted(today_logs, key=lambda x: x.clock_in_time or x.date, reverse=True)[:5]:
        emp = l.employee
        recent_logs_data.append({
            "id": l.id,
            "employee_id": l.employee_id,
            "employee_name": emp.name if emp else "Unknown",
            "designation": emp.designation if emp else "",
            "status": l.status,
            "clock_in_time": l.clock_in_time.strftime("%I:%M %p") if l.clock_in_time else "N/A",
            "clock_out_time": l.clock_out_time.strftime("%I:%M %p") if l.clock_out_time else "N/A",
            "working_hours": round(l.working_hours, 2)
        })

    return {
        "total_employees": total_employees,
        "face_registered_employees": face_registered_employees,
        "today_attendance": {
            "total_present": total_present,
            "total_late": total_late,
            "total_absent": total_absent,
            "active_clock_ins": active_clock_ins,
            "recent_logs": recent_logs_data
        },
        "total_clients": total_clients,
        "total_projects": total_projects,
        "total_services": total_services,
        "project_status_counts": project_status_counts,
        "recent_projects": recent_projects_data,
        "recent_clients": recent_clients_data
    }

@app.get("/api/settings", response_model=schemas.CompanySettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(models.CompanySettings).first()
    if not settings:
        settings = models.CompanySettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@app.post("/api/settings", response_model=schemas.CompanySettingsResponse)
def update_settings(settings_data: schemas.CompanySettingsCreate, db: Session = Depends(get_db)):
    settings = db.query(models.CompanySettings).first()
    if not settings:
        settings = models.CompanySettings(**settings_data.dict())
        db.add(settings)
    else:
        for key, value in settings_data.dict().items():
            setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings


@app.get("/api/employees/{employee_id}", response_model=schemas.EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {
        "id": employee.id,
        "name": employee.name,
        "phone": employee.phone,
        "email": employee.email,
        "designation": employee.designation,
        "salary": employee.salary,
        "salary_type": employee.salary_type,
        "nid_front_path": employee.nid_front_path,
        "nid_back_path": employee.nid_back_path,
        "face_registered": bool(employee.face_encoding),
        "dynamic_data": employee.dynamic_data,
        "created_at": employee.created_at
    }

@app.delete("/api/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}

@app.put("/api/employees/{employee_id}", response_model=schemas.EmployeeResponse)
def update_employee(
    employee_id: int,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    designation: str = Form(...),
    salary: float = Form(...),
    salary_type: str = Form(...),
    nid_front: UploadFile = File(None),
    nid_back: UploadFile = File(None),
    face_image: UploadFile = File(None),
    dynamic_data: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Check if email is being updated to an existing one
    if email != employee.email:
        existing = db.query(models.Employee).filter(models.Employee.email == email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
            
    employee.name = name
    employee.phone = phone
    employee.email = email
    employee.designation = designation
    employee.salary = salary
    employee.salary_type = salary_type
    employee.dynamic_data = dynamic_data

    if face_image:
        image_bytes = face_image.file.read()
        encoding_json = face_service.get_face_encoding(image_bytes)
        if not encoding_json:
            raise HTTPException(status_code=400, detail="Could not detect a face in the image")
        employee.face_encoding = encoding_json

    os.makedirs("uploads", exist_ok=True)
    if nid_front:
        nid_front_path = f"uploads/{uuid.uuid4()}_{nid_front.filename}"
        with open(nid_front_path, "wb") as buffer:
            shutil.copyfileobj(nid_front.file, buffer)
        employee.nid_front_path = nid_front_path

    if nid_back:
        nid_back_path = f"uploads/{uuid.uuid4()}_{nid_back.filename}"
        with open(nid_back_path, "wb") as buffer:
            shutil.copyfileobj(nid_back.file, buffer)
        employee.nid_back_path = nid_back_path

    db.commit()
    db.refresh(employee)

    return {
        "id": employee.id,
        "name": employee.name,
        "phone": employee.phone,
        "email": employee.email,
        "designation": employee.designation,
        "salary": employee.salary,
        "salary_type": employee.salary_type,
        "nid_front_path": employee.nid_front_path,
        "nid_back_path": employee.nid_back_path,
        "face_registered": bool(employee.face_encoding),
        "dynamic_data": employee.dynamic_data,
        "created_at": employee.created_at
    }

# --- Employee Field Routes ---


@app.get("/api/employee-fields", response_model=List[schemas.EmployeeFieldResponse])
def get_employee_fields(db: Session = Depends(get_db)):
    return db.query(models.EmployeeField).order_by(models.EmployeeField.order.asc(), models.EmployeeField.id.asc()).all()

@app.post("/api/employee-fields", response_model=schemas.EmployeeFieldResponse)
def create_employee_field(field: schemas.EmployeeFieldCreate, db: Session = Depends(get_db)):
    db_field = models.EmployeeField(**field.dict())
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

@app.put("/api/employee-fields/{field_id}", response_model=schemas.EmployeeFieldResponse)
def update_employee_field(field_id: int, field: schemas.EmployeeFieldCreate, db: Session = Depends(get_db)):
    db_field = db.query(models.EmployeeField).filter(models.EmployeeField.id == field_id).first()
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    for key, value in field.dict().items():
        setattr(db_field, key, value)
        
    db.commit()
    db.refresh(db_field)
    return db_field

@app.delete("/api/employee-fields/{field_id}")
def delete_employee_field(field_id: int, db: Session = Depends(get_db)):
    db_field = db.query(models.EmployeeField).filter(models.EmployeeField.id == field_id).first()
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
        
    db.delete(db_field)
    db.commit()
    return {"message": "Field deleted successfully"}

# --- SMTP Settings Routes ---
@app.get("/api/smtp-settings", response_model=schemas.SMTPSettingsResponse)
def get_smtp_settings(db: Session = Depends(get_db)):
    settings = db.query(models.SMTPSettings).first()
    if not settings:
        settings = models.SMTPSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@app.post("/api/smtp-settings", response_model=schemas.SMTPSettingsResponse)
def update_smtp_settings(settings_data: schemas.SMTPSettingsCreate, db: Session = Depends(get_db)):
    settings = db.query(models.SMTPSettings).first()
    if not settings:
        settings = models.SMTPSettings(**settings_data.dict())
        db.add(settings)
    else:
        for key, value in settings_data.dict().items():
            setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings
