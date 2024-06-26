# slrpEV-data-dashboard
Data dashboard for slrpEV.

App is live @ https://slrpev-data-dashboard.onrender.com !

Data from the physical chargers is located on [AWS DynamoDB](https://aws.amazon.com/dynamodb/).

Data cleaning and machine learning is executed on a schedule hosted by [Modal](https://modal.com) and results sent to [Redis](https://redis.io/).

App's frontend architecture is built with [Plotly Dash](https://dash.plotly.com/). 

### Local Development
Create a Python virtual environment with `python -m venv ./venv`.

Install the dependencies with `pip install -r requirements.txt`.

Activate the Python virtual environment with `.\venv\Scripts\activate` or `source venv/bin/activate`, depending on operating system.

Start the Dash app with `.\venv\Scripts\python.exe src/dashboard.py`.

Updates to the scheduled tasks (`tasks/schedule.py` file in the root directory) should be automatically pushed to Modal on pushes to the main branch, but manual deployments can be triggered with `cd src && modal deploy tasks/schedule.py`. 

The FastAPI can be run with `uvicorn api.api:app --host 0.0.0.0`.
