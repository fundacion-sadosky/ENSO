"""
Product: product-list
"""
from typing import List

from hopeit.app.api import event_api
from hopeit.app.context import EventContext
from hopeit.dataobjects.payload import Payload

from app0.admin.db import Query, SearchResults, db
from app0.app5.product import Product
from app0.app5.util import IDX_PRODUCT

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


async def get_objects(mo, query: Query) -> List[Product]:
    sort_field = query.sort.field if query.sort else 'barcode'
    sort_order = query.sort.order if query.sort else 1

    if query.flts:
        cursor = mo[IDX_PRODUCT].find(query.find_qry()).sort(sort_field, sort_order)
    else:
        cursor = mo[IDX_PRODUCT].find().sort(sort_field, sort_order)
    return [Payload.from_obj(doc, Product) for doc in await cursor.to_list(length=query.max_items)]
