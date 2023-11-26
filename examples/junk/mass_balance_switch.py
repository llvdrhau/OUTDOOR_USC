from pyomo.environ import ConcreteModel, Var, Objective, Constraint, NonNegativeReals, Binary, SolverFactory

# Create a model
model = ConcreteModel()

# Define variables
model.x = Var(domain=NonNegativeReals)  # Continuous variable
model.y = Var(domain=Binary)            # Binary variable

# Objective function: Maximize x + 2*y
model.objective = Objective(expr=model.x + 2*model.y)

# Constraints
model.constraint1 = Constraint(expr=model.x <= 10)
model.constraint2 = Constraint(expr=model.x - 4*model.y >= 3)

# Solve the model using Gurobi
solver = SolverFactory('gurobi')
solver.solve(model)

# Display the results
print(f"x = {model.x.value}")
print(f"y = {model.y.value}")


