from datetime import datetime

from sqlalchemy import Integer, Boolean, DateTime, String, Column
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
