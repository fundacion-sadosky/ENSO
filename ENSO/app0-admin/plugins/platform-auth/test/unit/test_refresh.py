import pytest  # type: ignore
from datetime import datetime, timedelta

import hopeit.toolkit.auth as auth
from app0.platform.auth import ContextUserInfo, AuthInfoExtended, AuthInfo  # type: ignore
from hopeit.app.context import EventContext, PostprocessHook

from app0.platform.auth import refresh  # type: ignore
from hopeit.app.errors import Unauthorized
from hopeit.server.config import AuthType
from . import mock_app_config, plugin_config  # noqa: F401


async def invoke_refresh(context: EventContext):
    auth_info = await refresh.refresh(None, context)

    assert auth_info.token_type == 'BEARER'

    access_token_info = auth.decode_token(auth_info.access_token)
    assert access_token_info['app'] == 'test_app.test'
    assert access_token_info['id'] == 'id'
    assert access_token_info['email'] == 'test@email'
    assert access_token_info['user'] == 'test'
    iat = access_token_info['iat']
    assert access_token_info['exp'] == iat + context.env['auth']['access_token_expiration']
    assert access_token_info['renew'] > 0
    assert access_token_info['renew'] < 1000.0 * (
        int(context.env['auth']['access_token_expiration']) - int(context.env['auth']['access_token_renew_window']))

    refresh_token_info = auth.decode_token(auth_info.refresh_token)
    assert refresh_token_info['app'] == 'test_app.test'
    assert refresh_token_info['id'] == 'id'
    assert refresh_token_info['email'] == 'test@email'
    assert refresh_token_info['user'] == 'test'
    iat = refresh_token_info['iat']
    assert refresh_token_info['exp'] == iat + context.env['auth']['refresh_token_expiration']

    assert auth_info.user_info == ContextUserInfo(id='id', user='test', fullname="", email='test@email', roles=[],
                                                  groups=[], image="")
    assert auth_info.access_token_expiration == context.env['auth']['access_token_expiration']
    assert auth_info.refresh_token_expiration == context.env['auth']['refresh_token_expiration']
    assert auth_info.renew == access_token_info['renew']
    return auth_info


async def invoke_postprocess(payload: AuthInfoExtended, context: EventContext):
    hook = PostprocessHook()
    result = await refresh.__postprocess__(payload, context, response=hook)
    print(hook.cookies)
    assert hook.cookies['test_app.test.refresh'] == (
        f"Refresh {payload.refresh_token}",
        tuple(),
        {'domain': None,
         'expires': 3600,
         'httponly': 'true',
         'max_age': 3600,
         'samesite': 'Lax',
         'path': '/'
         }
    )
    assert result == AuthInfo(
        access_token=payload.access_token,
        token_type=payload.token_type,
        renew=payload.renew
    )


async def execute_flow(context):
    auth_info = await invoke_refresh(context)
    await invoke_postprocess(auth_info, context)


def _event_context(mock_app_config, plugin_config):  # noqa: F811
    iat = datetime.now()
    timeout = plugin_config.env['auth']['access_token_expiration']
    return EventContext(
        app_config=mock_app_config,
        plugin_config=plugin_config,
        event_name='login',
        track_ids={},
        auth_info={
            'allowed': True,
            'auth_type': AuthType.REFRESH,
            'payload': {'id': 'id', 'user': 'test', 'email': 'test@email', 'iat': iat,
                        'roles': [], 'groups': [], 'fullname': '', 'exp': iat + timedelta(seconds=timeout)}
        }
    )


@pytest.mark.asyncio
async def test_refresh(mock_app_config, plugin_config):  # noqa: F811
    auth.init(mock_app_config.app_key(), mock_app_config.server.auth)
    context = _event_context(mock_app_config, plugin_config)
    await execute_flow(context)


@pytest.mark.asyncio
async def test_refresh_unauthorized(mock_app_config, plugin_config):  # noqa: F811
    auth.init(mock_app_config.app_key(), mock_app_config.server.auth)
    context = _event_context(mock_app_config, plugin_config)
    context.auth_info['auth_type'] = "UNKNOWN"
    with pytest.raises(Unauthorized):
        await execute_flow(context)
