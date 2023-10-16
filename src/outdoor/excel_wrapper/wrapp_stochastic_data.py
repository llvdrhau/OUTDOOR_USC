"""
Collects all the data related to the stochastic problem

author: Lucas Van der Hauwaert
date: october 2020
"""
from ..outdoor_core.input_classes.stochastic import StochasticObject
from . import wrapping_functions as WF


def wrapp_stochastic_data(dfi):
    # make the initial stochastic object
    obj = StochasticObject()

    # get all locations of the stochastic data of interest
    generalDataRange = WF.convert_total('B', 4, 'C', 5)
    generalDataFrame = dfi.iloc[generalDataRange]
    obj._set_general_data(generalDataFrame)

    # the composition of the feed stocks (Source units)
    phiRange = WF.convert_total('B', 10, 'F', 23) # feed composition
    phiDataFrame = dfi.iloc[phiRange]
    obj._set_general_dict(phiDataFrame, 'phi')

    # conversion factor (Stoichiometric reactor units)
    thetaRange = WF.convert_total('I', 10, 'N', 23) # conversion factor
    thetaDataFrame = dfi.iloc[thetaRange]
    obj._set_general_dict(thetaDataFrame, 'theta')

    # stoichiometric factor (Stoichiometric reactor units)
    gammaRange = WF.convert_total('I', 28, 'N', 41) # yield factor
    gammaDataFrame = dfi.iloc[gammaRange]
    obj._set_general_dict(gammaDataFrame, 'gamma')

    # yield factor (Yield reactor uints)
    xiRange = WF.convert_total('B', 28, 'G', 41) # split factor
    xiDataFrame = dfi.iloc[xiRange]
    obj._set_general_dict(xiDataFrame, 'xi')

    # split factor (Pysical process units)
    myuRange = WF.convert_total('B', 47, 'G', 60) # split factor
    myuDataFrame = dfi.iloc[myuRange]
    obj._set_general_dict(myuDataFrame, 'myu')

    # set the grouped parameters
    obj._set_group_dict()

    # set the dataframe of the stochastic object
    obj._set_scenario_probabilities()




    return obj
