import numpy as np
import matplotlib.pyplot as plt
from pyomo.environ import *
from pyomo.opt import SolverFactory


# Function to set up and solve the model with varying cost for product 1 from supplier 1
def solve_model(new_cost_c11):
    # Model
    model = ConcreteModel()

    # Sets
    model.Products = RangeSet(3)  # Three products
    model.Suppliers = RangeSet(2)  # Two suppliers

    # Parameters (costs, demand, supply)
    costs = {(1, 1): new_cost_c11, (2, 1): 10, (3, 1): 15,  # Updating cost for product 1 from supplier 1
             (1, 2): 4, (2, 2): 11, (3, 2): 14}
    demand = {1: 100, 2: 150, 3: 200}
    supply = {1: 250, 2: 300}

    model.Costs = Param(model.Products, model.Suppliers, initialize=costs)
    model.Demand = Param(model.Products, initialize=demand)
    model.Supply = Param(model.Suppliers, initialize=supply)

    # Variables
    model.Quantity = Var(model.Products, model.Suppliers, domain=NonNegativeReals)

    # Objective
    def total_cost_rule(model):
        return sum(model.Costs[p, s] * model.Quantity[p, s] for p in model.Products for s in model.Suppliers)

    model.TotalCost = Objective(rule=total_cost_rule, sense=minimize)

    # Constraints
    def demand_constraint_rule(model, p):
        return sum(model.Quantity[p, s] for s in model.Suppliers) == model.Demand[p]

    model.DemandConstraint = Constraint(model.Products, rule=demand_constraint_rule)

    def supply_constraint_rule(model, s):
        return sum(model.Quantity[p, s] for p in model.Products) <= model.Supply[s]

    model.SupplyConstraint = Constraint(model.Suppliers, rule=supply_constraint_rule)

    # Solve
    solver = SolverFactory('gurobi')
    result = solver.solve(model)

    return model.TotalCost()


# Initial setup
baseline_cost_c11 = 5
baseline_total_cost = solve_model(baseline_cost_c11)

# Range of costs for sensitivity analysis
cost_range_c11 = np.linspace(4, 6, 21)  # Exploring costs from 4 to 6 in 0.1 increments

# Arrays for results
cost_changes = []
total_cost_changes = []

# Perform sensitivity analysis
for new_cost_c11 in cost_range_c11:
    new_total_cost = solve_model(new_cost_c11)
    cost_change = ((new_cost_c11 - baseline_cost_c11) / baseline_cost_c11) * 100
    total_cost_change = ((new_total_cost - baseline_total_cost) / baseline_total_cost) * 100
    cost_changes.append(cost_change)
    total_cost_changes.append(total_cost_change)

# Plotting the sensitivity analysis
plt.figure(figsize=(10, 6))
plt.plot(cost_changes, total_cost_changes, marker='o', linestyle='-', color='b')
plt.title('Relative Sensitivity of Total Cost to Changes in Cost of Product 1 from Supplier 1')
plt.xlabel('Percent Change in Cost of Product 1 from Supplier 1')
plt.ylabel('Percent Change in Total Cost')
plt.grid(True)
plt.show()
