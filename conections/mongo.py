#Database Publications
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def conection_mongo():
    client = MongoClient(
        f"mongodb://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOSTIP')}:{os.getenv('MONGO_PORT')}/?authSource=admin"
    )
    return client[f"{os.getenv('MONGO_DB')}"]
