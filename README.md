# slrpEV-data-dashboard
Data dashboard for slrpEV.

App is live @ https://slrpev-data-dashboard.onrender.com !

Backend database (data from the physical chargers) is hosted on [AWS DynamoDB](https://aws.amazon.com/dynamodb/).

Data cleaning and machine learning is executed on a schedule hosted by [Modal](https://modal.com) and results sent to [Redis](https://redis.com/).

App's frontend architecture is built with [Plotly Dash](https://dash.plotly.com/). 
