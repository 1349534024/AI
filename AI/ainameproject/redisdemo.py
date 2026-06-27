import redis

REDIS_URL = "redis://127.0.0.1:6379/0"

redis_client = redis.from_url(REDIS_URL,decode_responses=True)

redis_client.set(name="username", value="admin")
redis_client.set(name="password", value="123456")