
import sys
import os
import tracemalloc
import time
import numpy as np
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

startTime = time.time()

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor
from outdoor import MultiModelOutput
from outdoor import AdvancedMultiModelAnalyzer



fileName = "Part_2_wait_and_see_200_sc.pkl"


# check the size of the pickle file
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# define the paths to the save and results directories
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_files')
savePathPLots = results_dir

# load the results from the pickle file
pickleFilePath = os.path.join(saved_data_dir, fileName)

WaitAndSee_Object = MultiModelOutput.load_from_pickle(path=pickleFilePath)

uncertaintyMatrix = WaitAndSee_Object.uncertaintyMatrix


# Split DataFrame into two halves
n = len(uncertaintyMatrix.columns) // 4  # Find the midpoint
DFList = [uncertaintyMatrix.iloc[:, i:i+n] for i in range(0, len(uncertaintyMatrix.columns), n)]

for i, df in enumerate(DFList):
    sns.pairplot(df, diag_kind='hist', corner=True)
    # save the plot
    plt.savefig('results/pair_plot_part_200sc{}.png'.format(i))


