from .stoich_reactor import StoichReactor

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#--------------------------ELECTRICTIY GENERATOR / TURBINE---------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------




class ElectricityGenerator(StoichReactor):
    """
    Class description
    -----------------

    This Class models an ElectricityGenerator or Steam turbine.
    It inherits from the StoichReactor Class.
    Therefore, it includes capital costs factors, energy demand factors,
    mass balance factors as well as the stoichiometric reaction facotrs.
    This class adds parameters to calculate the produced amount of electricity
    based on efficiency.

    Note: The energy production calculation in the SuperstructureModel is based
    on the inlet mass flow and the lower heating value of the components combined
    with the here defined overall efficiency value.
    """



    def __init__(self, Name, UnitNumber, Efficiency = None,  Parent = None,
                 *args, **kwargs):

        super().__init__(Name, UnitNumber, Parent)

        # Non-Indexed Parameters
        self.Type = "ElectricityGenerator"
        self.Efficiency_TUR = {'turbine_efficiency': {self.Number: Efficiency}}


    def fill_unitOperationsList(self, superstructure):
        super().fill_unitOperationsList(superstructure)
        superstructure.ElectricityGeneratorList['TURBINES'].append(self.Number)

    def set_efficiency(self, Efficiency):
        """
        Parameters
        ----------
        Efficiency : Float
            Sets efficiency of the Combined gas and stea turbine
            process between 0 and 1
        """
        self.Efficiency_TUR['turbine_efficiency'][self.Number]  = Efficiency


    def fill_parameterList(self):
        super().fill_parameterList()
        self.ParameterList.append(self.Efficiency_TUR)


