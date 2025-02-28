import redis
from ..config import settings
from .fake_no_sql_db import *

# Подключение к redis
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True
)

redis_client.hset('user-session:123', mapping={
    'name': 'John',
    "surname": 'Smith',
    "company": 'Redis',
    "age": 29,
    "list": ['1', 'sdf', 'asd', 'zxcda']
})

data = redis_client.hgetall('user-session:123')



print(data)
