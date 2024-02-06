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
    generalDataRange = WF.convert_total('B', 3, 'C', 8)
    generalDataFrame = dfi.iloc[generalDataRange]
    # make the first column of the dataframe the index of the dataframe
    generalDataFrame = generalDataFrame.set_index('Unnamed: 1')
    # make the dataframe a series
    generalDataFrame = generalDataFrame.squeeze()

    #generalDataFrame = generalDataFrame.T


    # get the custom level data
    customLevelRange = WF.convert_total('B', 14, 'B', 21)
    customLevelDataFrame = dfi.iloc[customLevelRange]

    # set the general data
    obj.set_general_data(generalDataFrame, customLevelDataFrame)

    # extract the uncertain parameters from the dataframe
    UncertainParametersRange = WF.convert_total('B', 25, 'K', 52)
    UncertainParametersDataFrame = dfi.iloc[UncertainParametersRange]
    obj.set_uncertain_params_dict(UncertainParametersDataFrame)

    # correct for the composition of the feed stocks that do not change (+ make sure the sum is allways 1)
    phiExclusionRange = WF.convert_total('D', 14, 'J', 21)  # feed composition
    phiExclusionDF = dfi.iloc[phiExclusionRange]
    obj.set_phi_exclusion_list(phiExclusionDF)


    # set the grouped parameters (i.e. those with the correlated uncertainty)
    obj.set_group_dict()

    # set the dataframe of the stochastic object
    obj.make_scenario_dataframe()

    # the price of the feed stocks (Source units)
    # materialCostRange = WF.convert_total('I', 47, 'M', 60) # feed price
    # materialCostDataFrame = dfi.iloc[materialCostRange]
    # obj._set_general_dict(materialCostDataFrame, 'materialcosts')
    #
    # # the price of products (Product pool units)
    # productPriceRange = WF.convert_total('O', 47, 'S', 60) # product price
    # productPriceDataFrame = dfi.iloc[productPriceRange]
    # obj._set_general_dict(productPriceDataFrame, 'ProductPrice')
    #
    # # the composition of the feed stocks (Source units)
    # phiRange = WF.convert_total('B', 10, 'G', 23) # feed composition
    # phiDataFrame = dfi.iloc[phiRange]
    # obj._set_general_dict(phiDataFrame, 'phi')
    #
    # phiExclusionRange = WF.convert_total('T', 13, 'Z', 20) # feed composition
    # phiExclusionDF = dfi.iloc[phiExclusionRange]
    # obj._set_phi_exclusion_list(phiExclusionDF)
    #
    # # conversion factor (Stoichiometric reactor units)
    # thetaRange = WF.convert_total('J', 10, 'P', 23) # conversion factor
    # thetaDataFrame = dfi.iloc[thetaRange]
    # obj._set_general_dict(thetaDataFrame, 'theta')
    #
    # # stoichiometric factor (Stoichiometric reactor units)
    # gammaRange = WF.convert_total('J', 28, 'P', 41) # yield factor
    # gammaDataFrame = dfi.iloc[gammaRange]
    # obj._set_general_dict(gammaDataFrame, 'gamma')
    #
    #
    # # split factor (Pysical process units)
    # myuRange = WF.convert_total('B', 28, 'H', 41) # split factor
    # myuDataFrame = dfi.iloc[myuRange]
    # obj._set_general_dict(myuDataFrame, 'myu')
    #
    # # yield factor (Yield reactor uints)
    # xiRange = WF.convert_total('B', 47, 'G', 60)  # split factor
    # xiDataFrame = dfi.iloc[xiRange]
    # obj._set_general_dict(xiDataFrame, 'xi')

    return obj
