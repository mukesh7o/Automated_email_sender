from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse
from datetime import datetime,date
from task import send_event_email
from models import Event,DailyReport
from sqlalchemy import exc
from db_query import (
    employee_email,
    get_employees,
    check_employee,
    get_events,
    initialize_project_data,
    get_email_log,
    get_daily_reports
    )

from dependency import *

from models import (
    Employee,
    Event,
    EmailTemplate
)

import re 
import logging

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
api = Api(app, prefix='/api')


class RecordEmployeeData(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='Missing param: name', required=True)
        parser.add_argument('email', type=str, help='Missing param: email', required=True)

        args = parser.parse_args()
        
        try:
            email = args['email']
            name = args['name']
            EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

            if not EMAIL_REGEX.match(email):
                return {'message': 'Invalid Email'}, 406
            
            #check if email already exist 
            if employee_email(email):   
                return {'message': 'Email already exists'}, 406
            else:
                new_employee = Employee(
                    name=name,
                    email=email
                )
                db.session.add(new_employee)
                db.session.commit()
                return {'message': 'Employee added successfully'}, 201
            
            
        except exc.SQLAlchemyError as err:
            logging.error(f"Database error: {err}")
            return jsonify({'error': 'Database error'}), 500  # Log the error and return an error response
        finally:
            db.session.close()
        
    def get(self):
        return get_employees()
    

class EmployeeEvent(Resource):

    def post(self):
        ALLOWED_EVENT_TYPES = ["Birthday", "Anniversary"]

        parser = reqparse.RequestParser()
        parser.add_argument('event_type', type=str, help='Missing param: event_type', required=True)
        parser.add_argument('employee_id', type=int, help='Missing param: employee_id', required=True)
        parser.add_argument('event_date', type=float, help='Missing param: event_date', required=True)

        def validate_event_type(event_type):
            if event_type not in ALLOWED_EVENT_TYPES:
                raise ValueError(f'Invalid event_type: {event_type}, only Birthday, Anniversary are allowed.')
            return event_type

        parser.add_argument('event_type', type=validate_event_type)

        args = parser.parse_args()
        
        try:
            event_type = args['event_type']
            employee_id = args['employee_id']
            event_date = args['event_date']

            event_date = datetime.fromtimestamp(event_date).strftime("%Y-%m-%d")

            if check_employee(employee_id):
                add_event=Event(
                    employee_id=employee_id,
                    event_date=event_date,
                    event_type=event_type
                )
                db.session.add(add_event)
                db.session.commit()
                return {'message': 'Employee Event added successfully'}, 201
            else:
                 return {'message': 'Employee id not found please provide correct one!'}, 404

            
            
            
        except exc.SQLAlchemyError as err:
            logging.error(f"Database error: {err}")
            return jsonify({'error': 'Database error'}), 500  # Log the error and return an error response
        finally:
            db.session.close()

    def get(self):
        return get_events()


class EmployeeLogs(Resource):
    def get(self):
        return get_email_log()


class SendGreetings(Resource):
    def get(self):
        query_data = (
        session.query(Event.id.label("event_id"),Employee.id.label("employee_id"),Event.event_type,Employee.name,Employee.email,EmailTemplate.template)
        .join(Event,Employee.id==Event.employee_id)  # Join Event and Employee tables on employee_id
        .join(EmailTemplate, Event.event_type == EmailTemplate.event_type)  # Join EmailTemplate using event_type
        .filter(Event.event_date == date.today())  # Filter by event_date
        .all()
    )   
        data=[{'event_id':event.event_id,"email":event.email,'employee_id':event.employee_id,'event_type': event.event_type, 'name': event.name, 'template': event.template} for event in query_data]
        
        if len(data)==0:
            daily_report=DailyReport(
                status= "NO EMAILS"
            )
            session.add(daily_report)
            session.commit()
            return "No emails for today"
        else:
            for event in data:
                send_event_email.delay(event)
            return "Emails scheduled for sending."


class DailySentReport(Resource):
    def get(self):
        return get_daily_reports()
        

api.add_resource(RecordEmployeeData,'/record/employee-data')
api.add_resource(EmployeeEvent,'/employee-event')
api.add_resource(EmployeeLogs,'/employee-logs')
api.add_resource(SendGreetings,'/send-greetings')
api.add_resource(DailySentReport,'/daily-sent-report')
initialize_project_data()
if __name__ == '__main__':
    app.run(debug=True)
    
    

