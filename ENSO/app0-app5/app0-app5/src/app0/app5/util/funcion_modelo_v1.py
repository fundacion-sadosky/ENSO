"""
Created on Wed Aug 16 07:29:45 2023

@author: jiramello84
"""
from datetime import timedelta
from ortools.linear_solver import pywraplp
from app0.app5.model import ModelInput, ModelOutput, AgendaMaquinaOt, AgendaPersonal
from app0.app5.util import date_util, modelo_util


def run_model(model_input: ModelInput) -> ModelOutput:
    """run model"""
    model_input = _validate_and_fix(model_input)
    fecha_inicio_plan = model_input.fecha_inicio

    # Generar lista de diccionarios con la clave 'ots'
    lista_id = [{'id': entry.id, 'ot': entry.ot_nro, 'maquina': entry.maquina_nro
                } for entry in model_input.ots]

    #SETS
    # operarios
    operarios = []
    for i in range(model_input.cantidad_operarios):
        operarios.append('o{}'.format(str(i+1))) 

    # ordenes de trabajo
    ots = [ot.ot_nro for ot in model_input.ots]

    # máquinas
    maquinas = list(set(ot.maquina_nro for ot in model_input.ots))

    # máquinas fuera de servicio
    fuera_servicios = list(set(item.maquina for item in model_input.fuera_servicios))

    #PARÁMETROS

    #operarios requeridos x ot
    operarios_requeridos = {ot.ot_nro: ot.operarios_requeridos for ot in model_input.ots}    

    #asignación ot-máquina
    asignacion = {ot.ot_nro: ot.maquina_nro for ot in model_input.ots}

    #prioridad ot
    prioridad = {ot.ot_nro: ot.prioridad for ot in model_input.ots}

    #tiempo ot
    proc = {ot.ot_nro: ot.horas for ot in model_input.ots}

    #fecha entrega ot
    fecha_vencimiento = {ot.ot_nro: ot.fecha_vencimiento for ot in model_input.ots}
    #fecha entrega ot en horas
    fecha_entrega = {ot_nro: (fecha - fecha_inicio_plan).total_seconds() / 3600 + 24 for ot_nro, fecha in fecha_vencimiento.items()}  # noqa

    #tiempos inicio y fin de fuera de máquinas fuera de servicio
    tiinactiva = {}
    tfinactiva = {}
    #Procesa los datos de 'fuera_servicios'
    for item in model_input.fuera_servicios:
        maquina = item.maquina
        hora_inicio = item.hora_inicio
        hora_fin = item.hora_fin
        diferencia_horas = (hora_inicio - fecha_inicio_plan).total_seconds() / 3600
        tiinactiva[maquina] = float(diferencia_horas)
        diferencia_horas = (hora_fin - fecha_inicio_plan).total_seconds() / 3600
        tfinactiva[maquina] = float(diferencia_horas)

    #changeover
    changeover = {(ot1, ot2): model_input.tiempo_setup if ot1 != ot2 else 0.0 for ot1 in ots for ot2 in ots}

    # Validación de datos de entrada y ejecución modelo
    #Validación 2: La fecha de inicio de indisponibilidad de máquina debe ser mayor o
    #igual a la fecha de inicio del plan.
    for fs in model_input.fuera_servicios:
        if fs.hora_inicio < fecha_inicio_plan:
            error_msg = f"Máquina {fs.maquina}: Fecha de fuera de servicio anterior a fecha de inicio del plan."
            return ModelOutput(
                error_code='INFEASIBLE',
                error_msg=error_msg)

    # Validación 1: verifica que tiempo de OT con prioridad 1 no coincida con tiempo de inicio de
    # fuera servicio de máquina asignada
    ot_prioridad_1 = None
    for ot in model_input.ots:
        if ot.prioridad == 1:
            ot_prioridad_1 = ot
            break
    for fs in model_input.fuera_servicios:
        if fs.maquina == ot_prioridad_1.maquina_nro:
            if tiinactiva[fs.maquina] < ot_prioridad_1.horas:
                    error_msg = f"""
                    La OT {ot_prioridad_1.ot_nro} con prioridad 1 y duración {ot_prioridad_1.horas} horas, no puede
                    ejecutarse al inicio del plan ya que la máquina {ot_prioridad_1.maquina_nro} no está disponible de
                    {date_util.to_dmyhm(fs.hora_inicio)} a {date_util.to_dmyhm(fs.hora_fin)}. Sugerencia: La OT
                    {ot_prioridad_1.ot_nro} no debería tener prioridad 1. Elija otra OT para asignar la prioridad 1,
                    cuya máquina esté disponible.
                    """
                    return ModelOutput(
                        error_code='INFEASIBLE',
                        error_msg=error_msg)

    #Validación 3: La fecha de inicio del plan debe ser mayor o igual al día posterior al momento
    # en el cual se genera el plan (función hoy()+1 o algo por el estilo).
    fecha_control = date_util.now()
    # while not modelo_util.es_dia_habil(fecha_control):
    #     fecha_control += timedelta(days=1)
    if fecha_inicio_plan < fecha_control:
        # error_msg = 'La fecha de inicio del plan es anterior al día en el que puede iniciarse'
        error_msg = 'La fecha de inicio del plan debe ser una fecha futura'
        return ModelOutput(
            error_code='INFEASIBLE',
            error_msg=error_msg)

    #Validación 4: Ninguna OT puede tener un requerimiento de personal mayor al personal disponible.
    #En caso que así sea, sacar el mensaje siguiente e interrumpir la corrida hasta que se resuelva:
    for ot in model_input.ots:
        if ot.operarios_requeridos > model_input.cantidad_operarios:
            error_msg = f'La OT {ot.ot_nro}, requiere una cantidad de personal superior a la disponible. Corrija la cantidad de personal disponible o el requerimiento de la OT' # noqa
            return ModelOutput(
                error_code='INFEASIBLE',
                error_msg=error_msg)

    #Validación 5: No deberían existir dos OT con igual ID. Si sucediera interrumpir
    # la corrida hasta que se resuelva y dar mensaje al usuario
    # Obtener la lista de órdenes de trabajo (ots) del diccionario
    unique_otsnros = []
    for ot in model_input.ots:
        if ot.ot_nro not in unique_otsnros:
            unique_otsnros.append(ot.ot_nro)
        else:
            error_msg = f'Existen OTs con igual número ({ot.ot_nro}), corregir. Cada OT debe tener un único número' # noqa
            return ModelOutput(
                error_code='INFEASIBLE',
                error_msg=error_msg)

    #Validación 6: No debería reportarse una máquina fuera de servicio, que no aparezca en el listado de OTs.
    # Obtener las listas de órdenes de trabajo (ots) y fuera de servicio (fuera_servicios)
    unique_otsmaquinas = []
    for ot in model_input.ots:
        if ot.maquina_nro not in unique_otsmaquinas:
            unique_otsmaquinas.append(ot.maquina_nro)
    for fs in model_input.fuera_servicios:
        if fs.maquina not in unique_otsmaquinas:
            error_msg = f'Existen máquinas fueras de servicio ({fs.maquina}) que no se utilizan en ninguna OT, corregir.' # noqa
            return ModelOutput(
                error_code='INFEASIBLE',
                error_msg=error_msg)

    #Validación 7: La fecha de vencimiento de ots debe ser mayor o igual a la fecha de inicio del plan.
    for ot in model_input.ots:
        if ot.fecha_vencimiento < fecha_inicio_plan:
            error_msg = f"OT {ot.ot_nro}: Fecha de entrega de la OT anterior a fecha de inicio del plan, corregir."
            return ModelOutput(
                error_code='INFEASIBLE',
                error_msg=error_msg)

    ###############################################################################
    ###############################################################################
    # Construcción modelo
    # BigM
    #bigM=300
    bigM = 2 * (sum(changeover[(j, jj)] for j, jj in changeover) + sum(proc[j] for j in proc))
    # Valor máxima prioridad
    MaximaPrioridad = max(prioridad.values())


    #SOLVER
    print("=========================>")
    print("=====> JOB creating solver...")
    print("=========================>")
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Parámetro primerOT
    primerOT = {}
    for m in maquinas:
        for j in ots:
            if (j, m) in asignacion.items():
                if prioridad[j] == min(prioridad[jj] for jj in ots if (jj, m) in asignacion.items()):
                    primerOT[(j, m)] = 1
                else:
                    primerOT[(j, m)] = 0


    #VARIABLES
    TF = {}
    Tard = {}
    Earl = {}
    zy = {}
    for j in ots:
        for m in maquinas:
            TF[(j, m)] = solver.NumVar(0, solver.infinity(), f'TF_{j}_{m}')
            Tard[(j, m)] = solver.NumVar(0, solver.infinity(), f'Tard_{j}_{m}')
            Earl[(j, m)] = solver.NumVar(0, solver.infinity(), f'Earl_{j}_{m}')
            for o in operarios:
                zy[(j,m,o)] = solver.IntVar(0,1,f'zy_{j}_{m}_{o}')

    #x2
    x2 = {}
    for j in ots:
        for jj in ots:
            if j != jj:
                for o in operarios:
                    x2[(j, jj, o)] = solver.IntVar(0,1,f'x2_{j}_{jj}_{o}')

    # TFo variables
    TFo = {}
    for j in ots:
        for o in operarios:
            TFo[j, o] = solver.NumVar(0, solver.infinity(), f'TFo{j},{o}')

    # Xgral(j,jj) En este modelo sería un parámetro
    xgral = {}
    #for j in ots:
    #    for jj in ots:
    #        if (j!=jj):
    #            xgral[j,jj] = solver.IntVar(0, 1, 'xgral[{},{}]'.format(j,jj))
    for m in maquinas:
        for j in ots:
            if (j, m) in asignacion.items():
                for jj in ots:
                    if jj != j and (jj,m) in asignacion.items():
                        if prioridad[j] < prioridad[jj]:
                            xgral[j,jj] = 1
                        else:
                            xgral[j,jj] = 0

    # z(j,o)
    z = {}
    for j in ots:
        for o in operarios:
            z[j,o] = solver.IntVar(0, 1, 'z[{},{}]'.format(j,o))

    # w(j,o)
    w = {}
    for j in ots:
        for o in operarios:
            w[j,o] = solver.IntVar(0, 1, 'w[{},{}]'.format(j,o))

    #Yanterior(j)
    Yanterior = {}
    for j in ots:
        Yanterior[j] = solver.IntVar(0, 1, 'Yanterior[{}]'.format(j))

    #OrdenMaquina(j,m)$asignacion(j,m)= 1+ sum(jj$asignacion(jj,m), xgral.l(j,jj))
    ordenmaquina = {}
    for j, m in asignacion.items():
        ordenmaquina[(j, m)] = 1 + sum(xgral[j, jj] for jj in ots if (jj, m) in asignacion.items() and (j!=jj))

    #x(j,jj,m) es variable fija en este modelo
    x = {}
    for m in maquinas:
        for j in ots:
            for jj in ots:
                if (j, m) in asignacion.items():
                    if (jj, m) in asignacion.items() and (j!=jj):
                        if ordenmaquina[j, m] == ordenmaquina[jj, m] + 1:
                            x[j, jj, m] = 1
                        else:
                            x[j, jj, m] = 0

    y = {}
    for j in ots:
        for m in maquinas:
            if (j,m) in primerOT:
                y[(j,m)] = primerOT[(j,m)]
            else:
                y[(j,m)] = 0

    # Makespam 1 y 2, Tardanza Total y prioOF
    Mk  = solver.NumVar(-solver.infinity(), solver.infinity(), 'Mk')
    Mk2 = solver.NumVar(-solver.infinity(), solver.infinity(), 'Mk2')
    TT  = solver.NumVar(-solver.infinity(), solver.infinity(), 'TT')
    prioOF = solver.NumVar(-solver.infinity(), solver.infinity(), 'piorFO')

    # Orden Tardía
    D = {}
    for j in ots:
        for m in maquinas:
            D[(j, m)] = solver.IntVar(0,1,f'D_{j}_{m}')

    # Otras variables
    maxT = solver.NumVar(-solver.infinity(), solver.infinity(), 'maxT')
    maxA = solver.NumVar(-solver.infinity(), solver.infinity(), 'maxA')
    NbD  = solver.NumVar(-solver.infinity(), solver.infinity(), 'NbD')
    TE   = solver.NumVar(-solver.infinity(), solver.infinity(), 'TE')


    # RESTRICCIONES (CONSTRAINTS)
    ###########################################################################

    #AsigOper(j).. sum(o,z(j,o))=e=operarios(j);
    AsigOper = {}
    for j in ots:
        # restricción de asignación de operarios
        AsigOper[j] = solver.Add(sum(z[(j,o)] for o in operarios) == operarios_requeridos[j], name=f'AsigOper_{j}')

    # FirstJobOP(O) .. SUM(j, W(J,O)) =e= 1;
    FirstJobOP = {}
    for o in operarios:
        FirstJobOP[o] = solver.Add(solver.Sum([w[(j, o)] for j in ots]) <= 1, name=f'FirstJobOP_{o}')

    #FirstIntermJobOP(jj,O) ..
    #W(jj,O)+ SUM[j $(NOT SAMEAS(j,jj)), X2(j,jj,O)] =e= z(jj,o);
    FirstIntermJobOP = {}
    for jj in ots:
        for o in operarios:
            FirstIntermJobOP[(jj,o)] = solver.Add(w[(jj,o)] + sum(x2[(j,jj,o)] for j in ots if j != jj) == z[(jj,o)],
                                                  name=f'FirstIntermJobOP_{jj}_{o}')

    #PredecOP(jj,O) .. SUM[j $(NOT SAMEAS(j,jj)), X2(j,jj,O)] =l= z(jj,o) ;
    PredecOP = {}
    for o in operarios:
        for jj in ots:
            PredecOP[(jj,o)]=solver.Add(sum(x2[j,jj,o] for j in ots if j != jj) <= z[(jj,o)],
                                        name=f'PredecOP_{jj}_{o}')


    #SucesOP(j,O) .. SUM[jj $(NOT SAMEAS(j,jj)), X2(j,jj,O)] =l= z(j,o) ;
    SucesOP = {}
    for o in operarios:
        for j in ots:
            SucesOP[(j,o)] = solver.Add(sum(x2[(j,jj,o)] for jj in ots if j!=jj) <= z[(j,o)],
                                        name=f'SucesOP_{j}_{o}')

    #tiempoFinOP(j,jj,O)$(NOT SAMEAS(j,jj)).. TFo(jj,O) =g= TFo(j,O)+proc(jj)
    #                                 + changeover(j,jj)-(1-X2(j,jj,O))*bigM ;
    tiempoFinOP = {}
    for jj in ots:
        for j in ots:
            if j != jj:
                for o in operarios:
                    tiempoFinOP[(j,jj,o)] = solver.Add(TFo[jj, o] >= TFo[j, o] + proc[jj] + changeover[j, jj] - (1 - x2[j, jj, o]) * bigM,  # noqa
                                                       name=f'tiempoFinOP_{j}_{jj}_{o}')

    # tiempoFinFirstJobOP(j,O).. TFo(j,O) =g= proc(j)*w(j,O);
    tiempoFinFirstJobOP = {}
    for j in ots:
        for o in operarios:
            tiempoFinFirstJobOP[(j,o)] = solver.Add(TFo[j, o] >= proc[j] * w[(j, o)],
                                                    name=f'tiempoFinFirstJobOP_{j}_{o}')

    #tfoUB(j,o).. TFo(j,o) =l= BigM * z(j,o);
    TFoUB = {}
    for j in ots:
        for o in operarios:
            TFoUB[(j,o)] = solver.Add(TFo[j, o] <= bigM * z[j, o], name=f'TFoUB_{j}_{o}')

    #AsigFirst(j,o)..  W(J,O)=l= z(j,o);
    AsigFirst = {}
    for j in ots:
        for o in operarios:
            AsigFirst[(j,o)] = solver.Add(w[(j,o)] <= z[(j, o)], name=f'AsigFirst_{j}_{o}')

    #Log1(j,m,o)$Asignacion(j,m).. zy(j,m,o) =e= z(j,o) ;
    Log1 = {}
    for j,m in asignacion.items():
        for o in operarios:
            # restricción de equivalencia de variables
            Log1[(j,m,o)] = solver.Add(zy[(j,m,o)] == z[(j,o)], name=f'Log1_{j}_{m}_{o}' )

    # Log4(j,m,o)$(not Asignacion(j,m)).. zy(j,m,o) =e= 0  ;
    Log4 = {}
    for j in ots:
        for m in maquinas:
            if (j, m) not in asignacion.items():
                Log4[(j,m,o)] = solver.Add(zy[j, m, o] == 0, name=f'Log4_{j}_{m}_{o}')
    # Log5(j,m)$Asignacion(j,m).. sum(o,zy(j,m,o)) =e= operarios(j);
    Log5 = {}
    for j,m in asignacion.items():
            Log5[(j,m)] = solver.Add(sum(zy[(j, m, o)] for o in operarios) == operarios_requeridos[j], name=f'Log5_{j}_{m}')

    # IgualTF1(j,m,o)$Asignacion(j,m).. tf(j,m) =g= tfo(j,o) - bigm * (1- zy(j,m,o));
    IgualTF1 ={}
    for j, m in asignacion.items():
        for o in operarios:
            IgualTF1[(j,m,o)] = solver.Add(TF[(j, m)] >= TFo[(j,o)] - bigM * (1-zy[(j, m, o)]), name='IgualTF1_{j}_{m}_{o}')

    # IgualTF2(j,m,o)$Asignacion(j,m).. tf(j,m) =l= tfo(j,o) + bigm * (1- zy(j,m,o)); 
    IgualTF2 = {}
    for j, m in asignacion.items():
        for o in operarios:
            IgualTF2[(j,m,o)] = solver.Add(TF[(j, m)] <= TFo[(j,o)] + bigM * (1-zy[(j, m, o)]), name='IgualTF2_{j}_{m}_{o}')

    # FirstJob(m) .. SUM(j$Asignacion(j,m), Y(j,m)) =e= 1;
    FirstJob = {}
    for m in maquinas:
        FirstJob[(m)] = solver.Add(sum(y[(j, m)] for j in ots if (j, m) in asignacion.items()) == 1)


    # FirstIntermJob(jj,m)$Asignacion(jj,m) ..
    # Y(jj,m)+ SUM[j $(Asignacion(j,m) and(NOT SAMEAS(j,jj))), X(j,jj,m)] =e= 1;
    FirstIntermJob = {}
    for (jj, m) in asignacion.items():
        FirstIntermJob[(jj,m)] = solver.Add(y[(jj,m)] + sum(x[(j,jj,m)] for (j,m) in filter(lambda jm: jm[1]==m and jm[0]!=jj, asignacion.items())) == 1)  # noqa

    #Predec(jj,m)$Asignacion(jj,m) ..
    # SUM[j $(Asignacion(j,m) and (NOT SAMEAS(j,jj))),X(j,jj,m)] =l= 1 ;
    Predec = {}
    for jj, m in asignacion.items():
        Predec[(jj,m)] = solver.Add(sum(x[(j,jj,m)
                        ] for (j,m) in filter(lambda jm: jm[1]==m and jm[0]!=jj
                                              ,asignacion.items())) <= 1)

    #Suces(j,m)$Asignacion(j,m) ..
    # SUM[jj $(Asignacion(jj,m) and(NOT SAMEAS(j,jj))), X(j,jj,m)] =l= 1 ;
    Suces = {}
    for j, m in asignacion.items():
        Suces[(j,m)] = solver.Add(sum(x[(j,jj,m)
                        ] for (jj,m) in filter(lambda jm: jm[1]==m and jm[0]!=j
                                               ,asignacion.items())) <= 1)

    #tiempoFin(j,jj,m)$(Asignacion(j,m) and Asignacion(jj,m) and (NOT SAMEAS(j,jj)))
    #.. TF(jj,m) =g= TF(j,m)+proc(jj)+ changeover(j,jj)-(1-X(j,jj,m))*bigM ;
    tiempoFin = {}
    for jj, mm in asignacion.items():
        for j, m in asignacion.items():
            if mm==m and j != jj:
                tiempoFin[(j,jj,m)] = solver.Add(TF[(jj, m)] >= TF[(j, m)] + proc[jj] + changeover[(j, jj)
                            ] - (1 - x[(j, jj, m)]) * bigM)

    #tiempoFinFirstJob(j,m)$Asignacion(j,m) .. TF(j,m) =g= proc(j)*Y(j,m);
    tiempoFinFirstJob = {}
    for j, m in asignacion.items():
        tiempoFinFirstJob[(j,m)] = solver.Add(TF[(j,m)] >= proc[j] * y[(j,m)])


    #tiempofinfirstjob2(j,m)$(asignacion(j,m) and (Prioridad(j) eq 1)).. tf(j,m) =e= proc(j);
    tiempofinfirstjob2 = {}
    for j, m in asignacion.items():
        if prioridad[j] == 1:
            tiempofinfirstjob2[(j,m)] = solver.Add(TF[(j, m)] == proc[j])

    #maqFS1(j,m)$(asignacion(j,m) and fueraservicio(m))..
    # tf(j,m)=l=tiinactiva(m)+BigM*(1-Yanterior(j));
    maqFS1 = {}
    for j, m in asignacion.items():
        if m in fuera_servicios:
            maqFS1[(j,m)] = solver.Add(TF[j, m] <= tiinactiva[m] + bigM * (1 - Yanterior[j]))

    #maqFS2(j,m)$(asignacion(j,m) and fueraservicio(m))..
    #tf(j,m)-proc(j)=g= tfinactiva(m)*(1-Yanterior(j));
    maqFS2 = {}
    for j, m in asignacion.items():
        if m in fuera_servicios:
            maqFS2[(j,m)] = solver.Add(TF[j, m] - proc[j] >= tfinactiva[m] * (1 - Yanterior[j]))

    #precedenciaGral(j,jj,m)$((Asignacion(j,m))
    # and (Asignacion(jj,m))
    # and (ord(j) ne ord(jj)))..
    #                 TF(jj,m) =g= TF(j,m)-(1-Xgral(j,jj))*bigM  ;
    precedenciaGral = {}
    for j, m in asignacion.items():
        for jj, mm in asignacion.items():
            if j != jj and m == mm:
                precedenciaGral[(j,jj,m)] = solver.Add(TF[(jj, m)] >= TF[(j, m)
                                            ] - (1 - xgral[(j, jj)]) * bigM)

    # noasignar(j,m)$(not Asignacion(j,m))..  Y(j,m)=e=0;
    noasignar = {}
    for j in ots:
        for m in maquinas:
            if (j, m) not in asignacion.items():
                noasignar[(j,m)] = solver.Add(y[(j, m)] == 0)

    # makespanDef(j,m)$Asignacion(j,m) .. Mk =g= TF(j,m) ;
    makespanDef = {}
    for j, m in asignacion.items():
        makespanDef[(j,m)] = solver.Add(Mk >= TF[(j, m)], name='makespanDef_{j}_{m}')

    # makespanDef2(j,o) .. Mk2 =g= TFo(j,o) ;
    makespanDef2 = {}
    for j in ots:
        for o in operarios:
            makespanDef2[(j,o)] = solver.Add(Mk2 >= TFo[(j, o)], name='makespanDef2_{j}_{o}')

    #minPrioridad(j,m)$(Asignacion(j,m))..
    #(tf(j,m))*(maximaprioridad+1-prioridad(j)+Mk)=l= prioOF;
    minPrioridad = {}
    for j,m in asignacion.items():
        minPrioridad[(j,m)] = solver.Add(TF[(j,m)]*(MaximaPrioridad + 1 - prioridad[j]
                                                    ) + Mk <= prioOF)

    #Check Constraint Total
    print('Number of partial constraints =', solver.NumConstraints())

    #Parámetros del Solver
    solver.Minimize(prioOF)
    solver.set_time_limit(600000)
    gap = 0.0
    solverParams = pywraplp.MPSolverParameters()
    solverParams.SetDoubleParam(solverParams.RELATIVE_MIP_GAP, gap)
    print("=========================>")
    print("=====> JOB solver.Solve START")
    print("=========================>")
    status = solver.Solve(solverParams)
    print("=========================>")
    print("=====> JOB solver.Solve END")
    print("=========================>")


    if status == pywraplp.Solver.OPTIMAL:
        print("Solución óptima")
        print('Objective value =', solver.Objective().Value())
        print(prioOF.name(),'=', prioOF.solution_value())
        print('relative gap (%):', (solver.Objective().Value()-solver.Objective().BestBound())/solver.Objective().BestBound()*100)
        print()
        print('Problem solved in %f milliseconds' % solver.wall_time())
        print('Problem solved in %d iterations' % solver.iterations())
        print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

    elif status == pywraplp.Solver.FEASIBLE:
        print("Solución factible")
        print('Objective value =', solver.Objective().Value())
        print(prioOF.name(),'=', prioOF.solution_value())
        print('relative gap (%):', (solver.Objective().Value
                                    ()-solver.Objective().BestBound())/solver.Objective().BestBound()*100)
        print()
        print('Problem solved in %f milliseconds' % solver.wall_time())
        print('Problem solved in %d iterations' % solver.iterations())
        print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
    elif status == pywraplp.Solver.INFEASIBLE:
        print('El problema es infactible')
        print('Objective value =', solver.Objective().Value())
        print(prioOF.name(),'=', prioOF.solution_value())
        # codigo comentado zero division error
        # print('relative gap (%):', (solver.Objective().Value()-solver.Objective(
        #     ).BestBound())/solver.Objective().BestBound()*100)
        # print()
        print('Problem solved in %f milliseconds' % solver.wall_time())
        print('Problem solved in %d iterations' % solver.iterations())
        print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

        return ModelOutput(
            error_code='INFEASIBLE',
            error_msg='Problema infactible')  # noqa
        
    ###############################################################################
    ###############################################################################
    # model output

    # IndicadoresPerformance('CompletamientoOrdenes')= Mk.l;
    tiempo_fin = {}
    max_TF = 0
    for j,m in asignacion.items():
            if (TF[j,m].solution_value() > 0):
                tiempo_fin[j,m] = TF[j,m].solution_value()
                max_TF = max(max_TF,tiempo_fin[j,m])
    completamiento_ordenes = max_TF

    #IndicadoresPerformance('TardanzaTotal')= tt.l;
    tardanza_total = TT.solution_value()

    #IndicadoresPerformance('AnticipacionTotal')= te.l  ;
    anticipacion_total = TE.solution_value()

    #IndicadoresPerformance('MaximaTardanza')= maxT.l ;
    maxT_result = 0
    for j in ots:
        for m in maquinas:
            maxT_result = max(maxT_result,Tard[(j,m)].solution_value())
    maxima_tardanza = maxT_result

    #IndicadoresPerformance('MaximaAnticipacion')=maxA.l;
    maxA_result = 0
    for j in ots:
        for m in maquinas:
            maxA_result = max(maxA_result,Earl[(j,m)].solution_value())
    maxima_anticipacion = maxA_result
    
    #IndicadoresPerformance('TotalSetup')=sum((j,jj,m), changeover(j,jj)*x.l(j,jj,m));
    TotalSetup = 0 
    for m in maquinas:
        for j in ots:
            for jj in ots:
                if (j, m) in asignacion.items():
                    if (jj, m) in asignacion.items() and (j!=jj):
                        TotalSetup = TotalSetup + changeover[(j, jj)] * x[(j, jj, m)] 
    total_setup = TotalSetup

    #IndicadoresPerformance('TotalProduccion')=sum((j), proc(j));
    total_produccion = sum(proc[j] for j in ots)

    #EstadoOrdenes('OrdenesTardias')= nbd.l/card(j);
    ordenes_tardias = NbD.solution_value()/len(ots)

    #EstadoOrdenes('OrdenesAnticipadas')=(card(j)-nbd.l)/card(j);
    ordenes_anticipadas = (len(ots)-NbD.solution_value())/len(ots)

    #uso_operarios_total (tiempo_prod_total= sum((j,o), tiempo_productivo(j,o));)
    tiempo_productivo = {}
    for j in ots:
        for o in operarios:
            zl = z[j,o].solution_value()
            tiempo_productivo[j,o] = proc[j]*zl + sum(changeover[j,jj
                                        ]*x2[(j, jj, o)
                                        ].solution_value() for jj in ots if jj!=j)
    
    tiempo_prod_total = sum(tiempo_productivo[j, o] for (j, o) in tiempo_productivo)
    uso_operarios_total = tiempo_prod_total

    #productividad_operarios (Productividad = tiempo_prod_total/(card(o)* mk.l);)
    productividad_operarios = tiempo_prod_total/(len(operarios)* max_TF)

    #formato = '%d/%m/%Y %H:%M'
    agenda_maquina_ot = []
    agenda_personal = []
    for i in lista_id:
            #if (TF[j,m].solution_value() > 0):
            fecha_inicio = fecha_inicio_plan + timedelta(hours=TF[i['ot'],i['maquina']].solution_value() - proc[i['ot']])  # noqa
            fecha_fin = fecha_inicio_plan + timedelta(hours=TF[i['ot'],i['maquina']].solution_value())
            agenda_maquina_ot.append(
                AgendaMaquinaOt(id = i['id'],
                                ot_nro = i['ot'],
                                maquina_nro = i['maquina'],
                                hora_inicio = fecha_inicio,
                                hora_fin = fecha_fin,
                                cant_personal = operarios_requeridos[i['ot']]))
            agenda_personal.append(
                AgendaPersonal(id = i['id'],
                               cant_personal = operarios_requeridos[i['ot']],
                               hora_inicio = fecha_inicio,
                               hora_fin = fecha_fin))

    model_output = ModelOutput(
        completamiento_ordenes = completamiento_ordenes,
        tardanza_total = tardanza_total,
        anticipacion_total = anticipacion_total,
        maxima_tardanza = maxima_tardanza,
        maxima_anticipacion = maxima_anticipacion,
        total_setup = total_setup,
        total_produccion = total_produccion,
        ordenes_tardias = ordenes_tardias,
        ordenes_anticipadas = ordenes_anticipadas,
        uso_operarios_total = uso_operarios_total,
        productividad_operarios = productividad_operarios,
        agenda_maquina_ot = agenda_maquina_ot,
        agenda_personal = agenda_personal,
    )
    print('===> Model output')
    # print(model_output)

    return model_output


def _validate_and_fix(model_input: ModelInput) -> ModelInput:
    """validate and fix data"""
    # delete fuera servicios of maquinas no incluidas en OTs
    unique_otsmaquinas = []
    for ot in model_input.ots:
        if ot.maquina_nro not in unique_otsmaquinas:
            unique_otsmaquinas.append(ot.maquina_nro)
    model_input.fuera_servicios = [obj for obj in model_input.fuera_servicios if obj.maquina in unique_otsmaquinas]

    return model_input
