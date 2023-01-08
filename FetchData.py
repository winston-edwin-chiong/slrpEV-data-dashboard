from dotenv import load_dotenv
import os 
import pandas as pd
import boto3
from boto3.dynamodb.conditions import Key, Attr

class FetchData:

    def __init__(self, table_id):
        self.__scan_results = []
        self.raw_data = None
        self.table_id = table_id
        self.__table = self.__get_table(self.table_id)

    def __configure(self):
        load_dotenv()

    def __get_table(self, table_id):
        self.__configure()
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id = os.getenv("access_key_id"),
            aws_secret_access_key = os.getenv("secret_access_key"),
            region_name="us-east-2",
        )
        return dynamodb.Table(table_id)

    # TODO: Only query for records I don't have. Currently don't know how, so I'm scanning for all records.
    def scan_save_all_records(self):
        done = False
        start_key = None
        params = {}

        while not done:
            if start_key is not None:
                params = {"ExclusiveStartKey": start_key}
                
            response = self.__table.scan(**params)
            self.__scan_results.extend(response.get("Items", []))

            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        self.raw_data = pd.json_normalize(self.__scan_results)
        self.raw_data.to_csv("data/raw_data.csv")