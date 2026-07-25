import re

with open("main.py", "r") as f:
    content = f.read()

# Add BackgroundTasks
content = content.replace("from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form", "from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks")

# Define send_email_task
email_func = """
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
"""
content = content.replace("@app.on_event(\"startup\")", email_func)

# Modify create_employee signature
old_sig = """    face_image: UploadFile = File(None),
    dynamic_data: str = Form(None),
    db: Session = Depends(get_db)
):"""
new_sig = """    face_image: UploadFile = File(None),
    dynamic_data: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):"""
content = content.replace(old_sig, new_sig)

# Modify email sending logic
old_logic = """    # Send email
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
            print(f"Failed to send email: {e}")"""

new_logic = """    # Send email
    smtp_settings = db.query(models.SMTPSettings).first()
    if smtp_settings and smtp_settings.host and smtp_settings.sender_email:
        subject = "Welcome to MY HRM - Account Created"
        body = f"Hello {name},\\n\\nYour account has been created successfully.\\nEmail: {email}\\nPassword: {raw_password}\\n\\nPlease log in and change your password.\\n\\nBest Regards,\\nHR Team"
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
        )"""
content = content.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(content)
