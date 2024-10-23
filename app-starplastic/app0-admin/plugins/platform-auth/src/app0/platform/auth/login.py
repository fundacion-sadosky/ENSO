"""
Auth: Login
--------------------------------------------------------------------
Handles users login using basic-auth
and generate access tokens for external services invoking apps
plugged in with basic-auth plugin.
"""
import base64
from datetime import datetime, timezone
from typing import Optional, List

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.errors import Unauthorized
from hopeit.app.logger import app_logger
from hopeit.toolkit.auth import AuthType
from hopeit.dataobjects.payload import Payload

from app0.admin.user import User, UserAppRole
from app0.admin.util import IDX_USER, IDX_USER_ROLE
from app0.platform.auth import (AuthInfo, AuthInfoExtended, ContextUserInfo, UserPassword, authorize_password,
                                authorize, db, set_refresh_token)

logger = app_logger()

__steps__ = ['login']
__api__ = event_api(
    responses={
        200: (AuthInfo, "Authentication information to be used for further API calls"),
        401: (Unauthorized.ErrorInfo, "Login failed, invalid credentials")
    }
)


async def login(payload: None, context: EventContext) -> AuthInfoExtended:
    """
    Returns a new access and refresh token for a set of given basic-auth credentials
    """
    assert context.auth_info['allowed']
    now = datetime.now().astimezone(timezone.utc)
    username, password = base64.b64decode(context.auth_info['payload'].encode()).decode().split(":")
    if context.auth_info['auth_type'] == AuthType.BASIC:
        # authenticate against mongodb
        es = db(context.env)
        user: Optional[User] = await _get_user_by_username(es, username)
        if user:
            if await _authorized(password, user.password):
                roles = await _get_user_roles_by_username(es=es, username=username)
                user_info = ContextUserInfo(
                    id=str(user.id),
                    user=user.username,
                    fullname=f"{user.firstname} {user.surname}",
                    email=str(user.email),
                    image=user.image if user.image else '',
                    roles=[r.role for r in roles],
                    groups=[]
                )
                return authorize(context, user_info, now)

    raise Unauthorized('Invalid authorization, status not catched')


async def __postprocess__(payload: AuthInfoExtended,
                          context: EventContext, *,
                          response: PostprocessHook) -> AuthInfo:
    set_refresh_token(context.app, context.auth_info, payload, response)
    return payload.to_auth_info()


async def _authorized(password: str, hashed_password: str) -> bool:
    if password and hashed_password:
        return authorize_password(password, UserPassword(hash=hashed_password))
    return False


async def _get_user_by_username(es, username: str) -> Optional[User]:
    doc = await es[IDX_USER].find_one({'username': {'$eq': username}})
    if not doc:
        return None

    return Payload.from_obj(doc, User)


async def _get_user_roles_by_username(es, username) -> List[UserAppRole]:
    cursor = es[IDX_USER_ROLE].find({'username': {'$eq': username}})
    return [Payload.from_obj(doc, UserAppRole) for doc in await cursor.to_list(length=100)]
