from pyomo.environ import *
import logging
from pyomo.util.infeasible import log_infeasible_constraints

# Set the logging level to INFO
logging.basicConfig(level=logging.INFO)
logging.getLogger('pyomo.core').setLevel(logging.INFO)

# Define model
model = ConcreteModel()

# Define variables
model.x = Var(bounds=(0, 10))
model.y = Var(bounds=(0, 5))

# Define constraints
model.c1 = Constraint(expr=model.x + model.y <= 8)
model.c2 = Constraint(expr=model.x - model.y >= 6)
model.c3 = Constraint(expr=model.x + model.y <= 4)  # Conflicting constraint

# Define objective
model.obj = Objective(expr=model.x + model.y, sense=maximize)

# Solve the model
solver = SolverFactory('gurobi')  # Replace with your preferred solver
results = solver.solve(model, tee=False)

# Check the status
if results.solver.termination_condition != TerminationCondition.optimal:
    print("Model is infeasible or unbounded.")

    # Log infeasible constraints AFTER solving the model
    log_infeasible_constraints(model)
