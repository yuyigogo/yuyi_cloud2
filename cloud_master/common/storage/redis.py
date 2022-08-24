from cloud.settings import REDIS_HOST, REDIS_PORT
from redis import ConnectionPool, Redis

# store normal values

redis = Redis(
    connection_pool=ConnectionPool(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=5,
        decode_responses=True,
        socket_timeout=3,
        retry_on_timeout=True,
        health_check_interval=30,
    )
)

# store only for websocket
ws_redis = Redis(
    connection_pool=ConnectionPool(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=1,
        decode_responses=True,
        socket_timeout=3,
        retry_on_timeout=True,
        health_check_interval=30,
    )
)
