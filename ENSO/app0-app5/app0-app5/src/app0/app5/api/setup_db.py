"""
Admin: setup-db
"""
from typing import Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_logger
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import Dto, HttpRespInfo
from app0.admin.enums import Enum
from app0.app5.machine import Machine
from app0.app5.product import Product
from app0.app5.util import (IDX_MACHINE, IDX_PRODUCT)

logger = app_logger()
BaseProductos = Enum.load_csv("app0-app5/config", "BaseProductos", '*')

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('code', str, "Setup Code")
    ],
    responses={
        200: (Dto, "OK"),
        400: (str, "Bad request"),
        403: (str, "Operation forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: None, context: EventContext, code: str) -> Union[Dto, HttpRespInfo]:
    """
    Initialize DB
    """
    # check if empty
    if code == 'FORCE':
        mo = db(context.env)
        # check if collections exists and create or clean
        query = {"name": {"$regex": r"^(?!system\.)"}}
        req_colls = [IDX_MACHINE, IDX_PRODUCT]
        coll_names = await mo.list_collection_names(filter=query)
        print(f"coll existentes: {coll_names}")
        for col in req_colls:
            if col in coll_names:
                await mo.drop_collection(col)
                print(f"coll {col} dropped")
            await mo.create_collection(col)
            print(f"coll {col} created")

        await _create_base_machines(mo)
        await _create_base_products(mo)

    return Dto(o={'msg': 'OK Run'})


async def __postprocess__(payload: Union[Dto, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[Dto, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _create_base_machines(mo):
    """
    Create Base machines
    """
    col = mo[IDX_MACHINE]
    for i in range(1, 33):
        machine = Machine(
            nbr=str(i),
            name=f"Máquina{str(i).rjust(2, '0')}",
            code=f"M{i}",
            realtime_status=(i == 17)
        )
        await col.replace_one({'_id': ObjectId(machine.id)}, Payload.to_obj(machine), upsert=True)


async def _create_base_products(mo):
    """
    Create Base products
    """
    col = mo[IDX_PRODUCT]
    for p in BaseProductos:
        try:
            product = Product(
                name=p['name'],
                barcode=p['barcode'],
                envases_por_bulto=p['envases_por_bulto'],
                bultos_por_m3=p['bultos_por_m3'],
                envases_por_m3=p['envases_por_m3'],
                cadencia_unidades_h=p['cadencia_unidades_h'],
                peso_envase=p['peso_envase'],
                tipo_tapa=p['tipo_tapa'],
                maquina=p['maquina'],
                maquina_alternativa=p['maquina_alternativa'],
                operarios=p['operarios'],
                palletizadores=p['palletizadores']
            )
            await col.replace_one({'_id': ObjectId(product.id)}, Payload.to_obj(product), upsert=True)
        except Exception:
            print(f"ERROR: can't insert {p}")
