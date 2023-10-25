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

    # get the custom level data
    customLevelRange = WF.convert_total('P', 12, 'P', 20)
    customLevelDataFrame = dfi.iloc[customLevelRange]

    # set the general data
    obj._set_general_data(generalDataFrame, customLevelDataFrame)

    # the price of the feed stocks (Source units)
    materialCostRange = WF.convert_total('I', 47, 'L', 60) # feed price
    materialCostDataFrame = dfi.iloc[materialCostRange]
    obj._set_general_dict(materialCostDataFrame, 'materialcosts')

    # the price of products (Product pool units)
    productPriceRange = WF.convert_total('N', 47, 'Q', 60) # product price
    productPriceDataFrame = dfi.iloc[productPriceRange]
    obj._set_general_dict(productPriceDataFrame, 'ProductPrice')

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


    # split factor (Pysical process units)
    myuRange = WF.convert_total('B', 28, 'G', 41) # split factor
    myuDataFrame = dfi.iloc[myuRange]
    obj._set_general_dict(myuDataFrame, 'myu')

    # yield factor (Yield reactor uints)
    xiRange = WF.convert_total('B', 47, 'F', 60)  # split factor
    xiDataFrame = dfi.iloc[xiRange]
    obj._set_general_dict(xiDataFrame, 'xi')

    # set the grouped parameters
    obj._set_group_dict()

    # set the dataframe of the stochastic object
    obj.make_scenario_dataframe()




    return obj
