from pyomo.environ import *

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
solver = SolverFactory('gurobi')
results = solver.solve(model, tee=True)

# Check infeasibility
if results.solver.termination_condition == TerminationCondition.infeasible:
    print("Model is infeasible. Running IIS analysis...")

    # Enable IIS computation
    solver.options['ResultFile'] = "iis.ilp"  # Save IIS to a file (optional)
    results = solver.solve(model, tee=True, options={'IISMethod': 1})

    # Mark constraints that are part of the IIS
    for c in model.component_objects(Constraint, active=True):
        for index in c:
            if c[index].active:
                print(f"Constraint {c.name} at index {index} is in the IIS.")
