from config import  MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import (
    EmailLog
)
from dependency import * 
import smtplib
import traceback
from celery import Celery
app=Celery('task',backend='redis://localhost',broker='redis://localhost')


@app.task(bind=True)
def send_event_email(self,event):
    try:
        port = MAIL_PORT
        smtp_server = MAIL_SERVER
        login = MAIL_USERNAME  
        password = MAIL_PASSWORD 
        sender_email = "contact@tran.co.in"
        message = MIMEMultipart("alternative")
        message["Subject"] = "Greetings"
        message["From"] = sender_email
        message["To"] = event["email"]
        
        # write the text/plain part
        text = f"""
        Dear {event["name"]},

        {event["template"]}
        
        """

        # convert both parts to MIMEText objects and add them to the MIMEMultipart message
        part1 = MIMEText(text, "plain")
        message.attach(part1)

        max_retiries=3
        retry_count = 0
        sent_successfully = False
        while retry_count < max_retiries and not sent_successfully:
            try:
                # send your email
                with smtplib.SMTP(smtp_server, port) as server:
                    server.login(login, password)
                    server.sendmail(
                            sender_email, event["email"], message.as_string())
                add_emaillog =EmailLog(
                    employee_id=event["employee_id"],
                    event_id=event["event_id"],
                    status="Delivered"
                )
                session.add(add_emaillog)
                session.commit()
                retry_count=3
            except Exception as e:
                print(f"Email delivery attempt {retry_count + 1} failed: {str(e)}")
                retry_count += 1

        return "success"
    except Exception as e:
        print(e)
        
        traceback_str = traceback.format_exc()
        add_emaillog =EmailLog(
            employee_id=event["employee_id"],
            event_id=event["event_id"],
            status="Failed",
            error_message=str(e)
        )
        session.add(add_emaillog)
        session.commit()
