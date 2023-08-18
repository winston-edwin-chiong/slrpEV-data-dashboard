import os
import pandas as pd
import boto3
from boto3.dynamodb.conditions import Key, Attr
from dotenv import load_dotenv


class FetchData:
    table_id = "Sessions2"

    def __init__(self):
        pass

    @staticmethod
    def __configure():
        load_dotenv()

    # TODO: Could be in __init__; does the table ever change? Don't need to call this every time?
    @classmethod
    def __get_table(cls, table_id):
        cls.__configure()  # load environment variables
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
            region_name="us-east-2",
        )
        return dynamodb.Table(table_id)


    @classmethod
    def scan_all_records(cls):
        scan_results = []
        table = cls.__get_table(cls.table_id)

        done = False
        start_key = None
        params = {}

        while not done:
            if start_key is not None:
                params = {"ExclusiveStartKey": start_key}

            response = table.scan(**params)
            scan_results.extend(response.get("Items", []))

            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        raw_data = pd.json_normalize(scan_results)
        
        return raw_data
