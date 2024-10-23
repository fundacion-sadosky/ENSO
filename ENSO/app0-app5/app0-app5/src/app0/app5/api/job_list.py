"""
Job: job-list
"""
from typing import Optional

from hopeit.app.api import event_api
from hopeit.app.context import EventContext
from hopeit.dataobjects.payload import Payload

from app0.admin.db import Query, SearchResults, db

from app0.app5.model import ModelJob
from app0.app5.util import IDX_JOB

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('offset', Optional[int], "Page offset / start"),
        ('page_size', Optional[int], "Page size")
    ],
    payload=(Query, "Filters to search"),
    responses={
        200: (SearchResults, "List of results")
    }
)


async def run(payload: Query, context: EventContext, offset: int = 0, page_size: int = 20) -> SearchResults:
    es = db(context.env)
    offset, page_size = int(offset), int(page_size)
    return await _get_jobs(es, payload, offset, page_size)


async def _get_jobs(es, query: Query, offset: int = 0, page_size: int = 20) -> SearchResults:
    """find jobs"""
    assert query
    count: int
    sort_field = query.sort.field if query.sort else 'creation_date'
    sort_order = query.sort.order if query.sort else -1

    if query.flts:
        search_query = query.find_qry()
        cursor = es[IDX_JOB].find(search_query)
        count = await es[IDX_JOB].count_documents(search_query)
    else:
        cursor = es[IDX_JOB].find()
        count = await es[IDX_JOB].estimated_document_count()

    cursor = cursor.sort(sort_field, sort_order)
    results = [Payload.from_obj(doc, ModelJob) for doc in await cursor.skip(offset).to_list(length=page_size)]

    return SearchResults(total=count, page_size=page_size, offset=offset,
                         results=[Payload.to_obj(result) for result in results])
