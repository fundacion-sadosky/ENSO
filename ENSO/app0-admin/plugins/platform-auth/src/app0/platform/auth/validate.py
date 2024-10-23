"""
Platform Auth: Validate
"""
from hopeit.app.context import EventContext
from hopeit.app.logger import app_logger

__steps__ = ['validate']

logger = app_logger()


async def validate(payload: None, context: EventContext) -> str:
    assert context.auth_info['allowed']
    return context.auth_info['payload']['access_token']
