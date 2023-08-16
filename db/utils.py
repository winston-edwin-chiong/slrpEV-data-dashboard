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
    

    @classmethod
    def send_chunks(cls, redis_client: redis.Redis, df: pd.DataFrame, name: str):
        chunks = np.array_split(df, cls.chunk_size)

        for i, chunk in enumerate(chunks):
            serialized_chunk = pickle.dumps(chunk)  
            redis_client.set(f"{name}_{i}", serialized_chunk)


    @classmethod
    def get_chunks(cls, redis_client: redis.Redis, name):
        deserialized_chunks = []
        for i in range(cls.chunk_size):
            serialized_chunk = redis_client.get(f"{name}_{i}")
            chunk = pickle.loads(serialized_chunk)
            deserialized_chunks.append(chunk)

        result = pd.concat(deserialized_chunks)
        return result
    
    