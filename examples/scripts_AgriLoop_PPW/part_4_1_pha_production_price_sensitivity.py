"""
Author: Lucas Van der Hauwaert, 07/2024

Part 4.1 Sensitivity analysis of the PHA selling price.
This script runs a local sensitivity analysis (on the full superstructure) for the selling price of PHA
The goal is to find out at which selling price the production of PHA become the most favourable option in the
superstructure.

Questions to anwser:
- What is the optimal selling price of PHA so it is the most fav route?
- Is it a realistic price?

Objective: EBIT (maximize the profit)
Optimization mode: Sensitivity analysis
Excel file: potato_peel_case_study.xlsm

Generated files:
- results/Part_4_1_sensitivity_pha_price.png: the sensitivity analysis plot
- see Notes for the results from the console

"""




import sys
import os
import tracemalloc
import numpy as np
from sklearn.linear_model import LinearRegression

# start the memory profiler
# tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor
from outdoor import ModelOutput, MultiModelOutput

# define the paths to the Excel file and the results directories
ExcelPath = '../../examples/Excel_files/potato_peel_case_study_no_starch.xlsm'
currentScriptDir = os.path.dirname(__file__)
resultsPath = os.path.join(currentScriptDir, 'results')
saveOutputObjectDir = os.path.join(currentScriptDir, 'saved_files')


# set optimization mode
optimization_mode= 'sensitivity'

# create the superstructure data from the Excel file and
superstructure_Data = outdoor.get_DataFromExcel(path=ExcelPath,
                                                optimization_mode=optimization_mode)

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                         optimization_mode=optimization_mode,
                                                         solver='gurobi',
                                                         interface='local',
                                                         calculation_VSS=False,
                                                         calculation_EVPI=False,
                                                         options=solverOptions,)

# save the text file with the over view of the optimization
model_output.get_results(savePath=resultsPath,
                         saveName="Part_4_1_sensitivity_overview.txt",
                         pprint=False)



analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
fig = analyzer.create_sensitivity_graph(savePath=resultsPath,
                                        saveName="Part_4_1_sensitivity_pha_price",
                                        figureMode="single",
                                        xlable="PHA selling price (€/t)]",)


data = analyzer._collect_sensi_data('EBIT')
dataRegressionY = data['Price (ProductPrice)_6000'][0][-3:-1]  # price
dataRegressionX = data['Price (ProductPrice)_6000'][1][-3:-1]  # Ebit

def linear_regression_from_points(x, y):
    """
    Perform a linear regression on points.

    Args:
        x list of float: The x values of the points.
        y list of float: The y values of the points.

    Returns:
        LinearRegression: The trained linear regression model.
    """
    # Extract x and y values
    x = np.array(x).reshape(-1, 1)
    y = np.array(y)

    # Perform linear regression
    model = LinearRegression().fit(x, y)
    return model


# Example usage

model = linear_regression_from_points(dataRegressionX, dataRegressionY)
# Use the model to predict a y value for a given x
x_new = 61.456  # €/ton PPW
y_pred = model.predict([[x_new]])  # Input must be a 2D array
print(f"The price to sell PHA is: {y_pred[0]}")



print('\033[92m' + '------sucess---------'+ '\033[0m')




