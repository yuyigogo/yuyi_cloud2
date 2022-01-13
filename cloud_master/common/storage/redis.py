from django.conf import settings
from redis import ConnectionPool, Redis

redis = Redis(
    connection_pool=ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=5,
        decode_responses=True,
        socket_timeout=3,
        retry_on_timeout=True,
        health_check_interval=30,
    )
)
