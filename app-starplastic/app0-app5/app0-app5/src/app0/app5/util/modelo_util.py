from datetime import datetime

dias_no_laborables = [5, 6] #Se agregó x defecto sábado y domingo


def es_dia_habil(fecha: datetime):
    return fecha.weekday() not in dias_no_laborables
