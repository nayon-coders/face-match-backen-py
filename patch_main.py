import re

with open("main.py", "r") as f:
    content = f.read()

# Add imports
imports_to_add = """import os
import shutil
import uuid
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
"""

content = content.replace("import models, schemas, database, face_service", imports_to_add + "\nimport models, schemas, database, face_service")

# Remove old os, shutil, uuid imports
content = content.replace("import os\nimport shutil\nimport uuid\n", "")


# Update create_employee
old_create_employee = """    encoding_json = None
    if face_image:"""

new_create_employee = """    existing_employee = db.query(models.Employee).filter(models.Employee.email == email).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Email already registered")

    encoding_json = None
    if face_image:"""

content = content.replace(old_create_employee, new_create_employee)

old_db_employee = """    db_employee = models.Employee(
        name=name,"""

new_db_employee = """    raw_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    hashed_password = pwd_context.hash(raw_password)

    db_employee = models.Employee(
        name=name,
        password=hashed_password,"""

content = content.replace(old_db_employee, new_db_employee)


old_db_refresh = """    db.refresh(db_employee)
    
    return {"""

new_db_refresh = """    db.refresh(db_employee)
    
    # Send email
    smtp_settings = db.query(models.SMTPSettings).first()
    if smtp_settings and smtp_settings.host and smtp_settings.sender_email:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_settings.sender_email
            msg['To'] = email
            msg['Subject'] = "Welcome to MY HRM - Account Created"
            body = f"Hello {name},\\n\\nYour account has been created successfully.\\nEmail: {email}\\nPassword: {raw_password}\\n\\nPlease log in and change your password.\\n\\nBest Regards,\\nHR Team"
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(smtp_settings.host, smtp_settings.port)
            if smtp_settings.use_tls:
                server.starttls()
            if smtp_settings.username and smtp_settings.password:
                server.login(smtp_settings.username, smtp_settings.password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")

    return {"""

content = content.replace(old_db_refresh, new_db_refresh)

# Add SMTP routes
smtp_routes = """
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
"""

content += smtp_routes

with open("main.py", "w") as f:
    f.write(content)

