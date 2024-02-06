from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Box_gps(Base):
    __tablename__ = "sku_current_gps_info"

    box = Column(Integer, primary_key=True, index=True)
    modem = Column(String, index=True)
    gps = Column(String, index=True)
    uwagi = Column(String, index=True)
    time_stamp = Column(String, index=True)

class Box_bts(Base):
    __tablename__ = "sku_current_bts_info"

    box = Column(Integer, primary_key=True, index=True)
    lac = Column(String, index=True)
    cid = Column(String, index=True)
    uwagi = Column(String, index=True)
    time_stamp = Column(String, index=True)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)

    roles = relationship("Role", secondary="userroles")

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True)

class UserRole(Base):
    __tablename__ = "userroles"

    user_role_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    role_id = Column(Integer, ForeignKey("roles.role_id"))
