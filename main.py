from fastapi import FastAPI
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

class Tasks(BaseModel):
    skills : set[str]
    time : datetime
    hoursRequired : float
    members : int
    end : datetime = Field(default_factory=lambda: datetime.min)

users : List[User] = []


app = FastAPI()
ind : int = 1

@app.get("/employees")
def print_Users():
    return users


@app.post("/employees")
def add_user(user : User):
    # mod_user = {"ind" : ind+1, **user}
    # users.append(mod_user)
    # return mod_user

    for i in users:
        if i.id == user.id:
            return "User already exists..."

    mod_user = user.model_copy(update={"fatigue": 0, "hoursWorked": 0, "recentShift": []})
    users.append(mod_user)
    return mod_user

@app.get("/employees/{id}")
def print_user(id : int):
    for i in users:
        if i.id == id:
            return i
    
    return "User not exists"

@app.post("/task")
def allote_members(task : Tasks):
    global users
    task = task.model_copy(update={"end": task.time + timedelta(hours=task.hoursRequired)})
    sorted_users = sorted(users, key = lambda i : i.fatigue)
    alloted : List[User] = []
    for i in sorted_users:
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
        users = sorted_users
        return alloted
    return "There are less number of employees to complete the task..."
