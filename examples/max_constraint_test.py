from pyomo.environ import *

# Create a ConcreteModel
model = ConcreteModel()

# Define a set of variables
model.var_set = Set(initialize=[1, 2, 3, 4, 5])  # Replace this with your actual set of variables

# Define the variables
model.variables = Var(model.var_set, domain=NonNegativeReals)
model.MaxCAPEX = Var()

# Define an expression for the maximum value
def max_expression_rule(model):
    return model.MaxCAPEX == max(model.variables[i] for i in model.var_set)
model.max_expression = Expression(rule=max_expression_rule)

# Define the constraint MaxCAPEX == max(set of variables)
model.constraint = Constraint(expr=model.MaxCAPEX == model.max_expression)

# Print the model to see the constraint
model.pprint()
