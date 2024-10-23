"""
Auth: Reset
"""
from datetime import datetime, timezone
from typing import Optional, Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_logger
from hopeit.dataobjects.payload import Payload
from hopeit.fs_storage import FileStorage

from app0.admin.mail import MAIL_PASSWORD_RESET_OK, MAIL_WELCOME, VAR_ADMIN_APP_URL, VAR_USER_NAME
from app0.admin.http import HttpRespInfo
from app0.admin.tmail import TmailSend
from app0.admin.user import User
from app0.admin.util import IDX_USER
from app0.platform.auth import AuthNew, AuthReset, db, password_hash

logger = app_logger()
fs_recover: Optional[FileStorage] = None
APP0_ADMIN_URL: Optional[str] = None

__steps__ = ['reset', 'notify_reset']
__api__ = event_api(
    payload=(AuthNew, "Expected data for password reset"),
    responses={
        200: (str, "Reset precedure succcess."),
        403: (str, "Operation forbidden"),
    }
)


async def __init_event__(context: EventContext):
    global fs_recover, APP0_ADMIN_URL
    if fs_recover is None:
        fs_recover = FileStorage(path=str(context.env['fs']['recover_store']))
    if APP0_ADMIN_URL is None:
        APP0_ADMIN_URL = str(context.env["env_config"]["app0_admin_url"])


async def reset(auth_info: AuthNew, context: EventContext) -> Union[HttpRespInfo, AuthReset]:
    """
    Reset user password if token is valid
    """
    assert fs_recover
    auth_reset: Optional[AuthReset] = await fs_recover.get(key=auth_info.auth_token, datatype=AuthReset)
    if auth_reset:
        assert auth_reset.id and auth_reset.expire
        if auth_reset.expire > datetime.now(tz=timezone.utc):
            auth_reset.expire = datetime.now(tz=timezone.utc)
            await fs_recover.store(key=auth_info.auth_token, value=auth_reset)
            # update new password
            es = db(context.env)
            await _update_user_password(es, auth_reset.id, password_hash(auth_info.password))
            logger.info(context, f"User '{auth_reset.id}' has reset his password")
            return auth_reset
        logger.warning(context, f"User '{auth_reset.id}' expire")
        return HttpRespInfo(403, 'Operation forbidden')
    logger.warning(context, f"Reset password token '{auth_info.auth_token}' missing")
    return HttpRespInfo(403, 'Operation forbidden')


async def notify_reset(auth_reset: AuthReset, context: EventContext) -> Optional[TmailSend]:
    """
    Send Recovery Mail
    """
    assert auth_reset.id
    es = db(context.env)
    user: Optional[User] = await _get_user(es, auth_reset.id)
    if user:
        # if first access, send welcome mail
        return TmailSend(
            template=MAIL_WELCOME if auth_reset.first_access else MAIL_PASSWORD_RESET_OK,
            destinations=[user.email],
            replacements={
                VAR_USER_NAME: user.firstname + ' ' + user.surname,
                VAR_ADMIN_APP_URL: f'{APP0_ADMIN_URL}',
            },
            files=[])
    return None


async def __postprocess__(payload: Optional[Union[HttpRespInfo, TmailSend]], context: EventContext,
                          *, response: PostprocessHook) -> str:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return "Something is wrong"


async def _get_user(es, oid: str) -> Optional[User]:
    doc = await es[IDX_USER].find_one(ObjectId(oid))
    return Payload.from_obj(doc, User)


async def _update_user_password(es, user_id: str, new_password: str):
    col = es[IDX_USER]
    await col.update_one({'_id': ObjectId(user_id)},
                         {'$set': {'password': new_password}})
