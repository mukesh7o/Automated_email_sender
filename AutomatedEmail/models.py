from sqlalchemy import Column, Integer, String, ForeignKey,TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from dependency import *

class Employee(base):
    __tablename__= "employee"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

class Event(base):
    __tablename__= "event"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id'))
    event_type = Column(String)
    event_date = Column(TIMESTAMP, default=datetime.utcnow())

    employee = relationship("Employee", backref="events")

class EmailTemplate(base):
    __tablename__= "email_template"
    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    template = Column(String)

class EmailLog(base):
    __tablename__= "email_log"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id'))
    event_id = Column(Integer, ForeignKey('event.id'))
    status = Column(String)
    error_message = Column(String)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow()) 

class DailyReport(base):
    __tablename__= "daily_report"
    id = Column(Integer, primary_key=True)
    status=Column(String)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow())

base.metadata.create_all(bind=engine, checkfirst=True)