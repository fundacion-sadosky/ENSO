"""
Admin: setup-db
"""
from typing import Optional, Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_logger
from hopeit.dataobjects.payload import Payload

from app0.platform.auth import password_hash
from app0.admin.app import AppDef, AppRole
from app0.admin.db import db
from app0.admin.http import Dto, HttpRespInfo
from app0.admin.util import (IDX_APP, IDX_GROUP, IDX_NOTIFICATION, IDX_ROLE, IDX_USER, IDX_USER_ROLE,
                             ROLE_USER, ROLE_ADMIN, IDX_BASE_MAIL)
from app0.admin.util.tmail_util import save_tmail
from app0.admin.util.user_util import save_user, save_user_role
from app0.admin.tmail import Tmail
from app0.admin.user import User, UserAppRole

logger = app_logger()
DEF_SUPERADMIN_USERNAME = "superuser"
DEF_PASSWORD = "abc123"
DEF_ROLES = [ROLE_USER]
TEMPLATES_FOLDER: Optional[str] = None

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


async def __init_event__(context: EventContext):
    global TEMPLATES_FOLDER
    if TEMPLATES_FOLDER is None:
        TEMPLATES_FOLDER = str(context.env["email_templates"]["templates_folder"])


async def run(payload: None, context: EventContext, code: str) -> Union[Dto, HttpRespInfo]:
    """
    Initialize DB
    """
    # check if empty
    if code == 'FORCE':
        es = db(context.env)
        # check if collections exists and create or clean
        query = {"name": {"$regex": r"^(?!system\.)"}}
        req_colls = [IDX_APP, IDX_GROUP, IDX_NOTIFICATION, IDX_ROLE, IDX_USER,
                     IDX_USER_ROLE, IDX_BASE_MAIL]
        coll_names = await es.list_collection_names(filter=query)
        print(f"coll existentes: {coll_names}")
        for col in req_colls:
            if col in coll_names:
                await es.drop_collection(col)
                print(f"coll {col} dropped")
            await es.create_collection(col)
            print(f"coll {col} created")
        # create base Apps & Roles
        await _create_base_apps_roles(es)

        # create superadmin user
        user = User(firstname="Superuser",
                    surname="Admin",
                    username=DEF_SUPERADMIN_USERNAME,
                    email="superuser@app0.me",
                    password=password_hash(DEF_PASSWORD))
        await save_user(es, user)
        print(f"user saved: {DEF_SUPERADMIN_USERNAME}")

        await _create_user_roles(es, DEF_SUPERADMIN_USERNAME, ROLE_USER)
        await _create_user_roles(es, DEF_SUPERADMIN_USERNAME, ROLE_ADMIN)

        # create email base templates
        await _create_email_templates(es)

    return Dto(o={'msg': 'OK Run'})


async def __postprocess__(payload: Union[Dto, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[Dto, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _create_base_apps_roles(es):
    """
    Create Base Roles & Apps
    """
    # ROLE_USER,ROLE_ADMIN
    role1 = AppRole(name=ROLE_USER, description="App0 User")
    await save_role(es, role1)
    print(f"saved role: {ROLE_USER}")
    role2 = AppRole(name=ROLE_ADMIN, description="App0 Admin")
    await save_role(es, role2)
    print(f"saved role: {ROLE_ADMIN}")

    # create app
    app_app1 = AppDef(
        name="App0 App1",
        description="App0 App1",
        url='http://localhost/app1',
        default_role=ROLE_USER)
    await save_app(es, app_app1)
    print("saved app: app_app1")
    app_app2 = AppDef(
        name="App0 App2",
        description="App0 App2",
        url='http://localhost/app2',
        default_role=ROLE_USER)
    await save_app(es, app_app2)
    print("saved app: app_app2")
    app_app2 = AppDef(
        name="App0 App2",
        description="App0 App2",
        url='http://localhost/app3',
        default_role=ROLE_USER)
    await save_app(es, app_app2)
    print("saved app: app_app2")
    app_app4 = AppDef(
        name="PUE App4",
        description="PUE App4",
        url='http://localhost/app4',
        default_role=ROLE_USER)
    await save_app(es, app_app4)
    print("saved app: app_app4")


async def _create_user_roles(es, username: str, rolename: str):
    """
    Create User Roles
    """
    ur = UserAppRole(username, rolename)
    await save_user_role(es, ur)
    print(f"saved user role: {ur}")


async def _create_email_templates(es):
    """Create Email Templates"""
    emails = [
        Tmail(name="email_confirmation", subject="Verify your email address", template="email-confirmation.html"),
        Tmail(name="welcome", subject="Welcome to App0 Platform", template="welcome.html"),
        Tmail(name="password_reset", subject="Reset your App0 Platform password", template="password-reset.html"),
        Tmail(name="password_reset_ok", subject="App0 Platform password succesfully changed",
              template="password-reset-ok.html"),
    ]
    for d in emails:
        await save_tmail(es, d)
        print(f"saved {d.name}")


async def save_role(es, app_role: AppRole) -> AppRole:
    col = es[IDX_ROLE]
    await col.replace_one({'_id': ObjectId(app_role.id)}, Payload.to_obj(app_role), upsert=True)
    return app_role


async def save_app(es, app_def: AppDef) -> AppDef:
    col = es[IDX_APP]
    await col.replace_one({'_id': ObjectId(app_def.id)}, Payload.to_obj(app_def), upsert=True)
    return app_def
