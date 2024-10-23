# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 07:29:45 2023

@author: jiramello84
"""

from datetime import datetime, timedelta

fecha_inicio_plan = datetime.strptime('19/12/2022 08:00', '%d/%m/%Y %H:%M')

model_input = {
        'tiempo_setup': 0.5,
        'cantidad_operarios': 3,
        'ots': [
            {'id': 1, 
             'ot_nro': "24597",
             'maquina_nro': "24",
             'producto_id': "7020310",
             'producto_desc': "BID T64 20 ECO-BIDON",
             'maquina_desc': "COEX-23 - SOPLADORA COEXTRUSORA KONG KEE",
             'color': "Blanco",
             'peso': 1050.0,
             'cantidad': 5760,
             'horas': 34.9,
             'fecha_vencimiento': datetime.strptime('19/12/2022', '%d/%m/%Y'),
             'cadencia': 165,
             'operarios_requeridos': 1,
             'prioridad': 3},
            {'id': 2, 
             'ot_nro': "24599",
             'maquina_nro': "23",
             'producto_id': "7020310",
             'producto_desc': "BID T64 20 ECO-BIDON",
             'maquina_desc': "COEX-23 - SOPLADORA COEXTRUSORA KONG KEE",
             'color': "Blanco",
             'peso': 1050.0,
             'cantidad': 5760,
             'horas': 12,
             'fecha_vencimiento': datetime.strptime('19/12/2022', '%d/%m/%Y'),
             'cadencia': 165,
             'operarios_requeridos': 1,
             'prioridad': 2},
            {'id': 3, 
             'ot_nro': "24608",
             'maquina_nro': "23",
             'producto_id': "7020310",
             'producto_desc': "BID T64 20 ECO-BIDON",
             'maquina_desc': "COEX-23 - SOPLADORA COEXTRUSORA KONG KEE",
             'color': "Blanco",
             'peso': 1050.0,
             'cantidad': 5760,
             'horas': 24,
             'fecha_vencimiento': datetime.strptime('19/12/2022', '%d/%m/%Y'),
             'cadencia': 165,
             'operarios_requeridos': 2,
             'prioridad': 1},
        ],
        'fuera_servicios': [
            {'id': 1,
             'maquina': "23",
             'hora_inicio': datetime.strptime('19/12/2022 10:00', '%d/%m/%Y %H:%M'),
             'hora_fin': datetime.strptime('19/12/2022 16:00', '%d/%m/%Y %H:%M'),
            },
        ]
    }

# Generar lista de diccionarios con la clave 'ots'
lista_id = [{'id': entry['id'], 'ot': entry['ot_nro'], 'maquina': entry['maquina_nro']
             } for entry in model_input['ots']]

#def function_model(model_input):
from datetime import datetime, timedelta
from ortools.linear_solver import pywraplp


###############################################################################
###############################################################################
# Lectura model_input

#SETS
# operarios
operarios = []
for i in range(model_input['cantidad_operarios']):
    operarios.append('o{}'.format(str(i+1))) 

# ordenes de trabajo
ots = [ot['ot_nro'] for ot in model_input['ots']]

# máquinas
maquinas = list(set(ot['maquina_nro'] for ot in model_input['ots']))

# máquinas fuera de servicio
fuera_servicios = list(set(item['maquina'] for item in model_input['fuera_servicios']))


#PARÁMETROS

#operarios requeridos x ot
operarios_requeridos = {ot['ot_nro']: ot['operarios_requeridos'] for ot in model_input['ots']}    

#asignación ot-máquina
asignacion = {ot['ot_nro']: ot['maquina_nro'] for ot in model_input['ots']}

#prioridad ot
prioridad = {ot['ot_nro']: ot['prioridad'] for ot in model_input['ots']}

#tiempo ot
proc = {ot['ot_nro']: ot['horas'] for ot in model_input['ots']}

#fecha entrega ot
fecha_vencimiento = {ot['ot_nro']: ot['fecha_vencimiento'] for ot in model_input['ots']}
# Función para encontrar el primer día de la semana
def primer_dia_semana(fecha):
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    return inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
#fecha entrega ot en horas
fecha_entrega = {ot_nro: (fecha - primer_dia_semana(fecha)).total_seconds() / 3600 + 24 for ot_nro, fecha in fecha_vencimiento.items()}

#tiempos inicio y fin de fuera de máquinas fuera de servicio
tiinactiva = {}
tfinactiva = {}
#Procesa los datos de 'fuera_servicios'
for item in model_input['fuera_servicios']:
    maquina = item['maquina']
    hora_inicio = item['hora_inicio']
    hora_fin = item['hora_fin']
    diferencia_horas = (hora_inicio - primer_dia_semana(hora_inicio)
                        ).total_seconds() / 3600 + 24
    tiinactiva[maquina] = float(diferencia_horas)
    
    diferencia_horas = (hora_fin - primer_dia_semana(hora_fin)
                        ).total_seconds() / 3600 + 24
    tfinactiva[maquina] = float(diferencia_horas)
    
    

#changeover
changeover = {(ot1, ot2): model_input['tiempo_setup'] if ot1 != ot2 else 
              0.0 for ot1 in ots for ot2 in ots}

# BigM
#bigM=90
bigM =  2 * (sum(changeover[(j, jj)] for j, jj in changeover) + sum(proc[j] for j in proc))
# Valor máxima prioridad
MaximaPrioridad = max(prioridad.values())

###############################################################################
###############################################################################
# Construcción modelo

#SOLVER
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
    ordenmaquina[(j, m)] = 1 + sum(xgral[j, jj] for jj in ots if (jj, m) in asignacion.items()
                                       and (j!=jj))

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
    AsigOper[j] = solver.Add(sum(z[(j,o)] for o in operarios) == operarios_requeridos[j]
                             ,name=f'AsigOper_{j}')

# FirstJobOP(O) .. SUM(j, W(J,O)) =e= 1;
FirstJobOP = {}
for o in operarios:
    FirstJobOP[o] = solver.Add(solver.Sum([w[(j, o)] for j in ots]) == 1
                               ,name=f'FirstJobOP_{o}')

#FirstIntermJobOP(jj,O) ..
#W(jj,O)+ SUM[j $(NOT SAMEAS(j,jj)), X2(j,jj,O)] =e= z(jj,o);
FirstIntermJobOP = {}
for jj in ots:
    for o in operarios:
        FirstIntermJobOP[(jj,o)] = solver.Add(w[(jj,o)] + sum(x2[(j,jj,o)] for j in ots if j != jj
                                                              ) == z[(jj,o)]
                   , name=f'FirstIntermJobOP_{jj}_{o}')

#PredecOP(jj,O) .. SUM[j $(NOT SAMEAS(j,jj)), X2(j,jj,O)] =l= z(jj,o) ;
PredecOP = {}
for o in operarios:
    for jj in ots:
        PredecOP[(jj,o)]=solver.Add(sum(x2[j,jj,o] for j in ots if j != jj) <= z[(jj,o)]
                                    , name=f'PredecOP_{jj}_{o}')


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
                tiempoFinOP[(j,jj,o)] = solver.Add(TFo[jj, o] >= TFo[j, o] + proc[jj] + changeover[j, jj
                ] - (1 - x2[j, jj, o]) * bigM, name=f'tiempoFinOP_{j}_{jj}_{o}')

# tiempoFinFirstJobOP(j,O).. TFo(j,O) =g= proc(j)*w(j,O);
tiempoFinFirstJobOP = {}
for j in ots:
    for o in operarios:
        tiempoFinFirstJobOP[(j,o)] = solver.Add(TFo[j, o] >= proc[j] * w[(j, o)], name=f'tiempoFinFirstJobOP_{j}_{o}')

#tfoUB(j,o).. TFo(j,o) =l= BigM * z(j,o);
TFoUB = {}
for j in ots:
    for o in operarios:
        TFoUB[(j,o)]  =solver.Add(TFo[j, o] <= bigM * z[j, o]
                                  ,name=f'TFoUB_{j}_{o}')

#AsigFirst(j,o)..  W(J,O)=l= z(j,o);
AsigFirst = {}
for j in ots:
    for o in operarios:
        AsigFirst[(j,o)] = solver.Add(w[(j,o)] <= z[(j, o)],
                                      name=f'AsigFirst_{j}_{o}')


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
            Log4[(j,m,o)] = solver.Add(zy[j, m, o] == 0, name=f'Log4_{j}_{m}_{o}'
                                       )
# Log5(j,m)$Asignacion(j,m).. sum(o,zy(j,m,o)) =e= operarios(j);
Log5 = {}
for j,m in asignacion.items():
        Log5[(j,m)] = solver.Add(sum(zy[(j, m, o)] for o in operarios) == operarios_requeridos[j]
                   , name=f'Log5_{j}_{m}')

# IgualTF1(j,m,o)$Asignacion(j,m).. tf(j,m) =g= tfo(j,o) - bigm * (1- zy(j,m,o));
IgualTF1 ={}
for j, m in asignacion.items():
    for o in operarios:
        IgualTF1[(j,m,o)] = solver.Add(TF[(j, m)] >= TFo[(j,o)] - bigM * (1-zy[(j, m, o)])
                   ,name='IgualTF1_{j}_{m}_{o}')

# IgualTF2(j,m,o)$Asignacion(j,m).. tf(j,m) =l= tfo(j,o) + bigm * (1- zy(j,m,o));
IgualTF2 = {} 
for j, m in asignacion.items():
    for o in operarios:
        IgualTF2[(j,m,o)] = solver.Add(TF[(j, m)] <= TFo[(j,o)] + bigM * (1-zy[(j, m, o)])
                     ,name='IgualTF2_{j}_{m}_{o}')

# FirstJob(m) .. SUM(j$Asignacion(j,m), Y(j,m)) =e= 1;
FirstJob = {}
for m in maquinas:
    FirstJob[(m)] = solver.Add(sum(y[(j, m)] for j in ots if (j, m) in asignacion.items()) == 1)


# FirstIntermJob(jj,m)$Asignacion(jj,m) ..
# Y(jj,m)+ SUM[j $(Asignacion(j,m) and(NOT SAMEAS(j,jj))), X(j,jj,m)] =e= 1;
FirstIntermJob = {}
for (jj, m) in asignacion.items():
    FirstIntermJob[(jj,m)] = solver.Add(y[(jj,m)] + sum(x[(j,jj,m)] for (j,m) in
                                                    filter(lambda jm: jm[1]==m and jm[0]!=jj
                                                          , asignacion.items())) == 1)

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

#tiempofin2(j,jj,m)$(Asignacion(j,m) and Asignacion(jj,m) and (NOT SAMEAS(j,jj)))
#.. TF(jj,m) =l= TF(j,m)+proc(jj)+ changeover(j,jj)+(1-X.l(j,jj,m))*bigM ;
#tiempofin2 = {}
#for j, m in asignacion.items():
#    for jj, mm in asignacion.items():
#        if m==mm and j != jj:
#            tiempofin2[(j,jj,m)] = solver.Add(TF[jj, m] <= TF[j, m] + proc[jj] + changeover[j, jj
#                                            ] + (1 - x[(j, jj, m)]) * bigM)

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

#tardanza(j,m)$Asignacion(j,m).. Tard(j,m)=g=TF(j,m)-dd(j);
tardanza = {}
for j, m in asignacion.items():
    tardanza[(j,m)] = solver.Add(Tard[j, m] >= TF[j, m] - fecha_entrega[j], name='tardanza_{j}_{m}')

# tardanzaTotal..   TT=g=sum((j,m)$Asignacion(j,m),Tard(j,m))  ;
solver.Add(TT >= solver.Sum(Tard[j, m] for j, m in asignacion.items())
           , name='tardanzaTotal')

# anticipacion(j,m)$Asignacion(j,m).. Earl(j,m)=g= dd(j)-TF(j,m);
anticipacion = {}
for j, m in asignacion.items():
    anticipacion[(j,m)] = solver.Add(Earl[(j,m)] >= fecha_entrega[j] - TF[(j,m)]
               , name='anticipacion_{j}_{m}')

# anticipacionTotal.. TE=g= sum((j,m)$Asignacion(j,m),Earl(j,m));
solver.Add(TE >= solver.Sum(Earl[(j,m)
                ] for j, m in asignacion.items()))

# ordenTardia(j,m)$Asignacion(j,m)..  (TF(j,m)-dd(j)) - D(j,m)* bigM =l= 0;
ordenTardia = {}
for j,m in asignacion.items():
    ordenTardia[(j,m)] = solver.Add((TF[(j,m)]-fecha_entrega[j]) - D[(j,m)] * bigM <= 0
               , name='ordenTardia_{j}_{m})')

# ordenTardia2(j,m)$Asignacion(j,m).. (TF(j,m)-dd(j))  =g= - bigM*(1-d(j,m));
ordenTardia2 = {}
for j,m in asignacion.items():
    ordenTardia2[(j,m)] = solver.Add((TF[(j,m)]-fecha_entrega[j]) >= - bigM*(1-D[(j,m)])
               , name='ordenTardia_{j}_{m})')

# numTotalTard..    NbD =g=sum((j,m)$Asignacion(j,m),D(j,m));
solver.Add(NbD >= solver.Sum(D[(j,m)] for j, m in asignacion.items()), name='numTotalTard')

#maxTard(j,m)$Asignacion(j,m)..  maxT =g= Tard(j,m);
maxTard = {}
for j, m in asignacion.items():
    maxTard[(j,m)] = solver.Add(maxT >= Tard[(j,m)])

# maxAntic(j,m)$Asignacion(j,m).. maxA =g= Earl(j,m);
maxAntic = {}
for j, m in asignacion.items():
    maxAntic[(j,m)] = solver.Add(maxA >= Earl[(j,m)])


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
status = solver.Solve(solverParams)


if status == pywraplp.Solver.OPTIMAL:
    print("Solución óptima")
    print('Objective value =', solver.Objective().Value())
    print(prioOF.name(),'=', prioOF.solution_value())
    print('relative gap (%):', (solver.Objective().Value()-solver.Objective(
          ).BestBound())/solver.Objective().BestBound()*100)
    print()
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
   
elif status == pywraplp.Solver.FEASIBLE:
    print("Solución factible")
    print('Objective value =', solver.Objective().Value())
    print(prioOF.name(),'=', prioOF.solution_value())
    print('relative gap (%):', (solver.Objective().Value
                                ()-solver.Objective(
          ).BestBound())/solver.Objective().BestBound()*100)
    print()
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
elif status == pywraplp.Solver.INFEASIBLE:
    print('El problema es infactible')
    print('Objective value =', solver.Objective().Value())
    print(prioOF.name(),'=', prioOF.solution_value())
    print('relative gap (%):', (solver.Objective().Value()-solver.Objective(
          ).BestBound())/solver.Objective().BestBound()*100)
    print()
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

###############################################################################
###############################################################################
# model output

model_output = {}

# IndicadoresPerformance('CompletamientoOrdenes')= Mk.l;
tiempo_fin = {}
max_TF = 0
for j,m in asignacion.items():
        if (TF[j,m].solution_value() > 0):
            tiempo_fin[j,m] = TF[j,m].solution_value()
            max_TF = max(max_TF,tiempo_fin[j,m])
model_output['completamiento_ordenes'] = max_TF

#IndicadoresPerformance('TardanzaTotal')= tt.l;
model_output['tardanza_total'] = TT.solution_value()

#IndicadoresPerformance('AnticipacionTotal')= te.l  ;
model_output['anticipacion_total'] = TE.solution_value()

#IndicadoresPerformance('MaximaTardanza')= maxT.l ;
maxT_result = 0
for j in ots:
    for m in maquinas:
        maxT_result = max(maxT_result,Tard[(j,m)].solution_value())
model_output['maxima_tardanza'] = maxT_result

#IndicadoresPerformance('MaximaAnticipacion')=maxA.l;
maxA_result = 0
for j in ots:
    for m in maquinas:
        maxA_result = max(maxA_result,Earl[(j,m)].solution_value())
model_output['maxima_anticipacion'] = maxA_result

#IndicadoresPerformance('TotalSetup')=sum((j,jj,m), changeover(j,jj)*x.l(j,jj,m));
TotalSetup = 0
for m in maquinas:
    for j in ots:
        for jj in ots:
            if (j, m) in asignacion.items():
                if (jj, m) in asignacion.items() and (j!=jj):
                    TotalSetup = TotalSetup + changeover[(j, jj)] * x[(j, jj, m)]
model_output['total_setup'] = TotalSetup

#IndicadoresPerformance('TotalProduccion')=sum((j), proc(j));
model_output['total_produccion'] = sum(proc[j] for j in ots)

#EstadoOrdenes('OrdenesTardias')= nbd.l/card(j);
model_output['ordenes_tardias'] = NbD.solution_value()/len(ots)

#EstadoOrdenes('OrdenesAnticipadas')=(card(j)-nbd.l)/card(j);
model_output['ordenes_anticipadas'] = (len(ots)-NbD.solution_value())/len(ots)

#uso_operarios_total (tiempo_prod_total= sum((j,o), tiempo_productivo(j,o));)
tiempo_productivo = {}
for j in ots:
    for o in operarios:
        zl = z[j,o].solution_value()
        tiempo_productivo[j,o] = proc[j]*zl + sum(changeover[j,jj
                                    ]*x2[(j, jj, o)
                                     ].solution_value() for jj in ots if jj!=j)
 
tiempo_prod_total = sum(tiempo_productivo[j, o] for (j, o) in tiempo_productivo)
model_output['uso_operarios_total'] = tiempo_prod_total

#productividad_operarios (Productividad = tiempo_prod_total/(card(o)* mk.l);)
Productividad = tiempo_prod_total/(len(operarios)* max_TF) ;
model_output['productividad_operarios'] = Productividad

formato = '%d/%m/%Y %H:%M'
agenda_maquina_ot = []
agenda_personal = []
for i in lista_id:
        #if (TF[j,m].solution_value() > 0):
        fecha_inicio = fecha_inicio_plan + timedelta(hours=TF[i['ot'],i['maquina']
                                        ].solution_value() - proc[i['ot']])
        fecha_fin = fecha_inicio_plan + timedelta(hours=TF[i['ot'],i['maquina']].solution_value())
        agenda_maquina_ot.append({
                'id': i['id'],
                'ot_nro': i['ot'],
                'maquina_nro': i['maquina'],
                'hora_inicio': fecha_inicio.strftime(formato),
                'hora_fin': fecha_fin.strftime(formato)
                })
        agenda_personal.append({
                'id': i['id'],
                'cant_personal': operarios_requeridos[i['ot']],
                'hora_inicio': fecha_inicio.strftime(formato),
                'hora_fin': fecha_fin.strftime(formato)})

model_output['agenda_maquina_ot'] = agenda_maquina_ot
model_output['agenda_personal'] = agenda_personal
print('===> Model output')
print(model_output)
