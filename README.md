# slrpEV-data-dashboard
A data dashboard for [slrpEV](https://sites.google.com/berkeley.edu/slrpev), the on-campus EV chargers at UC Berkeley.

> [!NOTE]
> __Unfortunately, effective mid-2024, slrpEV is no longer receiving real-time charger data so this dashboard was taken down. ☹️__

## Description
The app provides analysis at the five-minute, hourly, daily, and monthly granularities, as well as providing day-ahead and week-ahead forecasts. The app also provides historical data visualization at the the five-minute, hourly, daily, and monthly granularities, various demand analytics, user analysis, and real-time charger usage, and the ability to access the underlying dataset.

## Getting Started 

### Dependencies
- Create a Python virtual environment with `python -m venv ./venv`.
- Install the dependencies with `pip install -r requirements.txt`.
- Activate the Python virtual environment with `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (MacOS).
- A `.env` file should hold the Redis URI. 

### Running the App
- Start the Dash app with `.\venv\Scripts\python.exe src/dashboard.py`.

### Updating Modal Tasks
- Updates to the scheduled tasks (`tasks/schedule.py` file in the `src` directory) should be automatically pushed to Modal on pushes to the main branch via Github Actions, but manual deployments can be triggered with `modal deploy src/tasks/schedule.py` (ran from the root directory). 


## Built With
- Data from the physical chargers is located on [AWS DynamoDB](https://aws.amazon.com/dynamodb/).
- Data cleaning and machine learning tasks are executed on a schedule hosted on [Modal](https://modal.com) and results sent to [Redis](https://redis.io/), the app's main database.
- App's frontend is built with [Plotly Dash](https://dash.plotly.com/) and [Bootstrap](https://getbootstrap.com/). 
