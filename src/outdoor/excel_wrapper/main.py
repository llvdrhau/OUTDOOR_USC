# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 11:25:35 2020


@author: Celina geändert am 01.09.2020:
    Templates werden nicht eingelesen genauso wie "Tabelle1" sondern nur die neu hinzugefügten Tabellen
"""

import pandas as pd

import warnings

import copy

from .wrapp_processes import wrapp_processUnits, wrapp_productPoolUnits, wrapp_sourceUnits, wrapp_distributors

from ..outdoor_core.utils.timer import time_printer

from .wrapp_system import wrapp_SystemData

from .wrapp_stochastic_data import wrapp_stochastic_data

from ..outdoor_core.utils.progress_bar import print_progress_bar #, print_progress_bar

# function for Pandafunction to read an excelfile:

def get_DataFromExcel(PathName=None, optimization_mode=None):

    """
    Description
    -----------
    - Function to read all spreadsheets of an exceldata
    - put data from excel in Super Structure
    - One spreadsheet = one process
    - Hidden spreadsheets with the name:
      Tabelle1, Template_CC, Template_Stö, etc. will be skipped

    Context
    ----------
    -wrapp.ProcessUnits: to fill the Super Structure for all processes
    -wrapp.SystemData: to fill the Super Structure with the system datas
    -add_Units: add Process(Object) to Objectlist

    Parameters
    ----------
    PathName : String, Path to Exceldata

    Returns
    -------
    Superstructure_Object

    """
    print('PATH NAME IS:::')
    print(PathName)

    timer = time_printer(programm_step='Extract data from excel')
    # Disable the specific warning about Data Validation extension to make code run faster
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    dataframe = pd.read_excel(PathName, sheet_name = None)

    PU_ObjectList  =[]

    ## Hidden tables with specific names will be skipped:
    Hidden_Tables = []
    Hidden_Tables.append('Template_PhysicalProcess')
    Hidden_Tables.append('Template_StoichReactor')
    Hidden_Tables.append('Template_YieldReactor')
    Hidden_Tables.append('Template_SteamGenerator')
    Hidden_Tables.append('Template_ElGenerator')
    Hidden_Tables.append('Template_ProductPool')
    Hidden_Tables.append('DataBank')
    Hidden_Tables.append('Component Databases')
    Hidden_Tables.append('Uncertainty_test_idea')
    Hidden_Tables.append('Uncertainty_old')

    number_of_processes = len(dataframe.keys()) - len(Hidden_Tables)
    count = 0

    # only add data for the stochastic optimization if the optimization mode is not specified in the function call,
    # the optimization mode is then specified in the Excel file that is passed on to the Superstructure_Object

    Superstructure_Object = wrapp_SystemData(dataframe['Systemblatt'], optimization_mode=optimization_mode)
    _optimization_mode = Superstructure_Object.optimization_mode



    for i in dataframe.keys():
        if i == 'Systemblatt':
            continue

        elif i == 'Uncertainty':
            continue

        elif i == "Pools":
            pools = wrapp_productPoolUnits(dataframe[i])
            for k in pools:
                PU_ObjectList.append(k)

        elif i == "Sources":
            sources = wrapp_sourceUnits(dataframe[i])
            for k in sources:
                PU_ObjectList.append(k)

        elif i == 'Distributor':
            distributors = wrapp_distributors(dataframe[i])
            for k in distributors:
                PU_ObjectList.append(k)

        elif i in Hidden_Tables:
            continue # skip the hidden tables

        else: # for the unit operations
            PU_ObjectList.append(wrapp_processUnits(dataframe[i]))

        data_extraction = count / number_of_processes * 100

        print_progress_bar(iteration= count, total= number_of_processes, prefix= 'Data Extraction' )
        count += 1

    print()  # to get a new line after the progress bar
    Superstructure_Object.add_UnitOperations(PU_ObjectList)
    timer = time_printer(timer, 'Exctract data from excel')



    if _optimization_mode == '2-stage-recourse':
        # save the data of the single optimization variable in the object for VSS and EVPI calculation
        Superstructure_Object_duplicate = copy.deepcopy(Superstructure_Object)
        Superstructure_Object.parameters_single_optimization = Superstructure_Object_duplicate

        # set the uncertainty data in the object
        df_stochastic = dataframe['Uncertainty']
        uncertaintyObject = wrapp_stochastic_data(df_stochastic)
        Superstructure_Object.set_uncertainty_data(uncertaintyObject=uncertaintyObject)
        Superstructure_Object.uncertaintyDict = uncertaintyObject.LableDict

    return Superstructure_Object


