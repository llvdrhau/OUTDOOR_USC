from pyomo.environ import (ConcreteModel, Var, Param, Objective, Constraint,
                           NonNegativeReals, Binary, maximize, SolverFactory)
import pyomo.environ as pyo
import pyomo.opt as po

# Define the concrete model
model = ConcreteModel()

# Variables
model.glucose_use = Var(within=NonNegativeReals)
model.fructose_use = Var(within=NonNegativeReals)
model.reactor1_ethanol = Var(within=NonNegativeReals)
model.reactor2_ethanol = Var(within=NonNegativeReals)

# Bolean variables
model.glucose_choice = Var(within=Binary)
model.fructose_choice = Var(within=Binary)
model.reactor1_choice = Var(within=Binary)
model.reactor2_choice = Var(within=Binary)

# Parameters
model.reactor1_yield_glucose = Param(initialize=0.5)  # Yield of glucose in reactor 1
model.reactor1_yield_fructose = Param(initialize=0.6) # Yield of fructose in reactor 1
model.reactor2_yield_glucose = Param(initialize=0.25) # Yield of glucose in reactor 2
model.reactor2_yield_fructose = Param(initialize=0.3) # Yield of fructose in reactor 2

# Constraints
# define the constraints for the boolean variables
# Only one of glucose or fructose can be chosen
model.input_choice = Constraint(expr= model.glucose_choice + model.fructose_choice == 1)
model.reactor_choice = Constraint(expr= model.reactor1_choice + model.reactor2_choice == 1)

# Mass balance for inputs to reactors
model.mass_balance_reactor1 = Constraint(expr=model.reactor1_ethanol == model.reactor1_choice *(model.glucose_use * model.reactor1_yield_glucose
                                                                        + model.fructose_use * model.reactor1_yield_fructose))

model.mass_balance_reactor2 = Constraint(expr=model.reactor2_ethanol == model.reactor2_choice *(model.glucose_use* model.reactor2_yield_glucose
                                              + model.fructose_use * model.reactor2_yield_fructose))



# Big M method for handling conditional constraints
BigM = 1000  # Adjust this value as necessary

# Ensure inputs are used according to the choice
model.glucose_usage = Constraint(expr=model.glucose_use <= model.glucose_choice * BigM)
model.fructose_usage = Constraint(expr=model.fructose_use <= model.fructose_choice * BigM)

# # Ensure reactors are used according to the choice
# model.reactor1_usage = Constraint(expr=model.reactor1_ethanol <= model.reactor1_choice * BigM)
# model.reactor2_usage = Constraint(expr=model.reactor2_ethanol <= model.reactor2_choice * BigM)

# write objective of the optimization problem
model.objective = Objective(expr=model.reactor1_ethanol + model.reactor2_ethanol, sense=maximize)


solvername = 'gams'
opt = po.SolverFactory(solvername)
model.pprint()
solution = opt.solve(model, keepfiles=True, tee=True)

for v in model.component_objects(ctype=pyo.Var):
    for index in v:
        print('{0} = {1}'.format(v[index], pyo.value(v[index])))

