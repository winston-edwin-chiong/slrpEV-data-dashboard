# slrpEV-data-dashboard
Data dashboard for slrpEV.

## Local Development Setup

Create a Python virtual environment with `python -m venv ./venv`.

Install the dependencies with `pip install -r requirements.txt`.

Activate the Python virtual environment with `.\venv\Scripts\activate`.

Start the Redis server with `redis-server --port 6360`. 

Start the Celery worker with `celery -A tasks.schedule worker --loglevel=INFO -P eventlet`.

Start Celery beat with `celery -A tasks.schedule beat --loglevel=INFO`. 

Start the app with `<PATH TO VENV>/venv/Scripts/python.exe <PATH TO PROJECT DIR>/slrpEV-data-dashboard/app.py`

