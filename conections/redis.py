import redis
import os
from dotenv import load_dotenv

load_dotenv()

def conection_redis():
    return redis.Redis(
        host=os.getenv('REDIS_HOSTIP'), 
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )

