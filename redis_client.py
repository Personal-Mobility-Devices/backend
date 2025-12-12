import redis
from redis import Redis
import os

#redis_client = redis.from_url(os.getenv("REDIS_URL")) #ЕСЛИ БУДЕТ, СЮДА НУЖНА ССЫЛКА ИЗ Render!

redis_client = Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

try:
    redis_client.ping()
    print("Redis подключен")
except Exception as e:
    print("Ошибка подключения:", e)

redis_client = redis_client