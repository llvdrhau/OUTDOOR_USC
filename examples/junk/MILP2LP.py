from pyomo.environ import *

def solve_model(model):
    solver = SolverFactory('gurobi')
    result = solver.solve(model, tee=True)
    model.display()

# Create a model
model = ConcreteModel()

# Define variables
model.x = Var(within=NonNegativeReals)
model.y = Var(within=Binary)
model.a = Param(initialize=3)

# Define objective
model.obj = Objective(expr=model.x - 2 * model.y, sense=maximize)

# Define constraints
model.con1 = Constraint(expr=model.x + model.y <= 10)

# Solve the MILP
solve_model(model)

# Change binary variable y to a parameter
model.del_component(model.y)
model.y = Param(initialize=1)  # Assuming y=1 from the MILP solution

# # Update the constraints and objective that involved y
model.con1.set_value(expr=model.x + model.y <= 10)
model.obj.set_value(expr=model.x - 2 * model.y)

# Solve the LP
solve_model(model)
