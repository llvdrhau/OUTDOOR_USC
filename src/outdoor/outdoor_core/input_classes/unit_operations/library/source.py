import math

from ..superclasses.virtual_process import VirtualProcess

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#--------------------------RAW MATERIAL SOURCE --------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class Source(VirtualProcess):
    """
    Class description
    -----------------

    This Class models a virtual raw material source.
    It inherits from the VirtualProcess class.
    Therefore, it includes mass balance factors.

    This class adds parameters which define
        - Minimal and maximum available raw material
        - GHG and FWD factors
        - Raw material costs
        - Composition of chemical compounds

    """

    def __init__(self, Name,
                 UnitNumber,
                 Parent = None,
                 *args,
                 **kwargs):

        super().__init__(Name, UnitNumber, Parent)

        self.Type = 'Source'
        self.Composition = {'phi': {}}
        self.MaterialCosts = {'materialcosts': {self.Number: 0}}
        self.LowerLimit = {'ll': {self.Number: 0}}
        self.UpperLimit = {'ul': {self.Number: None}}
        self.EmissionFactor = {'em_fac_source': {self.Number: 0}}
        self.FreshWaterFactor = {'fw_fac_source': {self.Number: 0}}



    def fill_unitOperationsList(self, superstructure):

        super().fill_unitOperationsList(superstructure)
        superstructure.SourceList['U_S'].append(self.Number)

    def set_sourceData(self,
                        Costs,
                        LowerLimit,
                        UpperLimit,
                        EmissionFactor,
                        FreshwaterFactor,
                        Composition_dictionary):

        self.__set_materialCosts(Costs)
        self.__set_lowerlimit(LowerLimit)
        self.__set_upperlimit(UpperLimit)
        self.__set_sourceEmissionFactor(EmissionFactor)
        self.__set_sourceFreshWaterFactor(FreshwaterFactor)
        self.__set_composition(Composition_dictionary)


    def __set_materialCosts(self, Costs):
        self.MaterialCosts['materialcosts'][self.Number] = Costs


    def __set_composition(self, composition_dic):
        for i in composition_dic:
            self.Composition['phi'][(self.Number,i)] = composition_dic[i]

    def __set_lowerlimit(self, LowerLimit):
        self.LowerLimit['ll'][self.Number] = LowerLimit

    def __set_upperlimit(self, UpperLimit):
        self.UpperLimit['ul'][self.Number] = UpperLimit

    def __set_sourceEmissionFactor(self, EmissionFactor):
        self.EmissionFactor['em_fac_source'][self.Number] = EmissionFactor

    def __set_sourceFreshWaterFactor(self, FreshwaterFactor):
        self.FreshWaterFactor['fw_fac_source'][self.Number] = FreshwaterFactor


    def fill_parameterList(self):
        super().fill_parameterList()
        self.ParameterList.append(self.Composition)
        self.ParameterList.append(self.MaterialCosts)
        self.ParameterList.append(self.LowerLimit)
        self.ParameterList.append(self.UpperLimit)
        self.ParameterList.append(self.EmissionFactor)
        self.ParameterList.append(self.FreshWaterFactor)




