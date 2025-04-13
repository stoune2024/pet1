FROM redis:7-alpine3.21
COPY dump.rdb .
COPY redis.conf /usr/local/etc/redis/redis.conf

CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
