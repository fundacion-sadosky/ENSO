"""
Model: Product
"""
from typing import List, Optional

from bson.objectid import ObjectId  # type: ignore
from hopeit.dataobjects import dataclass, dataobject

from app0.admin import fd


@dataobject
@dataclass
class Product:
    """Product"""
    name: str = fd("Name")
    description: str = fd("Descripcion", default="")
    enabled: bool = fd("Enabled?", default=True)
    barcode: Optional[str] = fd("Barcode", default=None)
    image: Optional[str] = fd("Principal app image", default=None)
    envases_por_bulto: Optional[int] = fd("envases_por_bulto", default=None)
    bultos_por_m3: Optional[int] = fd("bultos_por_m3", default=None)
    envases_por_m3: Optional[int] = fd("envases_por_m3", default=None)
    cadencia_unidades_h: Optional[int] = fd("cadencia_unidades_h", default=None)
    peso_envase: Optional[float] = fd("peso_envase", default=None)
    tipo_tapa: Optional[str] = fd("tipo_tapa", default=None)
    maquina: Optional[str] = fd("maquina", default=None)
    maquina_alternativa: Optional[str] = fd("maquina_alternativa", default=None)
    operarios: Optional[float] = fd("operarios", default=None)
    palletizadores: Optional[float] = fd("palletizadores", default=None)
    cavidades_maquina: Optional[int] = fd("cavidades_maquina", default=None)
    id: Optional[str] = fd("id", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())


@dataobject
@dataclass
class ProductDataStatus:
    status: Optional[str] = fd("status", default=None)
    day: Optional[str] = fd("day", default=None)
    hour: Optional[str] = fd("hour", default=None)
    qty: Optional[int] = fd("quantity", default=None)


@dataobject
@dataclass
class ProductData:
    """ProductData"""
    machine: Optional[str] = fd("machine code", default=None)
    date_from: Optional[str] = fd("date_from", default=None)
    date_to: Optional[str] = fd("date_to", default=None)
    total_sense: Optional[int] = fd("total sensor received", default=0)
    status_list: List[ProductDataStatus] = fd("status", default_factory=list)
