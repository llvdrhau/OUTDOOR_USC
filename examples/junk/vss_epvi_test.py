from pyomo.environ import ConcreteModel, Var, Objective, NonNegativeReals, Param, SolverFactory, minimize

VALUE_OF_ETA1 = 1/3
VALUE_OF_ETA2 = 2/3

odds1 = 1/2
odds2 = 1/2

# Create a Concrete Model
model = ConcreteModel()

# Define the parameters (assuming eta1 and eta2 are given)
model.eta1 = Param(initialize=VALUE_OF_ETA1)
model.eta2 = Param(initialize=VALUE_OF_ETA2)

model.odds1 = Param(initialize=odds1)
model.odds2 = Param(initialize=odds2)

# Define variables
model.x = Var(domain=NonNegativeReals)

# Define Objective
def objective_rule(model):
    return 6 * model.x + 10 * (model.odds1 * (model.x - model.eta1) + model.odds1 * (model.x - model.eta2))

model.objective = Objective(rule=objective_rule, sense=minimize)

# No additional constraints are needed as x >= 0 is handled in the variable definition

# Solve the model using Gurobi
solver = SolverFactory('gurobi')
solver.solve(model)



# Print the value of x
x_value = model.x()
print(f"The value of x is: {x_value}")
