import redis
from redis import Redis
import os

redis_client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

try:
    redis_client.ping()
    print("Redis подключен")
except Exception as e:
    print("Ошибка подключения:", e)

redis_client = redis_client