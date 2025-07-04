# To Dos
# - Chance Input Reading of PHI1 and PHI2 , but also change this in the Excel
#   sheet


# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:56:00 2020

@author: Celina
"""

from . import wrapping_functions as WF
from .wrapp_unit_data import *
from ..outdoor_core.input_classes.unit_operations.library.CHP import CombinedHeatAndPower
from ..outdoor_core.input_classes.unit_operations.library.distributor import Distributor
from ..outdoor_core.input_classes.unit_operations.library.furnace import HeatGenerator
from ..outdoor_core.input_classes.unit_operations.library.pool import ProductPool
from ..outdoor_core.input_classes.unit_operations.library.source import Source
from ..outdoor_core.input_classes.unit_operations.library.stoich_reactor import StoichReactor
from ..outdoor_core.input_classes.unit_operations.library.turbine import ElectricityGenerator
from ..outdoor_core.input_classes.unit_operations.library.yield_reactor import YieldReactor
from ..outdoor_core.input_classes.unit_operations.superclasses.physical_process import PhysicalProcess


def wrapp_processUnits(dfi):
    """
    Description
    -----------
    - dfi = completely dataframe of one spreadsheet for one process
    - Function defines all ranges for the different "areas" in one spreadsheet
    - processclass will be set
    - Depending on the process class, function to set the other parameters will be called

    Context
    ----------
    function is called in get_DataFromExcel()

    Parameters
    ----------
    dfi : Dataframe

    """

    # Set the Excel Ranges
    GeneralDataRange = WF.convert_total('E', 10, 'E', 27)
    EnergyDataRange = WF.convert_total('M', 10, 'Q', 27)
    KappaUtRange = WF.convert_total('M', 10, 'Q', 27)
    BalanceDataRange = WF.convert_total('S', 10, 'U', 27)
    EconomicDataRange = WF.convert_total('H', 11, 'I', 27)

    PossibleSourcesRange = WF.convert_total('W', 10, 'Z', 27)

    ConcDataRange = WF.convert_total2('B', 10, 'F', 27)
    GammaDataRange = WF.convert_total2('H', 10, 'J', 37)  # increase the range to 37
    ThetaDataRange = WF.convert_total2('L', 10, 'N', 30)  # increase the range to 33
    XiDataRange = WF.convert_total2('H', 10, 'J', 30)

    process_class = dfi.iat[10, 4]

    if process_class == "Stoich.Reactor":

        obj = StoichReactor(dfi.iat[8, 4], dfi.iat[9, 4])
        wrapp_EnergyData(obj, dfi.iloc[EnergyDataRange], dfi.iloc[KappaUtRange], dfi.iloc[GeneralDataRange])
        wrapp_ReacionData(obj, dfi.iloc[GammaDataRange], dfi.iloc[ThetaDataRange])


    elif process_class == "Yield.Reactor":

        obj = YieldReactor(dfi.iat[8, 4], dfi.iat[9, 4])
        wrapp_EnergyData(obj, dfi.iloc[EnergyDataRange], dfi.iloc[KappaUtRange], dfi.iloc[GeneralDataRange])
        wrapp_ReacionData(obj, dfi.iloc[XiDataRange])


    elif process_class == "Heat.Generator":

        obj = HeatGenerator(dfi.iat[8, 4], dfi.iat[9, 4], Efficiency=dfi.iat[19, 4])
        wrapp_ReacionData(obj, dfi.iloc[GammaDataRange], dfi.iloc[ThetaDataRange])

    elif process_class == "Elect.Generator":

        obj = ElectricityGenerator(dfi.iat[8, 4], dfi.iat[9, 4], Efficiency=dfi.iat[19, 4])
        wrapp_ReacionData(obj, dfi.iloc[GammaDataRange], dfi.iloc[ThetaDataRange])

    elif process_class == "CHP.Generator":
        obj = CombinedHeatAndPower(dfi.iat[8, 4], dfi.iat[9, 4])  # Efficiency is already predifenied in the class
        wrapp_ReacionData(obj, dfi.iloc[GammaDataRange], dfi.iloc[ThetaDataRange])

    # everything else is a PhysicalProcess (which can only split or distribute streams)
    else:
        obj = PhysicalProcess(dfi.iat[8, 4], dfi.iat[9, 4])
        wrapp_EnergyData(obj, dfi.iloc[EnergyDataRange], dfi.iloc[KappaUtRange], dfi.iloc[GeneralDataRange])

    wrapp_GeneralData(obj, dfi.iloc[GeneralDataRange])
    wrapp_EconomicData(obj, dfi.iloc[EconomicDataRange], dfi.iloc[GeneralDataRange])
    wrapp_AdditivesData(obj, dfi.iloc[PossibleSourcesRange], dfi.iloc[ConcDataRange], dfi.iloc[BalanceDataRange])

    return obj


def wrapp_productPoolUnits(dfi):
    DataRange = WF.convert_total('D', 6, 'Q', 16)
    DataFrame = dfi.iloc[DataRange]
    PoolList = []

    for index, series in DataFrame.items():
        if not pd.isnull(series[4]):
            obj = ProductPool(series[4], series[5])
            wrapp_ProductpoolData(obj, series)
            PoolList.append(obj)

    return PoolList


def wrapp_sourceUnits(dfi):
    GeneralDataRange = WF.convert_total('D', 6, 'S', 12)
    CompositionDataRange = WF.convert_total('D', 14, 'S', 36)
    SourcesList = []

    df1 = dfi.iloc[GeneralDataRange]
    df1.set_index(df1.columns[0], inplace=True)

    df2 = dfi.iloc[CompositionDataRange]
    counter = 1

    for index, series in df1.items():
        if not pd.isnull(series['Name']):
            obj = Source(Name=series['Name'], UnitNumber=series['Number'])
            wrapp_SourceData(obj, series, df2, counter)
            SourcesList.append(obj)
            counter += 1

    return SourcesList


def wrapp_distributors(dfi):
    DataRange = WF.convert_total('E', 6, 'O', 23)
    distributor_list = []

    df1 = dfi.iloc[DataRange]

    counter = 0
    for index, series in df1.items():
        if not pd.isnull(series[4]):
            obj = Distributor(series[4], series[5], series[6])
            wrapp_DistributorData(obj, series, df1, counter)
            distributor_list.append(obj)
            counter += 1

    return distributor_list


