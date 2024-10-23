"""
Model: sensor
"""
from datetime import datetime
from typing import Optional, List

from bson.objectid import ObjectId  # type: ignore
from hopeit.dataobjects import dataclass, dataobject

from app0.admin import fd


@dataobject
@dataclass
class SensorMachine:
    client: Optional[str] = fd("client", default=None)
    sense_time: Optional[datetime] = fd("sense time", default=None)
    topic: Optional[str] = fd("topic", default=None)
    machine: Optional[str] = fd("machine", default=None)
    metric: Optional[str] = fd("metric", default=None)
    product: Optional[str] = fd("product", default=None)
    valstr: Optional[str] = fd("valstr", default=None)
    valint: Optional[int] = fd("valint", default=None)
    valflt: Optional[float] = fd("valflt", default=None)
    processed: Optional[bool] = fd("sensor data processed?", default=False)
    fixed: Optional[bool] = fd("temp process field", default=False)
    id: Optional[str] = fd("id", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())


@dataobject
@dataclass
class MachineMetric:
    metric_date: str = fd("status date in format yyyymmdd")
    metric_hour: str = fd("status hour in format xx_xx or 13_14", default=None)
    machine: Optional[str] = fd("machine", default=None)
    metric: Optional[str] = fd("metric type", default=None)
    metric_value: Optional[str] = fd("metric value", default=None)
    metric_qty: Optional[int] = fd("metric quantity", default=None)
    id: Optional[str] = fd("id", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())


@dataobject
@dataclass
class ProductMetric:
    metric_date: str = fd("status date in format yyyymmdd")
    metric_hour: str = fd("status hour in format xx_xx or 13_14", default=None)
    machine: Optional[str] = fd("machine", default=None)
    product: Optional[str] = fd("product", default=None)
    metric: Optional[str] = fd("metric type", default=None)
    metric_qty: Optional[int] = fd("metric quantity", default=None)
    metric_qtyflt: Optional[float] = fd("metric quantity float", default=None)
    id: Optional[str] = fd("id", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())


@dataobject
@dataclass
class SensorData:
    """SensorData"""
    machine: Optional[str] = fd("machine code", default=None)
    date_from: Optional[str] = fd("date_from", default=None)
    date_to: Optional[str] = fd("date_to", default=None)
    total_sense: Optional[int] = fd("total sensor received", default=0)
    sense_list: List[SensorMachine] = fd("senses", default_factory=list)
