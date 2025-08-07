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
        orm_mode = True

class Tasks(BaseModel):
    skills : set[str]
    time : datetime
    hoursRequired : float
    members : int
    end : datetime = Field(default_factory=lambda: datetime.min)

    class Config:
        orm_mode = True

employees : List[User] = []
tasks : List[Tasks] = []

Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


def load_Employees():
    global employees
    db = next(get_db())

    db_employees = db.query(DBEmployee).all()

    employees = [
        User(
            id=u.id,
            name=u.name,
            availability=u.availability,
            skills=set(u.skills.split(",")),
            maxWeeklyHours=u.maxWeeklyHours,
            fatigue=u.fatigue,
            hoursWorked=u.hoursWorked,
            recentShift=u.recentShift
        ) for u in db_employees
    ]


def load_Tasks():
    global tasks
    db = next(get_db())

    db_tasks = db.query(DBTask).all()
    tasks = [
        Tasks(
            skills=set(t.skills.split(",")),
            time=t.time,
            hoursRequired=t.hoursRequired,
            members=t.members,
            end=t.end
        )
        for t in db_tasks
    ]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Loading data on startup...")

    load_Employees()
    load_Tasks()

    print("INFO:     Data loading complete.")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/employees")
def print_employees():
    return employees


@app.post("/employees")
def add_user(user : User):
    # mod_user = {"ind" : ind+1, **user}
    # employees.append(mod_user)
    # return mod_user

    for i in employees:
        if i.id == user.id:
            return "User already exists..."

    mod_user = user.model_copy(update={"fatigue": 0, "hoursWorked": 0, "recentShift": []})
    employees.append(mod_user)
    return mod_user

@app.get("/employees/{id}")
def get_user_by_id(id : int, db: Session = Depends(get_db)):
    for i in employees:
        if i.id == id:
            return i
    
    return "User not exists"

@app.post("/task")
def allote_members(task : Tasks):
    global employees
    task = task.model_copy(update={"end": task.time + timedelta(hours=task.hoursRequired)})
    sorted_employees = sorted(employees, key = lambda i : i.fatigue)
    alloted : List[User] = []
    for i in sorted_employees:
        if(len(alloted) >= task.members): 
            return alloted
        
        if task.skills.issubset(i.skills):
            if i.recentShift and (task.end - i.recentShift[-1]).days >= 7:
                i.fatigue = 0
                i.hoursWorked = 0
            if (i.recentShift and i.recentShift[-1] >= task.time )or i.fatigue >= 4: continue
            new_fatigue = i.fatigue
            if i.recentShift and (task.end - i.recentShift[-1]).total_seconds() <= 86400: new_fatigue += 1
            if i.hoursWorked + task.hoursRequired > i.maxWeeklyHours: new_fatigue += 2

            if new_fatigue >= 4: continue

            i.hoursWorked += task.hoursRequired
            i.fatigue = new_fatigue
            i.recentShift.append(task.end)
            alloted.append(i)

    if(len(alloted) >= task.members):
        employees = sorted_employees
        return alloted
    return "There are less number of employees to complete the task..."
