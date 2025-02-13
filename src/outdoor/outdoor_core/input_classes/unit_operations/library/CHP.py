from .stoich_reactor import StoichReactor


class CombinedHeatAndPower(StoichReactor):
    """
    Class description
    -----------------

    This Class models an Combined heat and power unit (CHP)
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

    def __init__(self, Name, UnitNumber, Efficiency=None, Parent=None, *args, **kwargs):
        super().__init__(Name, UnitNumber, Parent)
        """
        Efficiency : is a tuple, with the first element being the electrical efficiency
        and the second element being the furnace heat efficiency
        """

        # Non-Indexed Parameters
        self.Type = "CombinedHeatAndPower" # Type of the unit operation
        # https://doi.org/10.1016/j.apenergy.2018.06.013
        if Efficiency is None:
            self.Eff_tur = 0.35 # Efficiency of the turbine to generate electricity 30-40%
            self.Eff_fur = 0.50 # Efficiency of the furnace to generate heat 50-60%
        else:
            self.Eff_tur = Efficiency[0]
            self.Eff_fur = Efficiency[1]

        self.Efficiency_FUR = {'Efficiency_FUR': {self.Number: self.Eff_fur}}
        self.Efficiency_TUR = {'Efficiency_TUR': {self.Number: self.Eff_tur}}

    def fill_unitOperationsList(self, superstructure):
        super().fill_unitOperationsList(superstructure)
        superstructure.HeatGeneratorList['U_FUR'].append(self.Number)
        superstructure.ElectricityGeneratorList['U_TUR'].append(self.Number)


    def set_efficiency(self, Efficiency):
        """
        Parameters
        ----------
        Efficiency : Float
            Sets efficiency of the furnace process between 0 and 1
        """

        self.Efficiency_FUR['Efficiency_FUR'][self.Number] = self.Eff_fur
        self.Efficiency_TUR['Efficiency_TUR'][self.Number] = self.Eff_tur

    def fill_parameterList(self):
        super().fill_parameterList()
        self.ParameterList.append(self.Efficiency_FUR)
        self.ParameterList.append(self.Efficiency_TUR)




