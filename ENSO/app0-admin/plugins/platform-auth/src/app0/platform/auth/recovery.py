"""
Auth: Recovery
---------------------------------------------
Request for reset user passowrd.
"""
import uuid
from dataclasses import dataclass
from typing import Optional

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_logger
from hopeit.dataobjects import dataobject
from hopeit.dataobjects.payload import Payload
from hopeit.fs_storage import FileStorage

from app0.admin.mail import MAIL_PASSWORD_RESET, VAR_PASSWORD_RESET_URL
from app0.admin.tmail import TmailSend
from app0.admin.user import User
from app0.admin.util import IDX_USER
from app0.platform.auth import AuthReset, db

logger = app_logger()
fs_recover: Optional[FileStorage] = None
APP0_ADMIN_URL: Optional[str] = None


@dataobject
@dataclass
class AuthResetData:
    """
    Info for password reset
    """
    user: User
    recovery_token: str


__steps__ = ['process_recovery', 'notify_recovery']
__api__ = event_api(
    payload=(AuthReset, "Expected data for password reset"),
    responses={
        200: (str, "Reset request succcess."),
    }
)


async def __init_event__(context: EventContext):
    global fs_recover, APP0_ADMIN_URL
    if fs_recover is None:
        fs_recover = FileStorage(path=str(context.env['fs']['recover_store']))
    if APP0_ADMIN_URL is None:
        APP0_ADMIN_URL = str(context.env["env_config"]["app0_admin_url"])


async def process_recovery(payload: AuthReset, context: EventContext) -> Optional[AuthResetData]:
    """
    Process requested user password recovery
    """
    assert fs_recover
    es = db(context.env)
    if payload.user:
        user: Optional[User] = await _get_user_by_username_or_email(es, context, payload.user)
        if user:
            notify: AuthResetData = AuthResetData(user=user, recovery_token=str(uuid.uuid4()))
            payload.id = user.id
            await fs_recover.store(notify.recovery_token, payload)
            logger.info(context, f"User '{notify.user.id}' request password reset")
            return notify
        logger.warning(context, f"Missing user '{payload.user}' request password reset")
        return None
    logger.warning(context, "Empty request for password reset")
    return None


async def notify_recovery(data: AuthResetData, context: EventContext) -> TmailSend:
    """
    Send Recovery Mail
    """
    return TmailSend(
        template=MAIL_PASSWORD_RESET,
        destinations=[data.user.email],
        replacements={
            VAR_PASSWORD_RESET_URL: f'{APP0_ADMIN_URL}/reset/{data.recovery_token}',
        },
        files=[])


async def __postprocess__(payload: Optional[TmailSend], context: EventContext, *, response: PostprocessHook) -> str:
    if payload:
        return "Notification submited to proccess"
    return "Something is wrong"


async def _get_user_by_username_or_email(es, context, username_email: str) -> Optional[User]:
    """find user by username or email"""
    search_query = {'$or': [{'username': {'$eq': username_email}},
                            {'email': {'$eq': username_email}}]}
    count = await es[IDX_USER].count_documents(search_query)
    if count > 1:
        logger.warning(context, f"ERROR: Duplicated user '{username_email}' request password reset")
    doc = await es[IDX_USER].find_one(search_query)
    if not doc:
        return None

    return Payload.from_obj(doc, User)
