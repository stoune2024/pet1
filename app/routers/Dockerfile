FROM redis:7.4.3-alpine3.21
COPY PATH/TO/dump.rdb .
COPY PATH/TO/redis.conf /usr/local/etc/redis/redis.conf
CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]