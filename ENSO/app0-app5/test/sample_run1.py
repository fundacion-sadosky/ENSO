# -*- coding: utf-8 -*-
"""
27/6/2023
@author: jiramello84

Modelo que contempla multiples maquinas
Cada OT se preasigna a la maquina donde debe ser procesada
Se conoce el requerimiento de operarios de cada OT
Es posible asignar un tiempo (momento de inicio y fin) que una maquina
esta fuera de servicio
Se asignan prioridades a las OT
Se respetan las prioridades dentro de una misma maquina
Se optimiza el ordenamiento de OT de acuerdo a las prioridades establecidas

En este ejemplo se consideran 5 maquinas, 15 ordenes y 3 operarios
La maquina m5 esta fuera de servicio desde la hora 60 hasta la 70
Las prioridades de las OT se indican crecientes de acuerdo a su numero,
es decir, la OT1 es la mas prioritaria y la OT15 es la menos prioritaria
"""

#Importamos librerías
import pandas as pd
from ortools.linear_solver import pywraplp


# Sets
jobs = ['j1', 'j2', 'j3', 'j4', 'j5', 'j6', 'j7', 'j8', 'j9', 'j10', 'j11', 'j12',
        'j13', 'j14', 'j15']
ope = ['o1', 'o2', 'o3']
maq = ['m1', 'm2', 'm3', 'm4', 'm5']

asignacion = {'j1': 'm1', 'j2': 'm1', 'j3': 'm2', 'j4': 'm2', 'j5': 'm2',
              'j6': 'm3', 'j7': 'm3', 'j8': 'm3', 'j9': 'm3', 
              'j10': 'm4', 'j11': 'm4', 'j12': 'm4', 
              'j13': 'm5', 'j14': 'm5', 'j15': 'm5'}

fueraservicio = ['m5']

# Parameters
operarios = {'j1': 2, 'j2': 1, 'j3': 2, 'j4': 1, 'j5': 1, 'j6': 2, 'j7': 1, 'j8': 2,
             'j9': 1, 'j10': 1, 'j11': 2,'j12': 1, 'j13': 2, 'j14': 1, 'j15': 1}

prioridad = {'j1': 1, 'j2': 2, 'j3': 3, 'j4': 4, 'j5': 5, 'j6': 6, 'j7': 7, 'j8': 8, 'j9': 9, 'j10': 10, 'j11': 11,
             'j12': 12, 'j13': 13, 'j14': 14, 'j15': 15}



proc = {'j1': 10, 'j2': 9, 'j3': 8, 'j4': 10, 'j5': 7, 'j6': 6, 'j7': 7, 'j8': 8, 'j9': 9, 'j10': 10, 'j11': 11,
        'j12': 10, 'j13': 10, 'j14': 12, 'j15': 10}

tiinactiva = {'m5': 60}
tfinactiva = {'m5': 70}

dd = {'j1': 9, 'j2': 57, 'j3': 27, 'j4': 41, 'j5': 34, 'j6': 46, 'j7': 47, 'j8': 38, 'j9': 19, 'j10': 10, 'j11': 11,
      'j12': 20, 'j13': 33, 'j14': 44, 'j15': 15}

MaximaPrioridad = max(prioridad.values())

changeover = {(j1, j2): 0.5 if j1 != j2 else 0.0 for j1 in jobs for j2 in jobs}

# BigM
bigM=300

# Parámetro primerOT
primerOT = {}
for m in maq:
    for j in jobs:
        if (j, m) in asignacion.items():
            if prioridad[j] == min(prioridad[jj] for jj in jobs if (jj, m) in asignacion.items()):
                primerOT[(j, m)] = 1
            else:
                primerOT[(j, m)] = 0


# Definimos el solver
solver = pywraplp.Solver.CreateSolver('SCIP')


# Definimos variables
prioOF = solver.IntVar(0, solver.infinity(), 'prioOF')
y = {}
x = {}
x2 = {}
TF = {}
Tard = {}
Earl = {}
TFo = {}
zy = {}

for j in jobs:
    for m in maq:
        #y[(j, m)] = solver.IntVar(0, 1, f'y_{j}_{m}')
        TF[(j, m)] = solver.NumVar(0, solver.infinity(), f'TF_{j}_{m}')
        Tard[(j, m)] = solver.NumVar(0, solver.infinity(), f'Tard_{j}_{m}')
        Earl[(j, m)] = solver.NumVar(0, solver.infinity(), f'Earl_{j}_{m}')
        #for jj in jobs:
        #    if j != jj and (j,m) in asignacion.items() and (jj,m) in asignacion.items():
                #x[(j, jj, m)] = solver.IntVar(0,1,f'x_{j}_{jj}_{m}')
        for o in ope:
            zy[(j,m,o)] = solver.IntVar(0,1,f'zy_{j}_{m}_{o}')

#x2
for j in jobs:
    for jj in jobs:#range(num_jobs):
        if j != jj:        
            for o in ope:
                x2[(j, jj, o)] = solver.IntVar(0,1,f'x2_{j}_{jj}_{o}')

# TFo variables
TFo = {}
for j in jobs:
    for o in ope:
        TFo[j, o] = solver.NumVar(0, solver.infinity(), f'TFo{j},{o}')

# Xgral(j,jj)
xgral = {}
#for j in jobs:
#    for jj in jobs:
#        if (j!=jj):
#            xgral[j,jj] = solver.IntVar(0, 1, 'xgral[{},{}]'.format(j,jj))            
for m in maq:
    for j in jobs:
        if (j, m) in asignacion.items():
            for jj in jobs:
                if jj != j and (jj,m) in asignacion.items():
                    if prioridad[j] < prioridad[jj]:
                        #solver.Add(xgral[j,jj]==1)
                        #xgral[j,jj].SetSolutionValue(1)
                        xgral[j,jj] = 1
                    else:
                        #solver.Add(xgral[j,jj]==0)
                        #xgral[j,jj].SetSolutionValue(0)
                        xgral[j,jj]=0
            
# z(j,o)
z = {}
for j in jobs:
    for o in ope:
        z[j,o] = solver.IntVar(0, 1, 'z[{},{}]'.format(j,o))

# w(j,o)
w = {}
for j in jobs:
    for o in ope:
        w[j,o] = solver.IntVar(0, 1, 'w[{},{}]'.format(j,o))

#Yanterior(j)
Yanterior = {}
for j in jobs:
    Yanterior[j] = solver.IntVar(0, 1, 'w[{}]'.format(j))

#OrdenMaquina(j,m)$asignacion(j,m)= 1+ sum(jj$asignacion(jj,m), xgral.l(j,jj))
ordenmaquina = {}
for j, m in asignacion.items():
        ordenmaquina[(j, m)] = 1 + sum(xgral[j, jj] for jj in jobs if (jj, m) in asignacion.items()
                                       and (j!=jj))

#x(j,jj,m) es variable fija en este modelo
for m in maq:
    for j in jobs:
        for jj in jobs:
            if (j, m) in asignacion.items():
                if (jj, m) in asignacion.items() and (j!=jj):
                    if ordenmaquina[j, m] == ordenmaquina[jj, m] + 1:
                        x[j, jj, m] = 1
                    else:
                        x[j, jj, m] = 0
                        
            
for j in jobs:
    for m in maq:
        if (j,m) in primerOT:
            y[(j,m)] = primerOT[(j,m)]
        else:
            y[(j,m)] = 0


# Makespam 1 y 2 y Tardanza Total        
Mk  = solver.NumVar(-solver.infinity(), solver.infinity(), 'Mk')
Mk2 = solver.NumVar(-solver.infinity(), solver.infinity(), 'Mk2')
TT  = solver.NumVar(-solver.infinity(), solver.infinity(), 'TT')
prioOF = solver.NumVar(-solver.infinity(), solver.infinity(), 'piorFO')
# Orden Tardía 
D = {}
for j in jobs:
    for m in maq:
        D[(j, m)] = solver.IntVar(0,1,f'D_{j}_{m}')
# Otras variables
maxT = solver.NumVar(-solver.infinity(), solver.infinity(), 'maxT')
maxA = solver.NumVar(-solver.infinity(), solver.infinity(), 'maxA')
NbD  = solver.NumVar(-solver.infinity(), solver.infinity(), 'NbD')
TE   = solver.NumVar(-solver.infinity(), solver.infinity(), 'TE')



# Definimos restricciones (CONSTRAINTS)
#########################################################################################
#AsigOper(j).. sum(o,z(j,o))=e=operarios(j); 
AsigOper = {}  
for j in jobs:
    # restricción de asignación de operarios
    AsigOper[j] = solver.Add(sum(z[(j,o)] for o in ope) == operarios[j]
                             ,name=f'AsigOper_{j}')

# FirstJobOP(O) .. SUM(j, W(J,O)) =e= 1;
FirstJobOP = {}
for o in ope:
    FirstJobOP[o] = solver.Add(solver.Sum([w[(j, o)] for j in jobs]) == 1
                               ,name=f'FirstJobOP_{o}')

#FirstIntermJobOP(jj,O) ..  
#W(jj,O)+ SUM[j $(NOT SAMEAS(j,jj)), X2(j,jj,O)] =e= z(jj,o);  
FirstIntermJobOP = {}
for jj in jobs:
    for o in ope:
        # restricción FirstIntermJobOP
        FirstIntermJobOP[(jj,o)] = solver.Add(w[(jj,o)] + sum(x2[(j,jj,o)] for j in jobs if j != jj) == z[(jj,o)]
                   , name=f'FirstIntermJobOP_{jj}_{o}')

# PredecOP(jj,O) .. SUM[j $(NOT SAMEAS(j,jj)), X2(j,jj,O)] =l= z(jj,o) ;
PredecOP = {}
for o in ope:
    for jj in jobs:
        PredecOP[(jj,o)]=solver.Add(sum(x2[j,jj,o] for j in jobs if j != jj) <= z[(jj,o)]
                                    , name=f'PredecOP_{jj}_{o}')

# SucesOP(j,O) .. SUM[jj $(NOT SAMEAS(j,jj)), X2(j,jj,O)] =l= z(j,o) ;
SucesOP = {}
for o in ope:
    for j in jobs:
        SucesOP[(j,o)] = solver.Add(sum(x2[(j,jj,o)] for jj in jobs if j!=jj) <= z[(j,o)], 
                   name=f'SucesOP_{j}_{o}')

#TFoUB(j,o)
TFoUB = {}
for j in jobs:
    for o in ope:
        TFoUB[(j,o)]=solver.Add(TFo[j, o] <= bigM * z[j, o])

#tiempoFinOP(j,jj,O)$(NOT SAMEAS(j,jj)).. TFo(jj,O) =g= TFo(j,O)+proc(jj)
#                                 + changeover(j,jj)-(1-X2(j,jj,O))*bigM ; 
tiempoFinOP = {}
for jj in jobs:
    for j in jobs:
        if j != jj:
            for o in ope:
                tiempoFinOP[(j,jj,o)] = solver.Add(TFo[jj, o] >= TFo[j, o] + proc[jj] + changeover[j, jj
                ] - (1 - x2[j, jj, o]) * bigM, name=f'tiempoFinOP_{j}_{jj}_{o}')

# tiempoFinFirstJobOP(j,O).. TFo(j,O) =g= proc(j)*w(j,O);
tiempoFinFirstJobOP = {}
for j in jobs:
    for o in ope:
        tiempoFinFirstJobOP[(j,o)] = solver.Add(TFo[j, o] >= proc[j] * w[(j, o)], name=f'tiempoFinFirstJobOP_{j}_{o}')

# AsigFirst(j,o)..  W(J,O)=l= z(j,o);

AsigFirst = {}
for j in jobs:
    for o in ope:
        AsigFirst[(j,o)] = solver.Add(w[(j,o)] <= z[(j, o)], name=f'AsigFirst_{j}_{o}')

# Log1(j,m,o)$Asignacion(j,m).. zy(j,m,o) =e= z(j,o) ; 
Log1 = {}
for j,m in asignacion.items():
    for o in ope:
        # restricción de equivalencia de variables
        Log1[(j,m,o)] = solver.Add(zy[(j,m,o)] == z[(j,o)], name=f'Log1_{j}_{m}_{o}' )

# Log4(j,m,o)$(not Asignacion(j,m)).. zy(j,m,o) =e= 0  ;
Log4 = {}
for j in jobs:
    for m in maq:
        if (j, m) not in asignacion.items():
            Log4[(j,m,o)] = solver.Add(zy[j, m, o] == 0, name=f'Log4_{j}_{m}_{o}'
                                       )
# Log5(j,m)$Asignacion(j,m).. sum(o,zy(j,m,o)) =e= operarios(j);
Log5 = {}
for j,m in asignacion.items():
        Log5[(j,m)] = solver.Add(sum(zy[(j, m, o)] for o in ope) == operarios[j]
                   , name=f'Log5_{j}_{m}')

# IgualTF1(j,m,o)$Asignacion(j,m).. tf(j,m) =g= tfo(j,o) - bigm * (1- zy(j,m,o));
IgualTF1 ={}
for j, m in asignacion.items():
    for o in ope:
        IgualTF1[(j,m,o)] = solver.Add(TF[(j, m)] >= TFo[(j,o)] - bigM * (1-zy[(j, m, o)])
                   ,name='IgualTF1_{j}_{m}_{o}')
   
# IgualTF2(j,m,o)$Asignacion(j,m).. tf(j,m) =l= tfo(j,o) + bigm * (1- zy(j,m,o)); 
IgualTF2 = {} 
for j, m in asignacion.items():
    for o in ope:
        IgualTF2[(j,m,o)] = solver.Add(TF[(j, m)] <= TFo[(j,o)] + bigM * (1-zy[(j, m, o)])
                     ,name='IgualTF2_{j}_{m}_{o}')
    
# FirstJob(m) .. SUM(j$Asignacion(j,m), Y(j,m)) =e= 1;
FirstJob = {}
for m in maq:
    FirstJob[(m)] = solver.Add(sum(y[(j, m)] for j in jobs if (j, m) in asignacion.items()) == 1)  
   
# FirstIntermJob(jj,m)$Asignacion(jj,m) ..  
# Y(jj,m)+ SUM[j $(Asignacion(j,m) and(NOT SAMEAS(j,jj))), X(j,jj,m)] =e= 1;
FirstIntermJob = {}
for (jj, m) in asignacion.items():
    FirstIntermJob[(jj,m)] = solver.Add(y[(jj,m)] + sum(x[(j,jj,m)] for (j,m) in 
                                                    filter(lambda jm: jm[1]==m and jm[0]!=jj,
                                                       asignacion.items())) == 1)  
    
#Predec(jj,m)$Asignacion(jj,m) .. 
# SUM[j $(Asignacion(j,m) and (NOT SAMEAS(j,jj))),X(j,jj,m)] =l= 1 ;   
Predec = {}
for jj, m in asignacion.items():
    Predec[(jj,m)] = solver.Add(sum(x[(j,jj,m) 
                    ] for (j,m) in filter(lambda jm: jm[1]==m and jm[0]!=jj,asignacion.items())) <= 1)    
#Suces(j,m)$Asignacion(j,m) .. 
# SUM[jj $(Asignacion(jj,m) and(NOT SAMEAS(j,jj))), X(j,jj,m)] =l= 1 ;     
Suces = {}
for j, m in asignacion.items():
    Suces[(j,m)] = solver.Add(sum(x[(j,jj,m) 
                    ] for (jj,m) in filter(lambda jm: jm[1]==m and jm[0]!=j,asignacion.items())) <= 1)    
    
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
tiempofin2 = {}
for j, m in asignacion.items():
    for jj, mm in asignacion.items():
        if m==mm and j != jj:
            tiempofin2[(j,jj,m)] = solver.Add(TF[jj, m] <= TF[j, m] + proc[jj] + changeover[j, jj
                                            ] + (1 - x[(j, jj, m)]) * bigM)

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
    if m in fueraservicio:
        maqFS1[(j,m)] = solver.Add(TF[j, m] <= tiinactiva[m] + bigM * (1 - Yanterior[j]))

#maqFS2(j,m)$(asignacion(j,m) and fueraservicio(m)).. 
#tf(j,m)-proc(j)=g= tfinactiva(m)*(1-Yanterior(j));
maqFS2 = {}
for j, m in asignacion.items():
    if m in fueraservicio:
        maqFS2[(j,m)] = solver.Add(TF[j, m] - proc[j] >= tfinactiva[m] * (1 - Yanterior[j]))
        
#precedenciaGral(j,jj,m)$((Asignacion(j,m)) 
# and (Asignacion(jj,m)) 
# and (ord(j) ne ord(jj)))..
#                 TF(jj,m) =g= TF(j,m)-(1-Xgral(j,jj))*bigM  ;
precedenciaGral = {}
for j, m in asignacion.items():
    for jj, mm in asignacion.items():
        if j != jj and m == mm:
            precedenciaGral[(j,jj,m)] = solver.Add(TF[(jj, m)] >= TF[(j, m)] - (1 - xgral[(j, jj)]) * bigM)

# noasignar(j,m)$(not Asignacion(j,m))..  Y(j,m)=e=0;
noasignar = {}
for j in jobs:
    for m in maq:
        if (j, m) not in asignacion.items():
            noasignar[(j,m)] = solver.Add(y[(j, m)] == 0)
# makespanDef(j,m)$Asignacion(j,m) .. Mk =g= TF(j,m) ;            
for j, m in asignacion.items():
    solver.Add(Mk >= TF[(j, m)], name='makespanDef_{j}_{m}')

# makespanDef2(j,o) .. Mk2 =g= TFo(j,o) ;
for j in jobs:
    for o in ope:
        solver.Add(Mk2 >= TFo[(j, o)], name='makespanDef2_{j}_{o}')

#tardanza(j,m)$Asignacion(j,m).. Tard(j,m)=g=TF(j,m)-dd(j);
tardanza = {}
for j, m in asignacion.items():
    tardanza[(j,m)] = solver.Add(Tard[j, m] >= TF[j, m] - dd[j], name='tardanza_{j}_{m}')

# tardanzaTotal..   TT=g=sum((j,m)$Asignacion(j,m),Tard(j,m))  ;
solver.Add(TT >= solver.Sum(Tard[j, m] for j, m in asignacion.items())
           , name='tardanzaTotal')

# anticipacion(j,m)$Asignacion(j,m).. Earl(j,m)=g= dd(j)-TF(j,m);
for j, m in asignacion.items():
    solver.Add(Earl[(j,m)] >= dd[j] - TF[(j,m)]
               , name='anticipacion_{j}_{m}')
    
# anticipacionTotal.. TE=g= sum((j,m)$Asignacion(j,m),Earl(j,m));
solver.Add(TE >= solver.Sum(Earl[(j,m)
                ] for j, m in asignacion.items()))  
    
# ordenTardia(j,m)$Asignacion(j,m)..  (TF(j,m)-dd(j)) - D(j,m)* bigM =l= 0; 
for j,m in asignacion.items():
    solver.Add((TF[(j,m)]-dd[j]) - D[(j,m)] * bigM <= 0
               , name='ordenTardia_{j}_{m})')

# ordenTardia2(j,m)$Asignacion(j,m).. (TF(j,m)-dd(j))  =g= - bigM*(1-d(j,m));
for j,m in asignacion.items():
    solver.Add((TF[(j,m)]-dd[j]) >= - bigM*(1-D[(j,m)])
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


#minPrioridad.. 
#sum((j,m)$(Asignacion(j,m)), tf(j,m)*(maximaprioridad-prioridad(j)))=e= prioOF;  
# Define the OR-Tools variable
min_prioridad = solver.Sum(TF[(j, m)] * (MaximaPrioridad - prioridad[j]
                                       ) for j, m in asignacion.items())
# Add the constraint to the solver
solver.Add(min_prioridad <= prioOF)
    
 
#Check Constraint Total
print('Number of partial constraints =', solver.NumConstraints())

#Parámetros del Solver
solver.Minimize(prioOF)
solver.set_time_limit(600000)
gap = 0.05
solverParams = pywraplp.MPSolverParameters()
solverParams.SetDoubleParam(solverParams.RELATIVE_MIP_GAP, gap)
status = solver.Solve(solverParams)


if status == pywraplp.Solver.OPTIMAL:
    print("Solución óptima")
    print('Objective value =', solver.Objective().Value()) 
    print(prioOF.name(),'=', prioOF.solution_value())
    print()
    print('Problem solved in %f milliseconds' % solver.wall_time())
    #print("Gap: {}".format(solver.Objective().relative_gap()))
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
elif status == pywraplp.Solver.FEASIBLE:
    print("Solución factible")
    print('Objective value =', solver.Objective().Value()) 
    print(prioOF.name(),'=', prioOF.solution_value())
    print()
    print('Problem solved in %f milliseconds' % solver.wall_time())
    #print("Gap: {}".format(solver.Objective().relative_gap()))
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())         
elif status == pywraplp.Solver.INFEASIBLE:
    print('El problema es infactible')
    print('Objective value =', solver.Objective().Value()) 
    print(prioOF.name(),'=', prioOF.solution_value())
    print()
    print('Problem solved in %f milliseconds' % solver.wall_time())
    #print("Gap: {}".format(solver.Objective().relative_gap()))
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
    
#######################################################################
#Escritura de resultados
# tiempo_inicio(j,m)$(Asignacion(j,m)) = tf.l(j,m)-proc(j);
tiempo_inicio = {}
for j,m in asignacion.items():
        if (TF[j,m].solution_value()>0.00001):
            tiempo_inicio[j,m] = TF[j,m].solution_value() - proc[j]
            #print('Ti',j,m,'=',tiempo_inicio[j,m])
tiempo_fin = {}
max_TF = 0
for j,m in asignacion.items():
        if (TF[j,m].solution_value()>0.00001):
            tiempo_fin[j,m] = TF[j,m].solution_value()
            max_TF = max(max_TF,tiempo_fin[j,m])
    
# tiempo_productivo(j,o)= proc(j)*z.l(j,o)+ sum(jj, changeover(j,jj)*X2.l(j,jj,O));    
tiempo_productivo = {}
for j in jobs:
    for o in ope:
        zl = z[j,o].solution_value()
        tiempo_productivo[j,o] = proc[j]*zl + sum(changeover[j,jj
                                        ]*x2[(j, jj, o)
                                         ].solution_value() for jj in jobs if jj!=j)

#tiempo_prod_total= sum((j,o), tiempo_productivo(j,o)); 
tiempo_prod_total = sum(tiempo_productivo[j, o] for (j, o) in tiempo_productivo)
#Productividad = tiempo_prod_total/(card(o)* mk.l) ;
Productividad = tiempo_prod_total/(len(ope)* max_TF) ;

# IndicadoresPerformance('CompletamientoOrdenes')= Mk.l;
CompletamientoOrdenes = max_TF
#IndicadoresPerformance('TardanzaTotal')= tt.l;
TardanzaTotal = TT.solution_value()
#IndicadoresPerformance('AnticipacionTotal')= te.l  ;
AnticipacionTotal = TE.solution_value()
#IndicadoresPerformance('MaximaTardanza')= maxT.l ;
maxT_result = 0
for j in jobs:
    for m in maq:
        maxT_result = max(maxT_result,Tard[(j,m)].solution_value())
MaximaTardanza = maxT_result
#IndicadoresPerformance('MaximaAnticipacion')=maxA.l;
maxA_result = 0
for j in jobs:
    for m in maq:
        maxA_result = max(maxA_result,Earl[(j,m)].solution_value())
MaximaAnticipacion = maxA_result
#IndicadoresPerformance('TotalSetup')=sum((j,jj,m), changeover(j,jj)*x.l(j,jj,m));
TotalSetup = 0 
for m in maq:
    for j in jobs:
        for jj in jobs:
            if (j, m) in asignacion.items():
                if (jj, m) in asignacion.items() and (j!=jj):
                    TotalSetup = TotalSetup + changeover[(j, jj)] * x[(j, jj, m)]
#IndicadoresPerformance('TotalProduccion')=sum((j), proc(j));
TotalProduccion = sum(proc[j] for j in jobs)
#EstadoOrdenes('OrdenesTardias')= nbd.l/card(j);
OrdenesTardias = NbD.solution_value()/len(jobs);
#EstadoOrdenes('OrdenesAnticipadas')=(card(j)-nbd.l)/card(j);
OrdenesAnticipadas = (len(jobs)-NbD.solution_value())/len(jobs)

#Contrucción archivo salida
indicadores_performance = pd.DataFrame(data= [[CompletamientoOrdenes
                                               ,TardanzaTotal
                                               ,AnticipacionTotal
                                               ,MaximaTardanza
                                               ,MaximaAnticipacion
                                               ,TotalSetup
                                               ,TotalProduccion
                                               ]
                                              ]
                                       ,columns=['CompletamientoOrdenes'
                                                 ,'TardanzaTotal'
                                                 ,'AnicipacionTotal'
                                                 ,'MáximaTardanza'
                                                 ,'MáximaAnticipacion'
                                                 ,'TotalSetup'
                                                 ,'TotalProduccion']
                                       )

estado_ordenes = pd.DataFrame(data= [[ OrdenesTardias
                                      ,OrdenesAnticipadas
                                      ]
                                     ]
                                       ,columns=['OrdenesTardias'
                                                 ,'OrdenesAnticipadas'
                                                 ]
                                       )

#inicio ordenes
inicio_ordenes = pd.DataFrame.from_dict(tiempo_inicio, orient='index')
inicio_ordenes.index = pd.MultiIndex.from_tuples(inicio_ordenes.index, 
                                                 names=['j', 'm'])
inicio_ordenes.columns = ['valor']

inicio_ordenes = inicio_ordenes.reset_index()
inicio_ordenes_pivot = pd.pivot_table(inicio_ordenes,
                                       index=['j'],
                                     columns=['m'], 
                                     values=['valor'],
                                     )
inicio_ordenes_pivot = inicio_ordenes_pivot.reindex(jobs).reset_index()

#fin ordenes
fin_ordenes = pd.DataFrame.from_dict(tiempo_fin, orient='index')
fin_ordenes.index = pd.MultiIndex.from_tuples(fin_ordenes.index, 
                                              names=['j', 'm'])
fin_ordenes.columns = ['valor']

fin_ordenes = fin_ordenes.reset_index()
fin_ordenes_pivot = pd.pivot_table(fin_ordenes,
                                       index=['j'],
                                     columns=['m'], 
                                     values=['valor'],
                                     )
fin_ordenes_pivot = fin_ordenes_pivot.reindex(jobs).reset_index()

#operarios
operarios = pd.DataFrame.from_dict(tiempo_productivo, orient='index')
operarios.index = pd.MultiIndex.from_tuples(operarios.index, 
                                              names=['j', 'm'])
operarios.columns = ['valor']

operarios = operarios.reset_index()
operarios_pivot = pd.pivot_table(operarios,
                                 index=['j'],
                                 columns=['m'], 
                                 values=['valor'],
                                     )
operarios_pivot = operarios_pivot.reindex(jobs).reset_index()

# Lista de elementos (puede contener texto o DataFrames)
elementos = ['Indicadores_Performance',
            indicadores_performance,
            'Estado_Ordenes', 
            estado_ordenes,
            'Inicio_Ordenes',
            inicio_ordenes_pivot,
            'Fin_Ordenes',
            fin_ordenes_pivot,
            'Operarios',
            operarios_pivot,
            'USoOperariosTotal',
            tiempo_prod_total,
            'productividadOperarios',
            Productividad
            
            ]

# Ruta del archivo de texto
archivo_txt = 'archivo.txt'

# Abrir el archivo en modo de escritura
with open(archivo_txt, 'w') as file:
    # Iterar sobre los elementos y escribirlos en el archivo
    for elemento in elementos:
        # Verificar el tipo de elemento
        if isinstance(elemento, str):
            # Si es texto, escribirlo directamente en el archivo
            file.write(elemento + '\n')
            file.write('\n')
        elif isinstance(elemento, pd.DataFrame):
            # Si es un DataFrame, escribirlo en el archivo utilizando to_string()
            file.write(elemento.to_string(index=False) + '\n')
            file.write('\n')
        else:
            # Otro tipo de elemento no compatible, omitirlo o manejarlo según tus necesidades
            file.write(str(elemento) + '\n')
            file.write('\n')
















