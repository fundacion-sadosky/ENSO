"""
Apps: app-list
"""
from typing import List

from hopeit.app.api import event_api
from hopeit.app.context import EventContext
from hopeit.dataobjects.payload import Payload

from app0.admin.db import Query, SearchResults, db
from app0.admin.app import AppDef
from app0.admin.util import IDX_APP

__steps__ = ['run']

__api__ = event_api(
    payload=(Query, "Filters to search"),
    responses={
        200: (SearchResults, "List of results")
    }
)


async def run(payload: Query, context: EventContext) -> SearchResults:
    es = db(context.env)
    results = await get_apps(es, payload)
    return SearchResults(results=[Payload.to_obj(result) for result in results])


async def get_apps(es, query: Query) -> List[AppDef]:
    sort_field = query.sort.field if query.sort else 'name'
    sort_order = query.sort.order if query.sort else 1

    if query.flts:
        cursor = es[IDX_APP].find(query.find_qry()).sort(sort_field, sort_order)
    else:
        cursor = es[IDX_APP].find().sort(sort_field, sort_order)
    return [Payload.from_obj(doc, AppDef) for doc in await cursor.to_list(length=query.max_items)]
