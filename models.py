from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import enum
from enum import Enum as PyEnum
import passlib.hash as _hash
from datetime import datetime

class UserType(str,PyEnum):
    USER = "user"
    SUPERUSER = "superuser"


class Employee(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True,index=True,nullable=False)
    name = Column(String,index=True,nullable=False)
    org = Column(String,index=True)
    user_type = Column(Enum(UserType),default=UserType.USER, nullable=False)
    hashed_password = Column(String,nullable=False)
    leave_requests = relationship("LeaveRequest", back_populates="user")

    def set_password(self,password: str):
    #     '''Hash and set the user password'''
        self.hashed_password = _hash.bcrypt.hash(password)

    def verify_password(self,password: str) -> bool :
    #     # Verify the user password
        return _hash.bcrypt.verify(password,self.hashed_password)
    

class LeaveStatus(str,enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    last_day_of_work = Column(Date,nullable=False)
    leave_start_date = Column(Date,nullable = False)
    return_to_work_date = Column(Date,nullable=False)
    num_days_on_leave = Column(Integer, nullable=False)
    reason = Column(String, nullable = False)
    status = Column(Enum(LeaveStatus),default = LeaveStatus.PENDING, nullable=False)
    date_submitted = Column(DateTime, default = datetime.utcnow)

    user = relationship("Employee", back_populates="leave_requests")


    

