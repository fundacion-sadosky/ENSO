"""
Roles: role-list
"""
from typing import List

from hopeit.app.api import event_api
from hopeit.app.context import EventContext
from hopeit.dataobjects.payload import Payload

from app0.admin.db import Query, SearchResults, db
from app0.admin.app import AppRole
from app0.admin.util import IDX_ROLE

__steps__ = ['run']
__api__ = event_api(
    payload=(Query, "Filters to search"),
    responses={
        200: (SearchResults, "List of results")
    }
)


async def run(payload: Query, context: EventContext) -> SearchResults:
    es = db(context.env)
    results = await get_roles(es, payload)
    return SearchResults(results=[Payload.to_obj(result) for result in results])


async def get_roles(es, query: Query) -> List[AppRole]:
    sort_field = query.sort.field if query.sort else 'name'
    sort_order = query.sort.order if query.sort else 1

    if query.flts:
        cursor = es[IDX_ROLE].find(query.find_qry()).sort(sort_field, sort_order)
    else:
        cursor = es[IDX_ROLE].find().sort(sort_field, sort_order)
    return [Payload.from_obj(doc, AppRole) for doc in await cursor.to_list(length=query.max_items)]
