"""
Model: Machine
"""
from datetime import datetime
from typing import List, Optional

from bson.objectid import ObjectId  # type: ignore
from hopeit.dataobjects import dataclass, dataobject

from app0.admin import fd
from app0.admin.common import IdDescription


@dataobject
@dataclass
class Machine:
    """Machine"""
    nbr: str = fd("Number")
    name: str = fd("Name")
    code: str = fd("MQTT Code")
    description: str = fd("Description", default="")
    manufacturer: Optional[str] = fd("manufacturer", default="")
    model: Optional[str] = fd("model", default="")
    image: Optional[str] = fd("Principal app image", default=None)
    enabled: bool = fd("Enabled?", default=True)
    realtime_status: bool = fd("realtime_status?", default=False)
    last_status_date: Optional[datetime] = fd("last_status_date", default=None)
    last_status: Optional[IdDescription] = fd("last_status", default=None)
    id: Optional[str] = fd("id", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())


@dataobject
@dataclass
class MachineDataStatus:
    status: Optional[str] = fd("status", default=None)
    day: Optional[str] = fd("day", default=None)
    hour: Optional[str] = fd("hour", default=None)
    qty: Optional[int] = fd("quantity", default=None)
    seconds: Optional[int] = fd("seconds", default=None)


@dataobject
@dataclass
class MachineData:
    """MachineData"""
    machine: Optional[str] = fd("machine code", default=None)
    date_from: Optional[str] = fd("date_from", default=None)
    date_to: Optional[str] = fd("date_to", default=None)
    total_sense: Optional[int] = fd("total sensor received", default=0)
    total_seconds: Optional[int] = fd("total seconds in range", default=0)
    status_list: List[MachineDataStatus] = fd("status", default_factory=list)


@dataobject
@dataclass
class KpiDataMachine:
    """
    KpiDataMachine
    """
    nbr: str = fd("Number")
    name: str = fd("Name")
    code: str = fd("MQTT Code")
    last_status_date: Optional[datetime] = fd("last_status_date", default=None)
    last_status: Optional[IdDescription] = fd("last_status", default=None)
    sense_last_1d: Optional[int] = fd("sense_last_1d", default=0)
    sense_last_7d: Optional[int] = fd("sense_last_7d", default=0)
    sense_last_15d: Optional[int] = fd("sense_last_15d", default=0)
    sense_month: Optional[int] = fd("sense_month", default=0)
    status_list: List[MachineDataStatus] = fd("status", default_factory=list)


@dataobject
@dataclass
class KpiData:
    """
    KpiData
    """
    machines_working: Optional[int] = fd("machines_working", default=None)
    production: Optional[int] = fd("production", default=None)
    alerts: Optional[int] = fd("alerts", default=None)
    machines: List[KpiDataMachine] = fd("machines", default_factory=list)
