
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import date, datetime  # Import datetime

class UserType(str, Enum):
    USER = "user"
    SUPERUSER = "superuser"


class EmployeeBase(BaseModel):
    email: EmailStr
    name: str
    org: str
    user_type: UserType


class EmployeeCreate(EmployeeBase):
    password: str


class Employee(EmployeeBase):
    id: int
    user_type: str

    class Config:
        orm_mode = True  # Corrected the attribute


class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    user_type: str


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LeaveRequestBase(BaseModel):
    last_day_of_work: date
    leave_start_date: date
    return_to_work_date: date
    num_days_on_leave: int
    reason: str


class LeaveRequestCreate(LeaveRequestBase):
    pass


class LeaveRequestUpdate(BaseModel):
    status: LeaveStatus


class LeaveRequest(LeaveRequestBase):
    id: int
    user_id: int
    status: LeaveStatus
    date_submitted: datetime  # Changed to datetime

    class Config:
        orm_mode = True  # Corrected the attribute
