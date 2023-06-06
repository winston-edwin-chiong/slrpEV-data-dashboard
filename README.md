# slrpEV-data-dashboard
Data dashboard for slrpEV.

Start the Celery worker and Celery beat using `celery -A tasks.schedule worker --loglevel=INFO -P eventlet` and `celery -A tasks.schedule beat --loglevel=INFO`. 

App is configured to run on Redis local host on port 6360. 

