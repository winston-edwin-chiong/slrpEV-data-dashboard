from dotenv import load_dotenv
import os 
import pandas as pd
import boto3
from boto3.dynamodb.conditions import Key, Attr


class FetchData:
    table_id = "Sessions2"
    __scan_results = []

    def __init__(self):
        pass

    @staticmethod
    def __configure():
        load_dotenv()

    @classmethod
    def __get_table(cls, table_id):
        cls.__configure()
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=os.getenv("access_key_id"),
            aws_secret_access_key=os.getenv("secret_access_key"),
            region_name="us-east-2",
        )
        return dynamodb.Table(table_id)

    # TODO: Only query for records I don't have. Currently don't know how, so I'm scanning for all records.
    @classmethod
    def scan_save_all_records(cls):
        table = cls.__get_table(cls.table_id)

        done = False
        start_key = None
        params = {}

        while not done:
            if start_key is not None:
                params = {"ExclusiveStartKey": start_key}
                
            response = table.scan(**params)
            cls.__scan_results.extend(response.get("Items", []))

            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        raw_data = pd.json_normalize(cls.__scan_results)
        raw_data.to_csv("data/raw_data.csv")
