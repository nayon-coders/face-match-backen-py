with open("main.py", "r") as f:
    content = f.read()

import_line = "from fastapi.staticfiles import StaticFiles\n"
if "StaticFiles" not in content:
    content = content.replace("from fastapi.middleware.cors import CORSMiddleware", "from fastapi.middleware.cors import CORSMiddleware\n" + import_line)

mount_line = """
app = FastAPI(title="FaceAttend API")
import os
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
"""
if "app.mount(\"/uploads\"" not in content:
    content = content.replace("app = FastAPI(title=\"FaceAttend API\")", mount_line)

with open("main.py", "w") as f:
    f.write(content)
