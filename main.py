from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import sessionLocal, engine
from models import Base, Employee as DBEmployee, Task as DBTask
from pydantic import BaseModel, Field
from typing import List
from datetime import date, datetime, timedelta
import security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

class EmployeeBase(BaseModel):
    name : str
    availability : List[date]
    skills : set[str]
    maxWeeklyHours : float

class EmployeeCreate(EmployeeBase):
    password : str
    role : str = "employee"


class EmployeeOut(EmployeeBase):
    id : int
    fatigue : int
    hoursWorked : float
    recentShift : List[datetime]
    role : str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token : str
    token_type : str

class Tasks(BaseModel):
    skills : set[str]
    time : datetime
    hoursRequired : float
    members : int
    end : datetime = Field(default_factory=lambda: datetime.min)

    class Config:
        from_attributes = True

Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token : str = Depends(oauth2_scheme), db : Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate" : "Bearer"}
    )
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    
    except security.JWTError:
        raise credentials_exception
    
    user = db.query(DBEmployee).filter(DBEmployee.name == username).first()
    if user is None:
        raise credentials_exception
    
    return user


def require_manager(currentuser : DBEmployee = Depends(get_current_user)):
    if currentuser.role != "manager":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return currentuser





@app.post("/register", response_model=EmployeeOut, status_code=201)
def register_user(user : EmployeeCreate, db : Session = Depends(get_db)):
    existing_employee = db.query(DBEmployee).filter(DBEmployee.name == user.name).first()
    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="A user with this name already exists."
        )
    
    user_count = db.query(DBEmployee).count()
    if user_count == 0:
        user.role = "manager"
    else:
        user.role = "employee"

    hashed_password = security.get_password_hash(user.password)
    new_employee = DBEmployee(
        name=user.name,
        hashed_password=hashed_password,
        role=user.role,
        availability=[d.isoformat() for d in user.availability],
        skills=list(user.skills),
        maxWeeklyHours=user.maxWeeklyHours
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee







@app.post("/token", response_model=Token)
def login_for_access_token(form_data : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    user = db.query(DBEmployee).filter(form_data.username == DBEmployee.name).first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password"
        )
    
    access_token = security.create_access_token(data={"sub" : user.name})
    return {"access_token" : access_token, "token_type" : "bearer"}

@app.post("/users/me", response_model=EmployeeOut)
def read_user_me(current_user : DBEmployee = Depends(get_current_user)):
    "Fetch details for the currently logged-in user"
    return current_user


@app.get("/employees", response_model=List[EmployeeOut], dependencies=[Depends(require_manager)])
def get_all_employees(db: Session = Depends(get_db)):
    employees = db.query(DBEmployee).all()
    return employees


@app.post("/employees", response_model=EmployeeOut, status_code=201, dependencies=[Depends(require_manager)])
def add_employee(Employee : EmployeeCreate, db: Session = Depends(get_db)):

    existing_employees = db.query(DBEmployee).filter(DBEmployee.name == Employee.name).first()
    if existing_employees:
        raise HTTPException(status_code=400, detail="Employee with this name already exists...")
    
    availability_as_strings = [d.isoformat() for d in Employee.availability]
    hashed_password = security.get_password_hash(Employee.password)

    new_employee = DBEmployee(
        name=Employee.name,
        hashed_password=hashed_password,
        role = Employee.role,
        availability=availability_as_strings,
        skills=list(Employee.skills), 
        maxWeeklyHours=Employee.maxWeeklyHours
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee

@app.get("/employees/{id}")
def get_Employee_by_id(id : int, db: Session = Depends(get_db)):
    employee = db.query(DBEmployee).filter(DBEmployee.id == id).first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee

@app.post("/task")
def allote_members(task : Tasks, db: Session = Depends(get_db)):
    task.end = task.time + timedelta(hours=task.hoursRequired)

    new_task = DBTask(
        skills=list(task.skills),
        time=task.time,
        hoursRequired=task.hoursRequired,
        members=task.members,
        end=task.end
    )

    db.add(new_task)


    employees = db.query(DBEmployee).all()
    sorted_employees = sorted(employees, key = lambda i : i.fatigue)
    alloted : List[DBEmployee] = []
    for employee in sorted_employees:
        if(len(alloted) >= task.members): 
            break
        
        if task.skills.issubset(employee.skills):
            if not employee.availability or len(employee.availability) < 2: continue

            employee_starting = datetime.fromisoformat(employee.availability[0])
            employee_ending = datetime.fromisoformat(employee.availability[1])
            if employee_starting > task.time: continue
            if employee_ending < task.end: continue
            recent_shifts_as_dates = [datetime.fromisoformat(s) for s in employee.recentShift]
            if recent_shifts_as_dates and (task.end - recent_shifts_as_dates[-1]).days >= 7:
                employee.fatigue = 0
                employee.hoursWorked = 0

            if (recent_shifts_as_dates and recent_shifts_as_dates[-1] >= task.time )or employee.fatigue >= 4: continue
            
            new_fatigue = employee.fatigue

            if recent_shifts_as_dates and (task.end - recent_shifts_as_dates[-1]).total_seconds() <= 86400: new_fatigue += 1
            if employee.hoursWorked + task.hoursRequired > employee.maxWeeklyHours: new_fatigue += 2

            if new_fatigue >= 4: continue

            employee.hoursWorked += task.hoursRequired
            employee.fatigue = new_fatigue
            new_shift_as_string = task.end.isoformat()
            current_shifts = employee.recentShift or []
            employee.recentShift = current_shifts + [new_shift_as_string]
            alloted.append(employee)
            print(alloted[0].name)

    if(len(alloted) < task.members):
        raise HTTPException(status_code=409, detail="Not suitable employees...")
    
    db.commit()
    print(len(alloted))
    for emp in alloted:
        db.refresh(emp)
    return alloted