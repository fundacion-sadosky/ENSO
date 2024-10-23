"""
Machine: machine-list
"""
from typing import List

from hopeit.app.api import event_api
from hopeit.app.context import EventContext
from hopeit.dataobjects.payload import Payload

from app0.admin.db import Query, SearchResults, db
from app0.app5.machine import Machine
from app0.app5.util import IDX_MACHINE

__steps__ = ['run']
__api__ = event_api(
    payload=(Query, "Filters to search"),
    responses={
        200: (SearchResults, "List of results")
    }
)


async def run(payload: Query, context: EventContext) -> SearchResults:
    mo = db(context.env)
    results = await get_objects(mo, payload)
    return SearchResults(results=[Payload.to_obj(result) for result in results])


async def get_objects(mo, query: Query) -> List[Machine]:
    sort_field = query.sort.field if query.sort else 'nbr'
    sort_order = query.sort.order if query.sort else 1

    if query.flts:
        cursor = mo[IDX_MACHINE].find(query.find_qry()).sort(sort_field, sort_order)
    else:
        cursor = mo[IDX_MACHINE].find().sort(sort_field, sort_order)
    return [Payload.from_obj(doc, Machine) for doc in await cursor.to_list(length=query.max_items)]
