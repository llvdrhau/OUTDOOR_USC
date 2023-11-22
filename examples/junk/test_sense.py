from pyomo.environ import ConcreteModel, Var, Objective, Constraint, NonNegativeReals, minimize, SolverFactory

# Create a model instance
model = ConcreteModel()

# Define variables
model.xA = Var(domain=NonNegativeReals)
model.xB = Var(domain=NonNegativeReals)

# Objective function: Minimize Cost
model.cost = Objective(expr=20*model.xA + 30*model.xB, sense=minimize)

# Constraints
model.capacity_constraint = Constraint(expr=model.xA + model.xB <= 100)
model.min_productA_constraint = Constraint(expr=model.xA >= 20)
model.ratio_constraint = Constraint(expr=model.xA >= model.xB)

# You can now solve this model using a solver like GLPK or CBC
solver = SolverFactory('gurobi')
solver.solve(model)

# Print the sense of the optimization problem
if model.cost.sense == 1:
    print("The optimization problem is a minimization problem.")
elif model.cost.sense == -1:
    print("The optimization problem is a maximization problem.")
