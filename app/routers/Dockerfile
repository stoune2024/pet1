FROM redis:7-alpine3.21
COPY dump.rdb .
COPY redis.conf /usr/local/etc/redis/redis.conf
#RUN sudo apk install redis-server
#RUN sudo service redis-server start
CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
