"""
Admin: setup-adhoc
"""
from typing import Union

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_logger

from app0.platform.auth import password_hash
from app0.admin.db import db
from app0.admin.http import Dto, HttpRespInfo
from app0.admin.util.user_util import get_user_by_username, save_user

logger = app_logger()
DEF_SUPER = "superuser"
DEF_ADM_SP = "admin.sp@app0.me"
DEF_OP_SP = "operario.sp@app0.me"
DEF_USERS = [DEF_SUPER, DEF_ADM_SP, DEF_OP_SP]
DEF_PASSWORD1 = "abc123"
DEF_PASSWORD2 = "cde123"
DEF_PASSWORD1S = "pueingar3657"
DEF_PASSWORD2S = "starpla2023DASH."

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('code', str, "Setup Code")
    ],
    responses={
        200: (Dto, "OK"),
        400: (str, "Bad request"),
        403: (str, "Operation forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: None, context: EventContext, code: str) -> Union[Dto, HttpRespInfo]:
    """
    Initialize DB
    """
    # check if empty
    if code == 'PASSFIX':
        es = db(context.env)
        for username in DEF_USERS:
            # create superadmin user
            user = await get_user_by_username(es, username)
            assert user
            if user.username == DEF_SUPER:
                user.password = password_hash(DEF_PASSWORD1S)
            else:
                user.password = password_hash(DEF_PASSWORD2S)

            await save_user(es, user)
            print(f"user updated: {username}")

    return Dto(o={'msg': 'OK Run'})


async def __postprocess__(payload: Union[Dto, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[Dto, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload
