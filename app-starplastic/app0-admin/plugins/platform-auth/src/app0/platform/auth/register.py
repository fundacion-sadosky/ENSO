"""
Auth: Register password
"""
import base64

from hopeit.app.api import event_api
from hopeit.app.context import EventContext
from hopeit.app.errors import Unauthorized
from hopeit.app.logger import app_logger

from app0.admin.util import IDX_USER

from app0.platform.auth import AuthInfo, password_hash, db

logger = app_logger()

__steps__ = ['register_password']
__api__ = event_api(
    responses={
        200: (AuthInfo, "Authentication information to be used for further API calls"),
        401: (Unauthorized.ErrorInfo, "Login failed, invalid credentials")
    }
)


async def register_password(payload: None, context: EventContext) -> str:
    """
    Register encoded new user password
    """
    assert context.auth_info['allowed']
    username, password = base64.b64decode(context.auth_info['payload'].encode()).decode().split(":")
    es = db(context.env)
    if await _register_user_password(es, username, password):
        return "OK"

    raise Unauthorized('Invalid password set')


async def _register_user_password(es, username: str, new_password: str) -> bool:
    col = es[IDX_USER]
    await col.update_one({'username': username},
                         {'$set': {'password': password_hash(new_password)}})
    return True
