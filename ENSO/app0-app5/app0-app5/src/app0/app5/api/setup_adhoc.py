"""
Admin: setup-adhoc
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
from app0.app5.product import Product
from app0.app5.util import IDX_SENSOR_MACHINE, IDX_PRODUCT

logger = app_logger()
BaseProductos = Enum.load_csv("app0-app5/config", "BaseProductos", '*')
BaseProductosCavidades = Enum.load_csv("app0-app5/config", "BaseProductosCavidades", '*')

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
    if code == 'SENSEPROCFIX':
        mo = db(context.env)
        await init_sense_processed(mo)
    elif code == 'FIXIDS':
        mo = db(context.env)
        await fixids(mo)
    elif code == 'RECREATEPRODUCTS':
        mo = db(context.env)
        await _recreate_products(mo)
    elif code == 'PRODUCTCAVIDADES':
        mo = db(context.env)
        await _product_cavidades(mo)

    return Dto(o={'msg': 'OK Run'})


async def __postprocess__(payload: Union[Dto, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[Dto, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def init_sense_processed(mo):
    filter_query = {'processed': {'$exists': False}}
    col = mo[IDX_SENSOR_MACHINE]
    count = await col.count_documents(filter_query)

    while count > 0:
        cursor = mo[IDX_SENSOR_MACHINE].find(filter_query)
        for doc in await cursor.to_list(length=1000):
            await mo[IDX_SENSOR_MACHINE].update_one({'_id': doc['_id']},
                                                    {'$set': {'processed': False,
                                                              'id': str(doc['_id'])}})
        count -= 1000


async def fixids(mo):
    filter_query = {'fixed': {'$exists': False}}
    col = mo[IDX_SENSOR_MACHINE]
    count = await col.count_documents(filter_query)

    while count > 0:
        print("=========================>")
        print(f"=====> procesando {count}...")
        print("=========================>")
        cursor = mo[IDX_SENSOR_MACHINE].find(filter_query)
        for doc in await cursor.to_list(length=1000):
            await mo[IDX_SENSOR_MACHINE].update_one({'_id': doc['_id']},
                                                    {'$set': {'fixed': True,
                                                              'id': str(doc['_id'])}})

        count -= 1000
    print("=========================>")
    print("=====> fixids END")
    print("=========================>")


async def _recreate_products(mo):
    col = mo[IDX_PRODUCT]
    await col.delete_many({})
    print(f"coll {IDX_PRODUCT} delete all")
    for p in BaseProductos:
        try:
            product = Product(
                name=p['name'],
                barcode=p['barcode'],
                envases_por_bulto=int(p['envases_por_bulto']) if p['envases_por_bulto'] else None,
                bultos_por_m3=int(p['bultos_por_m3']) if p['bultos_por_m3'] else None,
                envases_por_m3=int(p['envases_por_m3']) if p['envases_por_m3'] else None,
                cadencia_unidades_h=int(p['cadencia_unidades_h']) if p['cadencia_unidades_h'] else None,
                peso_envase=float(p['peso_envase']) if p['peso_envase'] else None,
                tipo_tapa=p['tipo_tapa'],
                maquina=p['maquina'],
                maquina_alternativa=p['maquina_alternativa'],
                operarios=float(p['operarios']) if p['operarios'] else None,
                palletizadores=float(p['palletizadores']) if p['palletizadores'] else None,
            )
            await col.replace_one({'_id': ObjectId(product.id)}, Payload.to_obj(product), upsert=True)
        except Exception as e:
            print(f"ERROR: can't insert {p}")
            print(f"ERROR: {e}")
    print("=========================>")
    print("=====> _recreate_products END")
    print("=========================>")


async def _product_cavidades(mo):
    col = mo[IDX_PRODUCT]
    for p in BaseProductosCavidades:
        try:
            barcode = p['barcode']
            cavidades = int(p['cavidades']) if p['cavidades'] else 0
            maquina = p['maquina']
            maquina_alternativa = p['maquina_alternativa']
            operarios = float(p['operarios']) if p['operarios'] else 0.0

            await col.update_one({'barcode': barcode},
                                 {"$set": {'cavidades': cavidades,
                                           'maquina': maquina,
                                           'maquina_alternativa': maquina_alternativa,
                                           'operarios': operarios}})
        except Exception as e:
            print(f"ERROR: can't update {p}")
            print(f"ERROR: {e}")
    print("=========================>")
    print("=====> _product_cavidades END")
    print("=========================>")
