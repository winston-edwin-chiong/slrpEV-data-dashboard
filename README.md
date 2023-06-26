# slrpEV-data-dashboard
Data dashboard for slrpEV.

Activate the Python virtual environment with `.\venv\Scripts\activate`.

Start the Celery worker with `celery -A tasks.schedule worker --loglevel=INFO -P eventlet`.

Start Celery beat with `celery -A tasks.schedule beat --loglevel=INFO`. 

Start the Redis server with `redis-server --port 6360`. 
