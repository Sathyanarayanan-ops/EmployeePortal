from sqlalchemy.orm import Session
from . import models,schemas
from typing import Optional
from .models import LeaveStatus



def get_employee(db: Session, employee_id: int)-> Optional[models.Employee]:
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employee_by_email(db:Session, email: str)-> Optional[models.Employee]:
    return db.query(models.Employee).filter(models.Employee.email == email).first()


def create_employee(db: Session, employee: schemas.EmployeeCreate, password: str) -> models.Employee:
    db_employee = models.Employee(
        email=employee.email,
        name=employee.name,
        org=employee.org,
        user_type=employee.user_type,
        hashed_password=pwd_context.hash(password)  # Use pwd_context to hash the password
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int , employee: schemas.EmployeeCreate) -> Optional[models.Employee]:
    db_employee = get_employee(db,employee_id)
    if db_employee:
        for key, value in employee.model_dump().items():
            setattr(db_employee,key,value)

        db.commit()
        db.refresh(db_employee)

    return db_employee

def delete_employee(db: Session, employee_id : int) -> Optional[models.Employee]:
    db_employee = get_employee(db,employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()

    return db_employee
    
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(db: Session, email: str, password: str):
    user = get_employee_by_email(db, email=email)  # Assuming you're using Employee instead of User
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_leave_request(db: Session, leave_request: schemas.LeaveRequestCreate, user_id: int):
    db_leave_request = models.LeaveRequest(
        user_id = user_id,
        last_day_of_work = leave_request.last_day_of_work,
        leave_start_date = leave_request.leave_start_date,
        return_to_work_date = leave_request.return_to_work_date,
        num_days_on_leave = leave_request.num_days_on_leave,
        reason = leave_request.reason,
    )
    db.add(db_leave_request)
    db.commit()
    db.refresh(db_leave_request)
    return db_leave_request


#Get all leave requests ( for super user )
def get_leave_requests(db: Session):
    return db.query(models.LeaveRequest).all()

#Get leave requests by user
def get_leave_requests_by_user(db:Session, user_id: int ):
    return db.query(models.LeaveRequest).filter(models.LeaveRequest.user_id == user_id).all()

#Update the status of a leave request
def update_leave_request_status(db: Session, leave_request_id: int, status: LeaveStatus):
    db_leave_request = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == leave_request_id).first()
    if db_leave_request:
        db_leave_request.status = status
        db.commit()
        db.refresh(db_leave_request)
    return db_leave_request
