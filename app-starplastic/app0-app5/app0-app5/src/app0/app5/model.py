"""
Model: Model
"""
from datetime import datetime
from typing import List, Optional

from bson.objectid import ObjectId  # type: ignore
from hopeit.dataobjects import dataclass, dataobject

from app0.admin import fd
from app0.admin.file import PlatformFile


@dataobject
@dataclass
class ItemOt:
    id: int = fd("Id")
    ot_nro: str = fd("Nro OT")
    maquina_nro: str = fd("Nro Maquina")
    producto_id: str = fd("Id Producto", default="")
    producto_desc: str = fd("Tipo Producto", default="")
    maquina_desc: str = fd("Máquina descripcion", default="")
    color: str = fd("Color", default="")
    peso: float = fd("Peso", default=0.0)
    cantidad: int = fd("Cantidad planificada", default=0)
    horas: float = fd("Horas estimadas", default=0.0)
    fecha_vencimiento: Optional[datetime] = fd("Fecha vencimiento", default=None)
    cadencia: int = fd("Cadencia de máquina", default=0)
    operarios_requeridos: float = fd("Operarios requeridos", default=0.0)
    prioridad: int = fd("Cantidad planificada", default=0)
    setup_maquina: Optional[float] = fd("Setup máquina (h)", default=0.0)


@dataobject
@dataclass
class ItemFueraServicio:
    id: int = fd("Id")
    maquina: str = fd("Máquina")
    hora_inicio: Optional[datetime] = fd("Desde", default=None)
    hora_fin: Optional[datetime] = fd("Hasta", default=None)
    motivo: Optional[str] = fd("Motivo", default="")


@dataobject
@dataclass
class ModelInput:
    """Model Input"""
    tiempo_setup: float = fd("tiempo_setup", default=0.5)
    cantidad_operarios: int = fd("cantidad_operarios", default=3)
    fecha_inicio: Optional[datetime] = fd("fecha inicio", default=None)
    fuera_servicios: List[ItemFueraServicio] = fd("Fuera Servicios", default_factory=list)
    ots: List[ItemOt] = fd("OTs", default_factory=list)


@dataobject
@dataclass
class AgendaMaquinaOt:
    id: int = fd("Id")
    ot_nro: str = fd("Nro OT")
    maquina_nro: str = fd("Nro Maquina")
    hora_inicio: Optional[datetime] = fd("Desde", default=None)
    hora_fin: Optional[datetime] = fd("Hasta", default=None)
    cant_personal: Optional[float] = fd("Cantidad de Personal", default=None)
    producto: Optional[str] = fd("Producto", default=None)
    descripcion: Optional[str] = fd("Descripción", default='')
    is_setup_maquina: Optional[bool] = fd("Is setup máquina?", default=False)


@dataobject
@dataclass
class AgendaPersonal:
    id: int = fd("Id")
    cant_personal: float = fd("Cantidad de Personal")
    hora_inicio: Optional[datetime] = fd("Desde", default=None)
    hora_fin: Optional[datetime] = fd("Hasta", default=None)


@dataobject
@dataclass
class ModelOutput:
    """Model Output"""
    completamiento_ordenes: float = fd("CompletamientoOrdenes", default=0.0)
    tardanza_total: float = fd("TardanzaTotal", default=0.0)
    anticipacion_total: float = fd("AnticipacionTotal", default=0.0)
    maxima_tardanza: float = fd("MáximaTardanza", default=0.0)
    maxima_anticipacion: float = fd("MáximaAnticipacion", default=0.0)
    total_setup: float = fd("TotalSetup", default=0.0)
    total_produccion: float = fd("TotalProduccion", default=0.0)
    ordenes_tardias: float = fd("OrdenesTardias", default=0.0)
    ordenes_anticipadas: float = fd("OrdenesAnticipadas", default=0.0)
    uso_operarios_total: float = fd("USoOperariosTotal", default=0.0)
    productividad_operarios: float = fd("productividadOperarios", default=0.0)
    plan_inicio: Optional[datetime] = fd("Plan inicio", default=None)
    plan_fin: Optional[datetime] = fd("Plan fin", default=None)
    plan_inicio_preparacion: Optional[datetime] = fd("Plan inicio preparación", default=None)
    agenda_maquina_ot: List[AgendaMaquinaOt] = fd("Agenda de producción", default_factory=list)
    agenda_personal: List[AgendaPersonal] = fd("Paper Rolls Used", default_factory=list)
    error_code: Optional[str] = fd("Error code", default=None)
    error_msg: Optional[str] = fd("Error message", default=None)


@dataobject
@dataclass
class JobRunLog:
    """
    Job run log
    """
    job_id: str = fd("Job Id")
    line_date: datetime = fd("Line Date")
    text: str = fd("Text")
    id: Optional[str] = fd("Db id", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())


@dataobject
@dataclass
class ModelJob:
    """
    Job (Model Run)
    """
    creation_date: datetime = fd("Creation Date")
    creation_user: str = fd("Creation User")
    number: str = fd("Number")
    status: str = fd("Status")
    name: str = fd("Name", default="")
    description: Optional[str] = fd("Description", default="")
    model_input: Optional[ModelInput] = fd("Model input", default=None)
    model_output: Optional[ModelOutput] = fd("Model output", default=None)
    start_date: Optional[datetime] = fd("Start Date", default=None)
    end_date: Optional[datetime] = fd("End Date", default=None)
    error_text: Optional[str] = fd("Error text if something wrong", default=None)
    result_files: Optional[List[PlatformFile]] = fd("Result Files", default=None)
    origin_id: Optional[str] = fd("Origin Id", default=None)
    origin_desc: Optional[str] = fd("Origin desc", default=None)
    scenario_status: Optional[str] = fd("Scenario Status", default=None)
    id: Optional[str] = fd("Db id", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())
