# Sample data

```python
    model_input = {
        'tiempo_setup': 0.5,
        'cantidad_operarios': 1,
        'ots': [
            {'id': 1, 
             'ot_nro': "24597",
             'maquina_nro': "23",
             'producto_id': "7020310",
             'producto_desc': "BID T64 20 ECO-BIDON",
             'maquina_desc': "COEX-23 - SOPLADORA COEXTRUSORA KONG KEE",
             'color': "Blanco",
             'peso': 1050.0,
             'cantidad': 5760,
             'horas': 34.9,
             'fecha_vencimiento': datetime.strptime('19/07/2023', '%d/%m/%y'),
             'cadencia': 165,
             'operarios_requeridos': 2,
             'prioridad': 1},
            {'id': 2, 
             'ot_nro': "24599",
             'maquina_nro': "23",
             'producto_id': "7020310",
             'producto_desc': "BID T64 20 ECO-BIDON",
             'maquina_desc': "COEX-23 - SOPLADORA COEXTRUSORA KONG KEE",
             'color': "Blanco",
             'peso': 1050.0,
             'cantidad': 5760,
             'horas': 34.9,
             'fecha_vencimiento': datetime.strptime('19/07/2023', '%d/%m/%y'),
             'cadencia': 165,
             'operarios_requeridos': 2,
             'prioridad': 1},
        ],
        'fuera_servicios': [
            {'id': 1,
             'maquina': "23",
             'hora_inicio': datetime.strptime('19/07/2023 10:00', '%d/%m/%y %H:%M'),
             'hora_fin': datetime.strptime('19/07/2023 20:00', '%d/%m/%y %H:%M'),
            },
        ]
    }
```

    # ejecutar el proceso etc etc
    # ejecutar el proceso etc etc
    # ejecutar el proceso etc etc
    # con los resultados del proceso, construir el model output
    model_output = {
        'completamiento_ordenes': 3.5,
        'tardanza_total': 3.5,
        'anticipacion_total': 3.5,
        'maxima_tardanza': 3.5,
        'maxima_anticipacion': 3.5,
        'total_setup': 3.5,
        'total_produccion': 3.5,
        'ordenes_tardias': 3.5,
        'ordenes_anticipadas': 3.5,
        'uso_operarios_total': 3.5,
        'productividad_operarios': 3.5,
        'agenda_maquina_ot': [
            {'id': 1,
             'ot_nro': "5361",
             'maquina_nro': "27",
             'hora_inicio': datetime.strptime('19/07/2023 10:00', '%d/%m/%y %H:%M'),
             'hora_fin': datetime.strptime('19/07/2023 20:00', '%d/%m/%y %H:%M'),
            },
            {'id': 2,
             'ot_nro': "5823",
             'maquina_nro': "27",
             'hora_inicio': datetime.strptime('19/07/2023 21:00', '%d/%m/%y %H:%M'),
             'hora_fin': datetime.strptime('19/07/2023 23:30', '%d/%m/%y %H:%M'),
            },
        ],
        'agenda_personal': [
            {'id': 1,
             'cant_personal': 1.0,
             'hora_inicio': datetime.strptime('19/07/2023 10:00', '%d/%m/%y %H:%M'),
             'hora_fin': datetime.strptime('19/07/2023 20:00', '%d/%m/%y %H:%M'),
            },
            {'id': 2,
             'cant_personal': 2.0,
             'hora_inicio': datetime.strptime('19/07/2023 21:00', '%d/%m/%y %H:%M'),
             'hora_fin': datetime.strptime('19/07/2023 23:30', '%d/%m/%y %H:%M'),
            },
        ],
    }

    return model_output

