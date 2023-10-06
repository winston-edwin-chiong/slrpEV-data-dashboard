import redis 
import os
import numpy as np
import pickle
import pandas as pd
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError
from io import BytesIO


class db:

    @staticmethod
    def get_redis_connection() -> redis.Redis:
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
    

    @staticmethod
    def send_item(redis_client: redis.Redis, key: str, item):
        '''
        Pickles and sends item to Redis.
        '''
        redis_client.set(key, pickle.dumps(item))

    
    @classmethod
    def get_df(cls, redis_client: redis.Redis, name):
        """
        All dataframes except should be retrieved with this method. 
        """
        buffer = redis_client.get(name)
        result = pd.read_parquet(BytesIO(buffer))
        return result
    
    
    @classmethod
    def send_df(cls, redis_client: redis.Redis, df: pd.DataFrame, name: str) -> None:
        """
        All dataframes except should be sent with this method.  
        """
        pq = df.to_parquet()
        redis_client.set(name, pq)


    @classmethod
    def get_multiple_df(cls, redis_client: redis.Redis, names: list) -> list:
        """
        For retrieving multiple dataframes in a block. Returns as a list in the same order as input.
        """
        pipe = redis_client.pipeline()

        for name in names:
            pipe.get(name)

        res = pipe.execute()
        res = [pd.read_parquet(BytesIO(buffer)) for buffer in res] 
        return res
    