# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379
# REDIS_DB = 5  # Using Redis DB 5, optional (default is 0)

# redis_client = aioredis.Redis(
#     host=REDIS_HOST,
#     port=REDIS_PORT,
#     db=REDIS_DB
# )

# STATE_TTL = 3600  # 1 hour
# DATA_TTL = 86400  # 1 day


import redis.asyncio as aioredis
import os

class RedisClientWrapper:
    def __init__(self, client, prefix='AT::'):
        self.client = client
        self.prefix = prefix

    def _prefixed_key(self, key):
        return f"{self.prefix}{key}"

    async def set(self, key, value, *args, **kwargs):
        prefixed_key = self._prefixed_key(key)
        return await self.client.set(prefixed_key, value, *args, **kwargs)

    async def get(self, key, *args, **kwargs):
        prefixed_key = self._prefixed_key(key)
        return await self.client.get(prefixed_key, *args, **kwargs)

    async def delete(self, key, *args, **kwargs):
        prefixed_key = self._prefixed_key(key)
        return await self.client.delete(prefixed_key, *args, **kwargs)


redis_url = os.getenv('REDIS_URL')

original_redis_client = aioredis.from_url(
    redis_url,
    encoding="utf-8",
    decode_responses=True
)

redis_client = RedisClientWrapper(original_redis_client)

STATE_TTL = 3600  # 1 hour
DATA_TTL = 86400  # 1 day
