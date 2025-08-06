from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import date, time

class User(BaseModel):
    id: int
    name : str
    availability : List[date]
    skills : set[str]
    maxWeeklyHours : float
    hoursWorked : float
    recentShift : List[time]
    fatigue : int

class Tasks(BaseModel):
    skills : set[str]
    members : int

users : List[User] = []


app = FastAPI()
ind : int = 1

@app.get("/employees")
def print_Users():
    return users


@app.post("/employees")
def read_root(user : User):
    # mod_user = {"ind" : ind+1, **user}
    # users.append(mod_user)
    # return mod_user

    for i in users:
        if i.id == user.id:
            return "User already exists..."

    users.append(user)
    return user

@app.post("/task")
def allote_members(task : Tasks):
    sorted(users, key = lambda i : i.fatigue)
    alloted : List[User]
    for i in users:
        if(len(alloted) >= task.members): 
            return alloted
        if task.skills.issubset(i.skills):
            alloted.append(i)
    
    if(len(alloted) >= task.members): return alloted
    return "There are less number of employees to complete the task..."
