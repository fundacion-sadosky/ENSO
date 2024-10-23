from bson.objectid import ObjectId  # type: ignore
from hopeit.dataobjects.payload import Payload

from app0.admin.common import Counter
from app0.admin.util import IDX_COUNTER


async def next_value(mo, key: str) -> int:
    """Returns next value of key"""
    doc = await mo[IDX_COUNTER].find_one({'key': key})
    if doc:
        # get next value
        counter = Payload.from_obj(doc, Counter)
        next = counter.value+1
        counter.value = next
    else:
        next = 1
        counter = Counter(key=key, value=next)
    await mo[IDX_COUNTER].replace_one({'_id': ObjectId(counter.id)},
                                      Payload.to_obj(counter), upsert=True)
    return next
