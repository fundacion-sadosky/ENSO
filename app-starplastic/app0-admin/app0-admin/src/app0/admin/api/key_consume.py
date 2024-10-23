"""
Admin: key-consume
"""
from typing import Optional

from hopeit.app.api import event_api
from hopeit.app.context import EventContext

from app0.admin.db.keystore import get_iddesc_key
from app0.admin.common import IdDescription

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('key', str, "Key")
    ],
    responses={
        200: (IdDescription, "Value"),
    }
)


async def run(payload: None, context: EventContext, key: str) -> Optional[IdDescription]:
    if key:
        kval = await get_iddesc_key(key, consume=True)
        return kval if kval else IdDescription('none', 'none')
    return IdDescription('none', 'none')
