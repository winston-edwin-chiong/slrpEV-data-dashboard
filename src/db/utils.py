import redis 
import os
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
        connection_pool = redis.ConnectionPool.from_url(url=os.getenv("REDIS_URI"))
        retry = Retry(ExponentialBackoff(), 3)
        return redis.Redis(connection_pool=connection_pool, retry=retry, retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])
    

    @staticmethod
    def get_item(redis_client: redis.Redis, key: str):
        '''
        Unpickles and returns item from Redis.
        '''
        return pickle.loads(redis_client.get(key))
    

    @staticmethod
    def send_item(redis_client: redis.Redis, key: str, item) -> None:
        '''
        Pickles and sends item to Redis.
        '''
        redis_client.set(key, pickle.dumps(item))

    
    @classmethod
    def get_df(cls, redis_client: redis.Redis, name) -> pd.DataFrame:
        """
        All dataframes except should be retrieved with this method. 
        """
        buffer = redis_client.get(name)
        result = pd.read_parquet(BytesIO(buffer))
        return result
    
    
    @classmethod
    def send_df(cls, redis_client: redis.Redis, df: pd.DataFrame, name: str) -> None:
        """
        All dataframes should be sent with this method.  
        """
        pq = df.to_parquet()
        redis_client.set(name, pq)


    @classmethod
    def get_multiple_df(cls, redis_client: redis.Redis, names: list) -> list[pd.DataFrame]:
        """
        For retrieving multiple dataframes in a block. Returns as a list in the same order as input.
        """
        pipe = redis_client.pipeline()

        for name in names:
            pipe.get(name)

        res = pipe.execute()
        res = [pd.read_parquet(BytesIO(buffer)) for buffer in res] 
        return res
    