# slrpEV-data-dashboard
Data dashboard for slrpEV.

App is live @ https://slrpev-data-dashboard.onrender.com !

Backend database (data from the physical chargers) is hosted on [AWS DynamoDB](https://aws.amazon.com/dynamodb/).

Data cleaning and machine learning is executed on a schedule hosted by [Modal](https://modal.com) and results sent to [Redis](https://redis.io/).

App's frontend architecture is built with [Plotly Dash](https://dash.plotly.com/). 

### Local Development
Create a Python virtual environment with `python -m venv ./venv`.

Install the dependencies with `pip install -r requirements.txt`.

Activate the Python virtual environment with `.\venv\Scripts\activate`.

Start the Dash app with `.\venv\Scripts\python.exe src/my_app.py`.

Updates to the scheduled tasks (`tasks/schedule.py` file in the root directory) should be pushed to Modal with `cd src && modal deploy --name slrpEV-data-dashboard-tasks tasks/schedule.py`.


