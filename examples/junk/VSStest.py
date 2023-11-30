from pyomo.environ import *
import numpy as np

fixAcres = True
varyYield = True

# Create a concrete model
model = ConcreteModel()

# Decision variables
model.x1 = Var(within=NonNegativeReals) # acres of land devoted to wheat
model.x2 = Var(within=NonNegativeReals) # acres of land devoted to corn
model.x3 = Var(within=NonNegativeReals) # acres of land devoted to sugar beets

# model.x1 = Param(initialize= 120) # acres of land devoted to wheat
# model.x2 = Param(initialize= 80) # acres of land devoted to corn
# model.x3 = Param(initialize= 300) # acres of land devoted to sugar beets

model.w1 = Var(within=NonNegativeReals) # tons of wheat sold
model.y1 = Var(within=NonNegativeReals) # tons of wheat purchased
model.w2 = Var(within=NonNegativeReals) # tons of corn sold
model.y2 = Var(within=NonNegativeReals) # tons of corn purchased
model.w3 = Var(within=NonNegativeReals) # tons of sugar beets sold at the favorable price
model.w4 = Var(within=NonNegativeReals) # tons of sugar beets sold at the lower price

# parameters (data)
model.a1 = Param(initialize=2.5, mutable=True) # tons of wheat produced per acre
model.a2 = Param(initialize=3, mutable=True) # tons of corn produced per acre
model.a3 = Param(initialize=20, mutable=True) # tons of sugar beets produced per acre

# Objective function
model.obj = Objective(expr=150*model.x1 + 230*model.x2 + 260*model.x3 + 238*model.y1 - 170*model.w1
                           + 210*model.y2 - 150*model.w2 - 36*model.w3 - 10*model.w4, sense=minimize)

# Constraints
model.land_constraint = Constraint(expr=model.x1 + model.x2 + model.x3 <= 500)
model.wheat_balance = Constraint(expr=model.a1 * model.x1 + model.y1 - model.w1 >= 200)
model.corn_balance = Constraint(expr=model.a2 * model.x2 + model.y2 - model.w2 >= 240)

model.sugar_beets_balance_upper = Constraint(expr= model.w3 <= 6000)
model.sugar_beets_balance_lower = Constraint(expr= model.w3 + model.w4 <= model.a3 * model.x3)

# Solving the model (assuming you have GLPK solver)
solver = SolverFactory('gams')
solver.solve(model, tee=True)

# Display the results
#model.display()

objective_values = []
obj_value = model.obj()
objective_values.append(obj_value)

print("the profit made is {} euros  \n"
      "the land allocated to wheat is {} \n"
      "the land allocated to Corn is {} \n"
      "the land allocated to beets is {} \n".format(-obj_value, model.x1(), model.x2(), model.x3()))

# print the yields of all crops
print("the yield of wheat is {} tons per acre \n"
      "the yield of corn is {} tons per acre \n"
      "the yield of beets is {} tons per acre \n".format(model.a1()* model.x1() ,
                                                         model.a2() * model.x2(),
                                                         model.a3()* model.x3()))

# print what is sold and what is purchased
print("the amount of wheat sold is {} tons \n"
      "the amount of wheat purchased is {} tons \n"
      "the amount of corn sold is {} tons \n"
      "the amount of corn purchased is {} tons \n"
      "the amount of beets sold at the favorable price is {} tons \n"
      "the amount of beets sold at the lower price is {} tons \n".format(model.w1(),
                                                                         model.y1(),
                                                                         model.w2(),
                                                                         model.y2(),
                                                                         model.w3(),
                                                                         model.w4()))

# ... (the rest of your code remains unchanged)




# Change x variables to a parameters
if fixAcres:
    # Step 1: Save the optimal values of the land variables into parameters
    optimal_x1 = model.x1()
    optimal_x2 = model.x2()
    optimal_x3 = model.x3()

    # Step 2: Delete the land variables
    model.del_component(model.x1)
    model.del_component(model.x2)
    model.del_component(model.x3)
    #model.del_component(model.land_constraint) # Delete the land constraint

    # Step 3: Create new parameters with the optimal values
    model.x1 = Param(mutable= True, initialize= optimal_x1)
    model.x2 = Param(mutable= True, initialize= optimal_x2)
    model.x3 = Param(mutable= True, initialize= optimal_x3)

    # Step 4: Update the constraints and objective that involved the land variables
    # Objective function
    model.obj.set_value(expr=150 * model.x1 + 230 * model.x2 + 260 * model.x3 + 238 * model.y1 - 170 * model.w1
                               + 210 * model.y2 - 150 * model.w2 - 36 * model.w3 - 10 * model.w4)

    # Constraints
    model.land_constraint.set_value(expr=model.x1 + model.x2 + model.x3 <= 500)
    model.wheat_balance.set_value(expr=model.a1 * model.x1 + model.y1 - model.w1 >= 200)
    model.corn_balance.set_value(expr=model.a2 * model.x2 + model.y2 - model.w2 >= 240)

    model.sugar_beets_balance_upper.set_value(expr=model.w3 <= 6000)
    model.sugar_beets_balance_lower.set_value(expr=model.w3 + model.w4 <= model.a3 * model.x3)

if varyYield:
    # Step 2: Modify the yield parameters and solve the LP problem for each variation
    yield_changes = [0.8, 1, 1.2]  # -20% and +20%


    for change in yield_changes:
        model.a1.set_value(2.5 * change)
        model.a2.set_value(3 * change)
        model.a3.set_value(20 * change)

        # Solve the model with the modified parameters
        solver.solve(model, tee=False)

        # Print and store the objective value
        obj_value = model.obj()
        print("Objective value for yield change of", change * 100, "% is:", obj_value)
        objective_values.append(obj_value)
        print("the profit made is {} \n"
              "the land allocated to wheat is {} \n"
              "the land allocated to Corn is {} \n"
              "the land allocated to beets is {} \n".format(-obj_value, model.x1(), model.x2(), model.x3()))
        # print the yields of all crops
        print("the yield of wheat is {} tons per acre \n"
              "the yield of corn is {} tons per acre \n"
              "the yield of beets is {} tons per acre \n".format(model.a1() * model.x1(),
                                                                 model.a2() * model.x2(),
                                                                 model.a3() * model.x3()))
        # print what is sold and what is purchased
        print("the amount of wheat sold is {} tons \n"
              "the amount of wheat purchased is {} tons \n"
              "the amount of corn sold is {} tons \n"
              "the amount of corn purchased is {} tons \n"
              "the amount of beets sold at the favorable price is {} tons \n"
              "the amount of beets sold at the lower price is {} tons \n".format(model.w1(),
                                                                                 model.y1(),
                                                                                 model.w2(),
                                                                                 model.y2(),
                                                                                 model.w3(),
                                                                                 model.w4()))
    print("Objective values list:", objective_values)
    print('')
    # get the mean of the objective values and print it
    mean = np.mean(objective_values)
    print("the mean of the objective values is {}".format(round(-mean, 2)))



