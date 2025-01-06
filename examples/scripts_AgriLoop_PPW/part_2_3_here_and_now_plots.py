"""

"""
import os
import matplotlib.pyplot as plt
import numpy as np
import pickle

def plot_boxplots_with_dots(box_plot_data_sets, dots_data_sets:list=None, xTicks=None, saveName=None):
    """
    Plots box plots for multiple sets of data and optionally overlays blue dots.

    Parameters:
    box_plot_data_sets (list of lists): A list where each element is a list of data for a box plot.
    dots_data_sets (list of lists, optional): A list where each element is a list of data points
                                                  to be plotted as red dots for each corresponding box plot.
    """
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot the box plots
    ax.boxplot(box_plot_data_sets, patch_artist=True,
               boxprops=dict(facecolor='lightgrey', color='black'),
               medianprops=dict(color='black'))

    # Overlay red dots if provided
    if dots_data_sets is not None:
        for i, red_dots_data in enumerate(dots_data_sets):
            x_positions = np.full_like(red_dots_data, i + 1)  # Position on the x-axis
            ax.plot(x_positions, red_dots_data, 'bo', label='blue Dots' if i == 0 else "", ms=2)

    # Customize the plot
    ax.set_xticklabels(xTicks)
    ax.set_ylabel('Earnings Before Income Taxes (€/ton PPW)')

    # Only show legend if red dots data is provided
    # if dots_data_sets is not None:
    #     ax.legend()

    # Show the plot
    #plt.show()

    # Save the plot
    if saveName is not None:
        plt.savefig(saveName)
    else:
        saveName = 'results/Part_2_3_box_plots_HAN.png'

    plt.savefig(saveName, dpi=300, bbox_inches='tight')

# file paths
# check the size of the pickle file
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# define the paths to the save and results directories
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_files')
savePathPLots = results_dir

# load the data from the pickle file
fileName = 'Part_2_3_HAN_data.pkl'
pickleFilePath = os.path.join(saved_data_dir, fileName)
# load the results from the pickle file
with open(pickleFilePath, 'rb') as file:
    dataDict = pickle.load(file)

# dataDict = {'boxplotData': boxplotData,
#             'flowSheetDict': flowSheetDict,
#             'MP_HereAndNowData': MP_HereAndNowData,
#             'AF_HereAndNowData': AF_HereAndNowData,
#             'pha_HereAndNowData': pha_HereAndNowData}

# these contain the optimal design of each scenario (i.e., the Wait and See solutions)
boxplotData = dataDict['boxplotData']
keysDict = list(boxplotData.keys())

# extract the wait and see results
compostKey = ((100, 'Grinding'), (800, 'Composting'), (8000, 'Compost'), (11, 'PotatoPeels'), (888, 'PPW splitter'))
compost_WaitAndSee = boxplotData[compostKey]
AFKey = ((100, 'Grinding'), (900, 'Extruder & dryer'), (7000, 'Animal.Feed'), (11, 'PotatoPeels'), (888, 'PPW splitter'))
AF_WaitAndSee = boxplotData[AFKey]
MPKey = ((100, 'Grinding'), (400, 'Mixed Culture Fermentation'), (500, 'Pasturisation & Decanter'),
         (510, 'MP Fermentation'), (520, 'Micro Filtration MP'), (550, 'Spray Dryer MP'), (600, 'Anaerobic Digester'),
         (610, 'Gas Membrane'), (800, 'Composting'), (1100, 'BioMethane'), (8000, 'Compost'), (9700, 'Micro.Prot.'),
         (11, 'PotatoPeels'), (22, 'Water'), (888, 'PPW splitter'), (777, 'Gas splitter'), (222, 'MCF splitter'))
MP_WaitAndSee = boxplotData[MPKey]
PHAKey = ((100, 'Grinding'), (400, 'Mixed Culture Fermentation'), (420, 'PHA Accumulation'), (430, 'Basket Centrifuge'),
          (435, 'PHA recovery Tank'), (438, 'Micro Filtration'), (440, 'PHA Washing'), (450, 'Micro Filtration 2'),
          (490, 'Spray Dryer PHA'), (600, 'Anaerobic Digester'), (610, 'Gas Membrane'), (800, 'Composting'),
          (1100, 'BioMethane'), (6000, 'PHA-Plastic'), (8000, 'Compost'), (11, 'PotatoPeels'), (22, 'Water'),
          (44, 'Lysol'), (888, 'PPW splitter'), (777, 'Gas splitter'), (222, 'MCF splitter'))
pha_WaitAndSee = boxplotData[PHAKey]

# extract the here and now results
compost_HereAndNow = dataDict['compost_HereAndNowData']
AF_HereAndNowData = dataDict['AF_HereAndNowData']
MP_HereAndNowData = dataDict['MP_HereAndNowData']
pha_HereAndNowData = dataDict['pha_HereAndNowData']

# make the box plot data sets
compost_dataBoxplot = compost_WaitAndSee + compost_HereAndNow
AF_dataBoxplot = AF_WaitAndSee + AF_HereAndNowData
MP_dataBoxplot = MP_WaitAndSee + MP_HereAndNowData
pha_dataBoxplot = pha_WaitAndSee + pha_HereAndNowData

sizeCheck = len(AF_dataBoxplot) + len(MP_dataBoxplot) + len(pha_dataBoxplot) + len(compost_dataBoxplot)
print(f'The size of the data is: {sizeCheck/4}')

# how many of the 200 scenarios are optimal results
print(f'For Compost (%): {len(compost_WaitAndSee)/len(compost_dataBoxplot)*100}')
print(f'For Animal Feed (%): {len(AF_WaitAndSee)/len(AF_dataBoxplot)*100}')
print(f'For Microbial Protein (%): {len(MP_WaitAndSee)/len(MP_dataBoxplot)*100}')
print(f'For PHA (%): {len(pha_WaitAndSee)/len(pha_dataBoxplot)*100}')


box_plot_data_sets = [
    compost_dataBoxplot,  # compost
    AF_dataBoxplot,  # animal feed
    MP_dataBoxplot,  # microbial protein
    pha_dataBoxplot,  # pha
     ]

dots_data_sets = [
    compost_WaitAndSee,  # compost
    AF_WaitAndSee,   # animal feed
    MP_WaitAndSee,  # microbial protein
    pha_WaitAndSee  # pha
]

# make the box plot figure
plot_boxplots_with_dots(box_plot_data_sets=box_plot_data_sets[0:2+1],
                        dots_data_sets=dots_data_sets[0:2+1],
                        xTicks=['Compost', 'Animal Feed', 'Microbial Protein'],
                        saveName='results/Part_2_3_box_plots_HAN.png')


plot_boxplots_with_dots(box_plot_data_sets= [box_plot_data_sets[-1]],
                        dots_data_sets= [dots_data_sets[-1]],
                        xTicks=['PHA'],
                        saveName='results/Part_2_3_box_plots_HAN_2.png')

plot_boxplots_with_dots(box_plot_data_sets=box_plot_data_sets,
                        dots_data_sets=dots_data_sets,
                        xTicks=['Compost', 'Animal Feed', 'Microbial Protein', 'PHA'],
                        saveName='results/Part_2_3_box_plots_HAN_3.png')

print('\033[92m' + '------sucess---------'+ '\033[0m')
