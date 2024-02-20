
"""
Created on Mon Mar 23 15:26:49 2020

@author: Celina
"""


# Definition des Systempfades der PySuOpt Bibliothek


import pandas as pd

from ..outdoor_core.input_classes.superstructure import Superstructure
from . import wrapping_functions as WF



def wrapp_SystemData(dfi, optimization_mode=None):

    """
    Description
    -----------

    - dfi = dataframe of the first spreadsheet "Systemblatt"
    - Ranges will be set for different "areas" in the spreadsheet
    - all other functions to set the parameters will be called

    Context
    ----------
    function is called in get_DataFromExcel()
    set-functions are called in this function to fill the Super Structure
    for all Systems-Information

    Parameters
    ----------
    dfi : Dataframe

    Return
    ---------
    Superstructure Object with lists of the system parameters

    """

    # Setting the Ranges

    GeneralDataRange = WF.convert_total('B', 4, 'C', 22)
    UtilitylistRange = WF.convert_total('S', 5, 'V', 8)
    ComponentlistRange = WF.convert_total('F', 5, 'K', 30)
    TemperatureIntervals = WF.convert_total('B', 34, 'B', 39)
    ReactionsListRange = WF.convert_total('N', 5, 'N', 15)
    ReactantsListRange = WF.convert_total ('P', 5,'P', 15)
    TemperaturePriceRange = WF.convert_total('T', 14, 'U',18 )

    #####



    df1 = dfi.iloc[GeneralDataRange]
    df1.set_index(df1.columns[0], inplace=True)

    df2 = dfi.iloc[UtilitylistRange]

    df3 = dfi.iloc[ComponentlistRange]

    df5 = dfi.iloc[TemperatureIntervals]
    df6 = dfi.iloc[ReactionsListRange]


    df7 = dfi.iloc[ReactantsListRange]


    df8= dfi.iloc [TemperaturePriceRange]



    # SET GENERAL DATA
    # -----------------
    if optimization_mode is None:
        # optimization mode is specified in the Excel file if it is not given as an argument to the function
        optimization_mode = df1.loc['Optimization mode'].iloc[0]

    obj = Superstructure(ModelName=df1.loc['TestCaseName'].iloc[0],
                         Objective=df1.loc['Objective'].iloc[0],
                         productDriver = df1.loc['Product driven'].iloc[0],
                         MainProduct=df1.loc['Main product'].iloc[0],
                         ProductLoad=df1.loc['Product load'].iloc[0],
                         OptimizationMode=optimization_mode)


    obj.set_operatingHours(df1.loc['Operating Hours'].iloc[0])

    obj.set_cecpi(df1.loc['Year of Study'].iloc[0])


    obj.set_interestRate(df1.loc['Interest rate'].iloc[0])

    obj.set_linearizationDetail()
    #obj.add_linearisationIntervals()

    obj.set_omFactor(df1.loc['O&M Factor'].iloc[0])



    # Heat Pump values

    if df1.loc['Heatpump Yes/No'].iloc[0] == 'Yes':
        COP = df1.loc['COP'].iloc[0]
        Costs = df1.loc['Cost per kW installed'].iloc[0]
        Lifetime = df1.loc['Lifetime'].iloc[0]
        T_IN = df1.loc['TIN'].iloc[0]
        T_OUT = df1.loc['TOUT'].iloc[0]

        obj.set_heatPump(Costs,
                         Lifetime,
                         COP,
                         T_IN,
                         T_OUT
                         )




    # ADD LISTS OF COMPONENTS, ETC.
    # ----------------------------
    liste = WF.read_list(df2,0)
    obj.add_utilities(liste)

    liste = WF.read_list(df3,0)
    obj.add_components(liste)

    liste = WF.read_list(df6,0)
    obj.add_reactions(liste)

    liste = WF.read_list(df7,0)
    obj.add_reactants(liste)

    dict1 = WF.read_type1(df3,0,1)
    obj.set_lhv(dict1)

    dict2  = WF.read_type1(df3,0,3)
    obj.set_mw(dict2)

    dict3 = WF.read_type1(df3,0,2)
    obj.set_cp(dict3)





    # ADD OTHER PARAMETERS
    # ---------------------

    dict1 = WF.read_type1(df2,0,2)
    obj.set_utilityEmissionsFactor(dict1)

    dict1 = WF.read_type1(df2,0,3)
    obj.set_utilityFreshWaterFator(dict1)

    liste = WF.read_type1(df3,0,4)
    obj.set_componentEmissionsFactor(liste)

    obj.set_deltaCool(df8.iloc[4,1])


    liste1 = WF.read_list(df8,0)
    liste2 = WF.read_list(df8,1)

    dictTemperaturePrices = {'super': df8.iloc[0,1],
                             'high': df8.iloc[1,1],
                             'medium': df8.iloc[2,1],
                             'low': df8.iloc[3,1]}

    obj.temperaturePricesDict = dictTemperaturePrices
    obj.set_heatUtilities(liste1, liste2)

    dict3 = WF.read_type1(df2,0,1)
    obj.set_deltaUt(dict3)


    # # PARAMETERS FOR SPECIAL OPTIMIZATION MODES
    # # -----------------------------------------

    # added to separate python file (wrapp_parameters_optimisation_mode.py)
    # functions called in this file:
    # .src\outdoor\excel_wrapper\main.py

    # -----------------------------
    #
    # if obj.optimization_mode == 'multi-objective':
    #
    #     MultiCriteriaRange = WF.convert_total('N', 32, 'P',34)
    #     df9 = dfi.iloc [MultiCriteriaRange]
    #
    #     dict1 = {}
    #     dict1[df9.iloc[0,0]] = (df9.iloc[0,1], df9.iloc[0,2])
    #     dict1[df9.iloc[1,0]] = (df9.iloc[1,1], df9.iloc[1,2])
    #     dict1[df9.iloc[2,0]] = (df9.iloc[2,1], df9.iloc[2,2])
    #
    #     obj.set_multiObjectives(dict1)


    # elif obj.optimization_mode == 'sensitivity':
    #
    #     SensitivityRange = WF.convert_total('S', 33, 'X',41)
    #     df9 = dfi.iloc[SensitivityRange]
    #
    #     for i in range(len(df9)):
    #         if not pd.isnull(df9.iloc[i,0]):
    #
    #             p_name = df9.iloc[i,0]
    #             min_v = df9.iloc[i,2]
    #             max_v = df9.iloc[i,3]
    #             steps = df9.iloc[i,4]
    #
    #             if not pd.isnull(df9.iloc[i,1]):
    #                 index =  df9.iloc[i,1]
    #             else:
    #                 index = None
    #
    #
    #             obj.add_sensi_parameters(p_name, min_v, max_v, steps, index)
    #
    # elif obj.optimization_mode == 'cross-parameter sensitivity':
    #
    #     SensitivityRange = WF.convert_total('S', 33, 'X',41)
    #     df9 = dfi.iloc[SensitivityRange]
    #
    #     for i in range(2):
    #         if not pd.isnull(df9.iloc[i,0]):
    #     #
    #     #             p_name = df9.iloc[i,0]
    #     #             min_v = df9.iloc[i,2]
    #     #             max_v = df9.iloc[i,3]
    #     #             steps = df9.iloc[i,4]
    #     #
    #     #             if not pd.isnull(df9.iloc[i,1]):
    #     #                 index =  df9.iloc[i,1]
    #     #             else:
    #     #                 index = None
    #     #
    #     #
    #     #             obj.add_sensi_parameters(p_name, min_v, max_v, steps, index)


    return obj





