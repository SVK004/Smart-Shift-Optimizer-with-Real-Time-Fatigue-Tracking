from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from database import sessionLocal, engine
from models import Base, Employee as DBEmployee, Task as DBTask
from pydantic import BaseModel, Field
from typing import List
from datetime import date, datetime, timedelta

class User(BaseModel):
    id: int
    name : str
    availability : List[date]
    skills : set[str]
    maxWeeklyHours : float
    fatigue : int=0
    hoursWorked : float = 0.0
    recentShift : List[datetime] = Field(default_factory=list)

    class Config:
        from_attributes = True

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

@app.get("/employees", response_model=List[User])
def print_employees(db: Session = Depends(get_db)):
    employees = db.query(DBEmployee).all()
    return employees


@app.post("/employees", response_model=User, status_code=201)
def add_user(user : User, db: Session = Depends(get_db)):

    existing_employees = db.query(DBEmployee).filter(DBEmployee.id == user.id).first()
    if existing_employees:
        raise HTTPException(status_code=400, detail="Employee with this ID already exists...")
    
    availability_as_strings = [d.isoformat() for d in user.availability]
    
    new_employee = DBEmployee(
        id=user.id,
        name=user.name,
        availability=availability_as_strings,
        skills=list(user.skills), 
        maxWeeklyHours=user.maxWeeklyHours
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee

@app.get("/employees/{id}")
def get_user_by_id(id : int, db: Session = Depends(get_db)):
    employee = db.query(DBEmployee).filter(DBEmployee.id == id).first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee

@app.post("/task")
def allote_members(task : Tasks, db: Session = Depends(get_db)):
    task.end = task.time + timedelta(hours=task.hoursRequired)
    employees = db.query(DBEmployee).all()
    sorted_employees = sorted(employees, key = lambda i : i.fatigue)
    alloted : List[DBEmployee] = []
    for employee in sorted_employees:
        if(len(alloted) >= task.members): 
            break
        
        if task.skills.issubset(employee.skills):
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