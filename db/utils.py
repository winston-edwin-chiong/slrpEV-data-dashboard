import redis 
import os
import numpy as np
import pickle
import pandas as pd
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError
from dotenv import load_dotenv

load_dotenv()

class db:

    chunk_size = 30

    @staticmethod
    def get_redis_connection():
        '''
        This function returns a Redis connection object. 
        '''
        retry = Retry(ExponentialBackoff(), 3)

        return redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            password=os.getenv("REDIS_PASSWORD"),
            retry=retry,
            retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError]
        )
    

    @staticmethod
    def get_item(redis_client: redis.Redis, key: str):
        '''
        Unpickles and returns item from Redis.
        '''
        return pickle.loads(redis_client.get(key))
    

    @classmethod
    def update_data(cls, redis_client: redis.Redis):
        '''
        Updates data and forecasts from Redis to the file system.
        '''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_folder = os.path.abspath(os.path.join(current_dir, '..', '..', 'data'))

        # update data 
        for name in ["raw_data", "todays_sessions", "fivemindemand", "hourlydemand", "dailydemand", "monthlydemand"]:
            data = cls.get_chunks(redis_client, name)
            csv_path = os.path.join(data_folder, f'{name}.csv')
            data.to_csv(csv_path)

        # update forecasts
        for name in ["hourlyforecasts", "dailyforecasts"]:
            forecasts = cls.get_item(redis_client, name)
            csv_path = os.path.join(data_folder, f'{name}.csv')
            forecasts.to_csv(csv_path)


    @classmethod
    def send_chunks(cls, redis_client: redis.Redis, df: pd.DataFrame, name: str):
        chunks = np.array_split(df, cls.chunk_size)

        for i, chunk in enumerate(chunks):
            serialized_chunk = pickle.dumps(chunk)  
            redis_client.set(f"{name}_{i}", serialized_chunk)


    @classmethod
    def get_chunks(cls, redis_client: redis.Redis, name):
        '''
        All dataframes except forecasts should be retrieved with this method. 
        '''
        deserialized_chunks = []
        for i in range(cls.chunk_size):
            serialized_chunk = redis_client.get(f"{name}_{i}")
            chunk = pickle.loads(serialized_chunk)
            deserialized_chunks.append(chunk)

        result = pd.concat(deserialized_chunks)
        return result
    

    @staticmethod
    def load_from_data_folder(name, time_series=False):
        '''
        Loads data from the data folder.
        '''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_folder = os.path.abspath(os.path.join(current_dir, '..', '..', 'data'))
        csv_path = os.path.join(data_folder, f'{name}.csv')
        if time_series:
            return pd.read_csv(csv_path, index_col="time", parse_dates=True)
        return pd.read_csv(csv_path)
    
    