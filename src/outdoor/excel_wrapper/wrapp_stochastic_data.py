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

   # make the scenario dataframe, depending on the sampling mode
    if obj.SamplingMode == 'Combinatorial':
        # set the grouped parameters (i.e., those with the correlated uncertainty)
        obj.set_group_dict()
        obj.make_scenario_dataframe_combinatorial()

    elif obj.SamplingMode == 'LHS':
        #obj.set_group_dict()
        obj.make_scenario_dataframe_LHS()

    else:
        raise ValueError('Sampling mode not recognized')

    return obj
