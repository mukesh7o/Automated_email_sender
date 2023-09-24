# Automated_email_sender

#Help full commands to run the project 
1. celery -A task worker --pool=solo --loglevel=info
2. http://127.0.0.1:5000/api/record/employee-data  --->Post
3. http://127.0.0.1:5000/api/employee-event ---> Post
4. http://127.0.0.1:5000/api/record/employee-data --> Get
5. http://127.0.0.1:5000/api/employee-event --->Get
6. http://127.0.0.1:5000/api/employee-logs ---> Get
7. http://127.0.0.1:5000/api/send-greetings ----> To send greetings.
8. http://127.0.0.1:5000/api/daily-sent-report ----> Get
