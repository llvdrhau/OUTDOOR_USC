# -*- coding: utf-8 -*-
"""
This is a temporary script file.
"""
import pyomo.environ as pyo
import pyomo.opt as po

scr = 2

model = pyo.ConcreteModel()
# variables

# input
model.glu = pyo.Var(bounds=(0, 100))
# output
model.prop_R1 = pyo.Var()
model.ace_R1 = pyo.Var()
model.prop_R2 = pyo.Var()
model.ace_R2 = pyo.Var()
model.fuel = pyo.Var()
# reactor (or the sum of the outputs)
model.R1 = pyo.Var()
model.R2 = pyo.Var()
model.R3 = pyo.Var()
# boolean vars
model.y1 = pyo.Var(domain=pyo.Boolean)
model.y2 = pyo.Var(domain=pyo.Boolean)

# constraints
model.ConstraintsR = pyo.ConstraintList()
# outputs
model.ConstraintsR.add(expr=model.prop_R1 <= 0.5 * model.glu)
model.ConstraintsR.add(expr=model.ace_R1 <= 0.2 * model.glu)

model.ConstraintsR.add(expr=model.fuel <= 0.4 * model.prop_R1 + 0.1* model.ace_R1 )

model.ConstraintsR.add(expr=model.prop_R2 <= 0.25 * model.glu)
model.ConstraintsR.add(expr=model.ace_R2 <= 0.4 * model.glu)



if scr == 1:
    model.ConstraintsR.add(expr= model.R1 == (model.prop_R1 + model.ace_R1) * model.y1)
    model.ConstraintsR.add(expr= model.R2 == (model.prop_R2 + model.ace_R2) * model.y2)
    model.ConstraintsR.add(expr=model.R3 == model.fuel)
    model.ConstraintsR.add(expr=model.y1 + model.y2 == 1)

elif scr == 2:
    model.ConstraintsR.add(expr= model.R1 == (model.prop_R1 + model.ace_R1))
    model.ConstraintsR.add(expr= model.R2 == (model.prop_R2 + model.ace_R2))
    model.ConstraintsR.add(expr=model.R3 == model.fuel)

    model.ConstraintsR.add(expr=model.y1 + model.y2 == 1)

    model.ConstraintsR.add(expr= model.prop_R1 <= 1000 * model.y1)
    model.ConstraintsR.add(expr=model.ace_R1 <= 1000 * model.y1)
    #model.ConstraintsR.add(expr= model.y1 * 0 <= model.R1)

    model.ConstraintsR.add(expr= model.prop_R2 <= 1000 * model.y2)
    model.ConstraintsR.add(expr=model.ace_R2 <= 1000 * model.y2)
    #model.ConstraintsR.add(expr= model.y2 * 0 <= model.R2)




objective =  + model.R3 * 0.5 + model.R2 * 3 - model.glu * 0.5
#objective =   model.R1 * 0.7 + model.R2 * 0.5
model.obj = pyo.Objective(sense=pyo.maximize, expr=objective)

solvername = 'gams'
opt = po.SolverFactory(solvername)
# could also introduce extra variable in opt.solve to specify solver eg: solver='cplex'

# =============================================================================
#     Possible solver are: 'BARON', 'ANTIGONE', 'CPLEX', 'DICOPT'
# =============================================================================
#results = opt.solve(model, solver='BARON', keepfiles=True, tee=True)
results = opt.solve(model, keepfiles=True, tee=True)

model.pprint()

for v in model.component_objects(ctype=pyo.Var):
    for index in v:
        print('{0} = {1}'.format(v[index], pyo.value(v[index])))
