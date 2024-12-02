from database import Base, engine
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
import enum
from datetime import date




class Assignee(Base):
    __tablename__ = 'assignee'

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    department = Column(String)
    username = Column(String, unique=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)



class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String) 
    description = Column(String)
    priority = Column(Integer)  # Must absolutely take a value (1, 2, 3)
    due_date = Column(Date, default=None)
    task_status = Column(Boolean, default=False)
    notes = Column(String)
    owner_id = Column(Integer, ForeignKey("assignee.id"))



