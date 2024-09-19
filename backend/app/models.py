from sqlalchemy import Column, Integer, TIMESTAMP, String, ForeignKey, Date
from database import Base

class Employee(Base):
    __tablename__ = 'employee'
    staff_id = Column(Integer, primary_key=True)
    staff_fname = Column(String(64), nullable=False)
    staff_lname = Column(String(64), nullable=False)
    dept = Column(String(64), nullable=True)
    position = Column(String(64), nullable=False)
    country = Column(String(64), nullable=False)
    email = Column(String(256), nullable=False)
    reporting_manager = Column(Integer, ForeignKey("employee.staff_id"), nullable=False)
    role = Column(Integer, nullable=False)
    
  
class Schedule(Base):
    __tablename__ = 'schedule'
    schedule_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(String(2), nullable=False)
    reason = Column(String(256), nullable=True)
    status = Column(Integer, nullable=False)

class Team(Base):
    __tablename__ = 'team'
    team_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, primary_key=True)
