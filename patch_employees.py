import re

with open("main.py", "r") as f:
    content = f.read()

new_routes = """
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
"""

content = content.replace("# --- Employee Field Routes ---", new_routes)

with open("main.py", "w") as f:
    f.write(content)

