from sqlalchemy import Table, Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DATETIME
import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = "Employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    availability = Column(JSON)
    skills = Column(JSON)
    maxWeeklyHours = Column(Float)
    fatigue = Column(Integer, default=0)
    hoursWorked = Column(Float, default=0)
    recentShift = Column(JSON, default=list)


class Task(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    skills = Column(JSON)
    time = Column(DATETIME)
    hoursRequired = Column(Float)
    members = Column(Integer)
    end = Column(DATETIME)