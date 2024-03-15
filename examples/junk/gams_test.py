# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pyomo.environ as pyo
import pyomo.opt as po

model = pyo.ConcreteModel()
# variables

# input
model.glu = pyo.Var(bounds=(0, 1000))
model.fru = pyo.Var(bounds=(0, 1000))
# output
model.prop_R1 = pyo.Var()
model.ace_R1 = pyo.Var()

model.prop_R2 = pyo.Var()
model.ace_R2 = pyo.Var()


# boolean vars
model.y1 = pyo.Var(domain=pyo.Boolean)
model.y2 = pyo.Var(domain=pyo.Boolean)
model.y_R1 = pyo.Var(domain=pyo.Boolean)
model.y_R2 = pyo.Var(domain=pyo.Boolean)

# constraints
model.ConstraintsR = pyo.ConstraintList()

# only one input can be chosen
model.ConstraintsR.add(expr=model.y1 + model.y2 == 1)
model.ConstraintsR.add(expr= model.glu <= 1000 * model.y1)
model.ConstraintsR.add(expr=model.fru <= 1000 * model.y2)


# outputs reactor R1 and R2
model.ConstraintsR.add(expr=model.y_R1 + model.y_R2 == 1)

model.ConstraintsR.add(expr=model.prop_R1 == (0.5 * model.glu + 0.6 * model.fru)* model.y_R1 )
model.ConstraintsR.add(expr=model.ace_R1 == (0.2 * model.glu + 0.3 * model.fru) * model.y_R1 )

model.ConstraintsR.add(expr=model.prop_R2 == (0.25 * model.glu + 0.3 * model.fru) * model.y_R2 )
model.ConstraintsR.add(expr=model.ace_R2 == (0.4 * model.glu + 0.3 * model.fru) * model.y_R2 )


objective =   (model.prop_R1 + model.prop_R2) * 0.5 + (model.ace_R2 + model.ace_R1) * 0.1

model.obj = pyo.Objective(sense=pyo.maximize, expr=objective)

solvername = 'gams'
opt = po.SolverFactory(solvername)
# could also introduce extra variable in opt.solve to specify solver eg: solver='cplex'

# =============================================================================
#     Possible solver are: 'BARON', 'ANTIGONE', 'CPLEX', 'DICOPT'
# =============================================================================
#results = opt.solve(model, solver='BARON', keepfiles=True, tee=True)

model.pprint()
results = opt.solve(model, keepfiles=True, tee=True)

for v in model.component_objects(ctype=pyo.Var):
    for index in v:
        print('{0} = {1}'.format(v[index], pyo.value(v[index])))



