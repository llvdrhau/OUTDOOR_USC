from .stoich_reactor import StoichReactor


class HeatGenerator(StoichReactor):
    """
    Class description
    -----------------

    This Class models an HeatGenerator or Steam generating furnace
    It inherits from the StoichReactor Class.
    Therefore, it includes capital costs factors, energy demand factors,
    mass balance factors as well as the stoichiometric reaction facotrs.
    This class adds parameters to calculate the produced amount of steam
    based on efficiency.

    Note: The energy production calculation in the SuperstructureModel is based
    on the inlet mass flow and the lower heating value of the components combined
    with the here defined overall efficiency value.
    It is assumed that HeatGenerators produce heat at the highest Heat-Temperature
    which is defined for the Superstructure-Class (boundary conditions).
    """


    def __init__(self, Name, UnitNumber, Efficiency = None, Parent = None,
                 *args, **kwargs):

        super().__init__(Name, UnitNumber, Parent)

        # Non-Indexed Parameters
        self.Type = "HeatGenerator"
        self.Efficiency_FUR = {'furnace_efficiency': {self.Number: Efficiency}}

    def fill_unitOperationsList(self, superstructure):
        super().fill_unitOperationsList(superstructure)
        superstructure.HeatGeneratorList['FURNACES'].append(self.Number)

    def set_efficiency(self, Efficiency):
        """
        Parameters
        ----------
        Efficiency : Float
            Sets efficiency of the furnace process between 0 and 1
        """
        self.Efficiency_FUR['furnace_efficiency'][self.Number]  = Efficiency

    def fill_parameterList(self):
        super().fill_parameterList()
        self.ParameterList.append(self.Efficiency_FUR)



