import sys
from database import SessionLocal
from pm_schemas import ClientCreate
from repositories.client_repo import client_repo

db = SessionLocal()
client_in = ClientCreate(client_name="Test2", display_name="Test2", client_type="Company", email="test2@test.com")
try:
    c = client_repo.create_with_code(db, client_in)
    print("Success:", c.id)
except Exception as e:
    import traceback
    traceback.print_exc()
