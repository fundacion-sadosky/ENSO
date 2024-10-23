"""
Key store Module
"""
from typing import Optional
import os

from hopeit.redis_storage import RedisStorage

from app0.admin.common import IdDescription


def redis_conn() -> Optional[RedisStorage]:
    redis_url = os.getenv('REDIS_URL')
    assert redis_url is not None, "Cannot get value from OS environment var: REDIS_URL"
    return RedisStorage().connect(address=redis_url)


async def set_iddesc_key(key: str, value: IdDescription):
    """Set value in redis."""
    redis = redis_conn()
    assert redis
    # expire key 3600 seconds = 60 minutes
    print(f"==> REDIS saving key {key} with value {value}")
    await redis.store(key, value, ex=3600)


async def get_iddesc_key(key: str, consume: bool = False) -> Optional[IdDescription]:
    """Get value in redis."""
    redis = redis_conn()
    assert redis
    print(f"==> REDIS getting key {key}")
    payload = await redis.get(key=key, datatype=IdDescription)
    print(f"==> REDIS getted key {key} value {payload}")
    if not payload:
        return None
    if consume:
        await redis.delete(key)
        print(f"==> REDIS key {key} deleted")
    return payload
