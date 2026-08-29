from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# No more HR/Attendance specific models in this file.
# We are pivoting to an API-as-a-Service model.

