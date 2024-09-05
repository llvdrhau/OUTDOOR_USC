"""
Author: Lucas Van der Hauwaert, 07/2024

Part 2.3: Here and now analysis,

Imagine you choose to implement the best flow-sheet design from the single objective optimization. How would the
flow-sheet over the different scenarios made from the Wait and see design? We're going to do this for the three scenarios
which were feasible in the wait and see optimization. I.e. for production of Microbial Prottein, Animal Feed and PHA

Objective: EBIT (maximize the profit)
Optimization mode: wait and see
Output file: Part_2_wait_and_see_300_sc.pkl (generated in part_2_1_wait_and_see_optimization_run.py)

Generated files:
- results/box_plot_flowsheet_designs.png: the scenario analysis box plots
- Standard Regression Coefficients (SRC) from the wait and see optimization (see notes for results from the console)

"""


import sys
import os
import tracemalloc
import time
import matplotlib.pyplot as plt
import numpy as np

startTime = time.time()

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor
from outdoor import MultiModelOutput
from outdoor import AdvancedMultiModelAnalyzer

def plot_boxplots_with_dots(box_plot_data_sets, red_dots_data_sets:list=None):
    """
    Plots box plots for multiple sets of data and optionally overlays red dots.

    Parameters:
    box_plot_data_sets (list of lists): A list where each element is a list of data for a box plot.
    red_dots_data_sets (list of lists, optional): A list where each element is a list of data points
                                                  to be plotted as red dots for each corresponding box plot.
    """
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot the box plots
    ax.boxplot(box_plot_data_sets)

    # Overlay red dots if provided
    if red_dots_data_sets is not None:
        for i, red_dots_data in enumerate(red_dots_data_sets):
            x_positions = np.full_like(red_dots_data, i + 1)  # Position on the x-axis
            ax.plot(x_positions, red_dots_data, 'ro', label='Red Dots' if i == 0 else "", size=2)

    # Customize the plot
    # ax.set_title('Box Plots with Red Dots')
    ax.set_xlabel(['Microbial Protein', 'Animal Feed', 'PHA'])
    ax.set_ylabel('Eearnings Before Income Taxes (M€)')

    # Only show legend if red dots data is provided
    if red_dots_data_sets is not None:
        ax.legend()

    # Show the plot
    #plt.show()

    # Save the plot
    plt.savefig('results/Part_2_3_box_plots_HAN.png')



# file name that contains the results
fileName = 'Part_2_wait_and_see_200_sc.pkl'
# 'stochastic_mpi_sppy_100sc.pkl' #"Part_2_wait_and_see_300_sc.pkl"

# check the size of the pickle file
current_script_dir = os.path.dirname(os.path.abspath(__file__))


# define the paths to the save and results directories
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_files')
savePathPLots = results_dir

# load the results from the pickle file
pickleFilePath = os.path.join(saved_data_dir, fileName)
#WaitAndSee_Object = MultiModelOutput.load_chunks_from_pickle(path=saved_data_dir,
#                                                       saveName=fileName,
#                                                       nChunks=5)
WaitAndSee_Object = MultiModelOutput.load_from_pickle(path=pickleFilePath)



# Initialise the analyser object and plot the scenario analysis
analyzer = AdvancedMultiModelAnalyzer(WaitAndSee_Object)
_, flowSheetDict, boxplotData = analyzer.plot_scenario_analysis(path=savePathPLots,
                                savePlot=False,
                                showPlot=False,
                                flowThreshold=0.001)

print('')

# -----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------


# define the paths to the Excel file and the results directories
Excel_Path = '../../examples/Excel_files/potato_peel_case_study.xlsm'
#Excel_Path = '../../examples/Excel_files/potato_peel_case_study_reduced.xlsm'
current_script_dir = os.path.dirname(__file__)
Results_Path = os.path.join(current_script_dir, 'results')
save_Output_object_dir = os.path.join(current_script_dir, 'saved_files')


# get the scenario files from the wait and see analysis and pass them to the superstructure object
# load the results from the pickle file
scenarioDataFiles = WaitAndSee_Object._dataFiles
# delete the WaitAndSee_Object to free up memory
del WaitAndSee_Object


# for the here and now mode, we need to define the design variables.
# We can get the designs from the flowSheetDict and boxplotData from the wait and see analysis
keysDict = list(flowSheetDict.keys())

# --------------------------
# FOR MICROBIAL PROTEIN
# --------------------------
scKeys = list(flowSheetDict[keysDict[0]].keys())
microbialProteinDesign = flowSheetDict[keysDict[0]][scKeys[0]]  # take the first design
microbialProteinScenarioDataFiles = {}
# get the select set of scenario files from the wait and see analysis and pass them to the superstructure object
for sc in scenarioDataFiles:
    if sc not in flowSheetDict[keysDict[0]]:
        microbialProteinScenarioDataFiles.update({sc: scenarioDataFiles[sc]})

# --------------------------
# FOR Animal Feed
# --------------------------
scKeys = list(flowSheetDict[keysDict[1]].keys())
animalFeedDesign = flowSheetDict[keysDict[1]][scKeys[0]]  # take the first design
annimalFeedScenarioDataFiles = {}
# get the select set of scenario files from the wait and see analysis and pass them to the superstructure object
for sc in scenarioDataFiles:
    if sc not in flowSheetDict[keysDict[1]]:
        annimalFeedScenarioDataFiles.update({sc: scenarioDataFiles[sc]})

# --------------------------
# FOR PHA PRODUCTION
# --------------------------
scKeys = list(flowSheetDict[keysDict[2]].keys())
phaDesign = flowSheetDict[keysDict[2]][scKeys[0]]  # take the first design
phaScenarioDataFiles = {}
# get the select set of scenario files from the wait and see analysis and pass them to the superstructure object
for sc in scenarioDataFiles:
    if sc not in flowSheetDict[keysDict[2]]:
        phaScenarioDataFiles.update({sc: scenarioDataFiles[sc]})


# delete the scenarioDataFiles to free up memory
del scenarioDataFiles


# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# set optimization mode
optimization_mode = 'here and now'

# create the superstructure data from the Excel file
superstructure_Object_MP = outdoor.get_DataFromExcel(path=Excel_Path,
                                                  optimization_mode=optimization_mode,
                                                  scenarioDataFiles=microbialProteinScenarioDataFiles,
                                                  )

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output_microbial_protein = abstract_model.solve_optimization_problem(input_data=superstructure_Object_MP,
                                                                            optimization_mode=optimization_mode,
                                                                            solver='gurobi',
                                                                            interface='local',
                                                                            options=solverOptions,
                                                                            outputFileDesignSpace=microbialProteinDesign)


#print(model_output_microbial_protein._results_data)
print('scenarios of MP:', len(microbialProteinScenarioDataFiles))
print('Number of successful runs for Microbial Protein:', len(model_output_microbial_protein._results_data))


MPRedDots = []
for sc, objc in model_output_microbial_protein._results_data.items():
    data = objc._data
    try:
        MPRedDots.append(data['EBIT'])
    except:
        MPRedDots.append('xx')
        # print in red
        print('\033[91m' + 'EBIT not found in the data for scenario:', sc)
#print(MPRedDots)
del model_output_microbial_protein # delete the model_output_microbial_protein to free up memory

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

superstructure_Object_AF = outdoor.get_DataFromExcel(path=Excel_Path,
                                                    optimization_mode=optimization_mode,
                                                    scenarioDataFiles=annimalFeedScenarioDataFiles,
                                                    )


model_output_animal_feed = abstract_model.solve_optimization_problem(input_data=superstructure_Object_AF,
                                                                    optimization_mode=optimization_mode,
                                                                    solver='gurobi',
                                                                    interface='local',
                                                                    options=solverOptions,
                                                                    outputFileDesignSpace=animalFeedDesign)

print('scenarios of Animal Feed:', len(annimalFeedScenarioDataFiles))
print('Number of successful runs for Animal Feed:', len(model_output_animal_feed._results_data))

animalFeedRedDots = []
for sc, objc in model_output_animal_feed._results_data.items():
    data = objc._data
    try:
        animalFeedRedDots.append(data['EBIT'])
    except:
        # animalFeedRedDots.append('xx')
        # print in red
        print('\033[91m' + 'EBIT not found in the data for scenario:', sc)
#print(animalFeedRedDots)
del model_output_animal_feed # delete the model_output_animal_feed to free up memory

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


superstructure_Object_PHA = outdoor.get_DataFromExcel(path=Excel_Path,
                                                    optimization_mode=optimization_mode,
                                                    scenarioDataFiles=phaScenarioDataFiles,
                                                    )

model_output_pha = abstract_model.solve_optimization_problem(input_data=superstructure_Object_PHA,
                                                                    optimization_mode=optimization_mode,
                                                                    solver='gurobi',
                                                                    interface='local',
                                                                    options=solverOptions,
                                                                    outputFileDesignSpace=phaDesign)

print('scenarios of PHA:', len(phaScenarioDataFiles))
print('Number of successful runs for PHA:', len(model_output_pha._results_data))

phaRedDots = []
for sc, objc in model_output_pha._results_data.items():
    data = objc._data
    try:
        phaRedDots.append(data['EBIT'])
    except:
        # phaRedDots.append('xx')
        # print in red
        print('\033[91m' + 'EBIT not found in the data for scenario:', sc)
#print(phaRedDots)
del model_output_pha # delete the model_output_pha to free up memory




box_plot_data_sets = [
    boxplotData[keysDict[0]] ,  # First box plot
    boxplotData[keysDict[1]],  # Second box plot
    boxplotData[keysDict[2]],   # Third box plot
     ]

red_dots_data_sets = [
    MPRedDots,  # Red dots for the first box plot
    animalFeedRedDots,  # Red dots for the second box plot
    phaRedDots  # Red dots for the third box plot
]

# make the box plot figure
plot_boxplots_with_dots(box_plot_data_sets=box_plot_data_sets,
                        red_dots_data_sets=red_dots_data_sets)



# print in green
print('\033[92m' + '------sucess---------')


