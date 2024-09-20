

from fastapi import FastAPI, Depends, HTTPException, status  # Import Depends and HTTPException
from sqlalchemy.orm import Session  # Import Session
from fastapi.middleware.cors import CORSMiddleware
from . import crud, models, schemas, auth, database
from .database import SessionLocal, engine
from typing import List  
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from .auth import get_current_user, get_current_superuser

models.Base.metadata.create_all(bind=engine)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(debug=True)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust according to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee Management System!"}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "user_type": user.user_type, "user_name": user.name},  # Include user_name and user_type
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name,  # Include user_name in the response
        "user_type": user.user_type  # Include user_type in the response
    }

@app.get("/api/employees", response_model=List[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    employees = db.query(models.Employee).offset(skip).limit(limit).all()
    return employees

@app.post("/api/employees", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = crud.get_employee_by_email(db, email=employee.email)
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_employee(db=db, employee=employee, password=employee.password)

@app.get("/api/employees/{employee_id}", response_model=schemas.Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.put("/api/employees/{employee_id}", response_model=schemas.Employee)
def update_employee(employee_id: int, employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.update_employee(db=db, employee_id=employee_id, employee=employee)

@app.delete("/api/employees/{employee_id}", response_model=schemas.Employee)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.delete_employee(db=db, employee_id=employee_id)

@app.post("/api/leave-requests/", response_model=schemas.LeaveRequest)
def create_leave_request(
    leave_request: schemas.LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_employee: schemas.Employee = Depends(auth.get_current_user)
):
    return crud.create_leave_request(db=db, leave_request=leave_request, user_id=current_employee.id)

@app.get("/api/leave-requests/", response_model=List[schemas.LeaveRequest])
def read_leave_requests(
    db: Session = Depends(get_db),
    current_employee: schemas.Employee = Depends(auth.get_current_user)
):
    if current_employee.user_type == schemas.UserType.SUPERUSER:
        return crud.get_leave_requests(db=db)
    return crud.get_leave_requests_by_user(db=db, user_id=current_employee.id)

@app.put("/api/leave-requests/{leave_request_id}", response_model=schemas.LeaveRequest)
def update_leave_request_status(
    leave_request_id: int,
    status: schemas.LeaveRequestUpdate,
    db: Session = Depends(get_db),
    current_superuser: schemas.Employee = Depends(auth.get_current_superuser)
):
    leave_request = crud.update_leave_request_status(db=db, leave_request_id=leave_request_id, status=status.status)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave_request
