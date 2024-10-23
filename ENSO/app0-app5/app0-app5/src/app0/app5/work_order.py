"""
Model: Work Order
"""
from datetime import datetime
from typing import List, Optional

from bson.objectid import ObjectId  # type: ignore
from hopeit.dataobjects import dataclass, dataobject

from app0.admin import fd
from app0.admin.common import IdDescription


@dataobject
@dataclass
class WorkOrder:
    """
    WorkOrder
    """
    wo_nbr: int = fd("Work order number")
    creation_date: Optional[datetime] = fd("creation_date", default=None)
    machine: Optional[IdDescription] = fd("machine", default=None)
    product: Optional[IdDescription] = fd("product", default=None)
    qty_required: Optional[int] = fd("qty_required", default=0)
    qty_produced: Optional[int] = fd("qty_produced", default=0)
    estimated_start_date: Optional[datetime] = fd("estimated_start_date", default=None)
    estimated_end_date: Optional[datetime] = fd("estimated_end_date", default=None)
    start_date: Optional[datetime] = fd("start_date", default=None)
    end_date: Optional[datetime] = fd("end_date", default=None)
    delivery_date: Optional[datetime] = fd("delivery_date", default=None)
    enabled: bool = fd("Enabled?", default=True)
    id: Optional[str] = fd("id", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())
