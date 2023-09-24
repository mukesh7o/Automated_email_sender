from functools import wraps
from sqlalchemy.sql.expression import update
from flask import jsonify
from sqlalchemy import exc
from models import (
	Employee,
	Event,
	EmailTemplate,
	EmailLog,
	DailyReport
) 

from dependency import session
from sqlalchemy.exc import OperationalError, StatementError
import logging


def retry_db(exceptions, n_retries=3, ival=1):
	def decorator(fun):
		@wraps(fun)
		def wrapper(*args, **kwargs):
			exception_logged = False
			for r in range(n_retries):
				try:
					return fun(*args, **kwargs)
				except exceptions as e:
					if not exception_logged:
						print(e)
						exception_logged = True
					else:
						print("Retry #{r} after receiving exception.")

					time.sleep(ival)
			return fun(*args, **kwargs)
		return wrapper
	return decorator


@retry_db((OperationalError, StatementError), n_retries=30)
def employee_email(email):
	try:
		check_email = session.query(Employee).filter(Employee.email== email).first()
		if check_email:
			logging.error(f"{email} ---> Email Already Exist")
			return True
		else:
			return False 
	except exc.SQLAlchemyError as err:
		print(err)
		
@retry_db((OperationalError, StatementError), n_retries=30)
def get_employees():
	try:
		check_email = session.query(Employee).all()
		employee_list = [{'id': employee.id, 'name': employee.name, 'email': employee.email} for employee in check_email]
		return jsonify(employee_list)
	except exc.SQLAlchemyError as err:
		print(err)
		
@retry_db((OperationalError, StatementError), n_retries=30)
def check_employee(employee_id):
	try:
		check_email = session.query(Employee).filter(Employee.id==employee_id).first()
		if check_email:
			return True
		else:
			return False
	except exc.SQLAlchemyError as err:
		print(err)
    
@retry_db((OperationalError, StatementError), n_retries=30)
def get_events():
	try:
		check_events = session.query(Event).all()
		employee_list = [{'id': event.id, 'employee_id': event.employee_id, 'event_type': event.event_type,'event_date': event.event_type} for event in check_events]
		return jsonify(employee_list)
	except exc.SQLAlchemyError as err:
		print(err)
		
@retry_db((OperationalError, StatementError), n_retries=30)
def get_email_log():
	try:
		check_logs = session.query(EmailLog).all()
		email_logs = [{'id': event.id, 'employee_id': event.employee_id, 'event_id': event.event_id,'status': event.status,'error_message': event.error_message,'timestamp':event.timestamp} for event in check_logs]
		
		return jsonify(email_logs)
	except exc.SQLAlchemyError as err:
		print(err)

@retry_db((OperationalError, StatementError), n_retries=30)
def get_daily_reports():
	try:
		daily_reports = session.query(DailyReport).all()
		email_logs = [{'id': event.id, 'status': event.status, 'timestamp': event.timestamp} for event in daily_reports]
		
		return jsonify(email_logs)
	except exc.SQLAlchemyError as err:
		print(err)		


def initialize_project_data():
    try:
        # Check if "Birthday" and "Anniversary" entries already exist
        birthday_template = session.query(EmailTemplate).filter(EmailTemplate.event_type=="Birthday").first()
        anniversary_template = session.query(EmailTemplate).filter(EmailTemplate.event_type=="Anniversary").first()

        # If either template doesn't exist, add it
        if not birthday_template:
            birthday_template = EmailTemplate(event_type="Birthday", template="Happy Birthday! Best Wishes from Data Axle. Wishing you a fantastic day! May your day be filled with joy and laughter, and may the year ahead bring you success and happiness beyond measure. Cheers to another amazing year ahead!")
            session.add(birthday_template)

        if not anniversary_template:
            anniversary_template = EmailTemplate(event_type="Anniversary", template="Happy Anniversary! Best Wishes from Data Axle. Wishing you a fantastic day! May your day be filled with joy and laughter, and may the year ahead bring you success and happiness beyond measure. Cheers to another amazing year ahead!")
            session.add(anniversary_template)

        # Commit the changes
        session.commit()
    except exc.SQLAlchemyError as err:
        print(f"Error initializing project data: {err}")
    finally:
        session.close()