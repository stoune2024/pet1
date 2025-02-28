import redis

# Подключение к redis
r = redis.Redis(
    host='localhost',
    port=6379
)

# Проверка подключения
try:
    response = r.ping()
    if response:
        print('Подключение к Redis успешно)')
    else:
        print('Не удалось подключиться к Redis(')
except Exception as e:
    print(f'произошла ошибка {e}')