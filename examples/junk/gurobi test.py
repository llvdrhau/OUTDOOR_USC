from pyomo.environ import *

# Create a Pyomo model
model = ConcreteModel()

# Define decision variables
model.x = Var(within=NonNegativeReals)

# Define the objective function to maximize (e.g., maximize 2x)
model.obj = Objective(expr=2 * model.x, sense=maximize)

# Define constraints (e.g., x <= 5)
model.constraint = Constraint(expr=model.x <= 5)

# Create a solver instance (GUROBI in this case)
opt = SolverFactory('gurobi')

# Solve the model
results = opt.solve(model)

# Check the solver status
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    # Model was solved to optimality
    print("Optimal solution found.")
    print(f"x = {model.x.value}")
    print(f"Objective value = {model.obj()}")

elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("The model is infeasible.")

elif results.solver.termination_condition == TerminationCondition.unbounded:
    print("The model is unbounded.")

else:
    print("Solver did not converge to optimality.")

# Display solver information
results.write()

from pyomo.environ import *
import numpy as np


def find_nan_parameters(model):
    """
    Check for NaN values in parameters of a Pyomo model.

    Args:
        model: A Pyomo model instance.

    Returns:
        A list of tuples containing component and key for parameters with NaN values.
        Returns an empty list if no NaN values are found.
    """
    nan_parameters = []

    # Iterate through all active parameters in the model
    for component in model.component_objects(Param, active=True):
        for key in component:
            param_value = component[key]()
            if isinstance(param_value, numbers.Number) and np.isnan(param_value):
                nan_parameters.append((component, key))

    return nan_parameters




# Create a Pyomo model (replace this with your model)
model = ConcreteModel()

# Define parameter declarations in the model
model.A = Param(initialize=1)
model.B = Param(initialize=2)
model.C = Param(initialize=3)

# Retrieve all parameter declarations in the model
parameter_declarations = list(model.component_data_objects(Param, active=True))

# Extract and print the values of the parameters
for param_declaration in parameter_declarations:
    param_name = param_declaration.name
    param_value = param_declaration()
    print(f"Parameter {param_name}: {param_value}")
