import sys
import os
from pyomo.environ import *

import tracemalloc
tracemalloc.start()

a = os.path.dirname(__file__)
a = os.path.dirname(a)


b = a + '/src'
sys.path.append(b)


import outdoor 

Solver_Path = 'C:/Users/swbkeph/OneDrive - ArcelorMittal/Arbeitsordner/Bearbeitung/Python-Scripts/cbc/bin/cbc.exe'

Excel_Path = "large_case - Kopie.xlsm"

Results_Path = a +  '/examples/results/'

Data_Path = a +  '/examples/data/'

superstructure_instance = outdoor.get_DataFromExcel(Excel_Path)

# Opt = outdoor.SuperstructureProblem(parser_type='Superstructure')


# model_output = Opt.solve_optimization_problem(input_data=superstructure_instance, 
#                                               solver='glpk', 
#                                               interface='local', 
#                                               optimization_mode='single')

# current, peak = tracemalloc.get_traced_memory()
# print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")


# model_output.save_file(Results_Path, option='tidy')
# model_output.save_data(Data_Path)

# outdoor.create_superstructure_flowsheet(ts, Results_Path)

