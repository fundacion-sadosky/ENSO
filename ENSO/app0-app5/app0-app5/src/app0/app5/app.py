"""
Model: App
"""
from typing import List, Optional

from hopeit.dataobjects import dataclass, dataobject

from app0.admin import fd
from app0.app5.machine import Machine


@dataobject
@dataclass
class AppData:
    """
    AppData
    """
    machines_working: Optional[int] = fd("machines_working", default=None)
    production: Optional[int] = fd("production", default=None)
    alerts: Optional[int] = fd("alerts", default=None)
    alerts2: Optional[int] = fd("alerts", default=None)
    machines: List[Machine] = fd("machines", default_factory=list)
