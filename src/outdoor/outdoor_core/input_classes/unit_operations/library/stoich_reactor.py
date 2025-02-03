from ..superclasses.physical_process import PhysicalProcess


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#--------------------------STOICHIOMETRIC REACTOR------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class StoichReactor(PhysicalProcess):

    """
    Class description
    -----------------

    This Class models stoichmetric reactors, which inherit from the PhysicalProcess
    class. Therefore, they includes capital costs factors, energy demand factors and
    mass balance factors.
    This class adds parameters to calculated mass-based stoichmetric reactions
    based on reactants, conversion factors and stoichmetric values.

    """

    def __init__(self, Name, UnitNumber, Parent =None, *args, **kwargs):

        super().__init__(Name, UnitNumber, Parent)

        # Non-Indexed Attributes
        self.Type = "Stoich-Reactor"

        # Indexed Attrubutes
        self.gamma = {'stoich_reaction_coefficient': {}}
        self.theta = {'stoich_conversion_factor': {}}


    # REACTION SETTING METHODS
    # ------------------------

    def fill_unitOperationsList(self, superstructure):

        super().fill_unitOperationsList(superstructure)
        superstructure.StoichRNumberList['STOICH_REACTORS'].append(self.Number)

    def set_gammaFactors(self, gamma_dic):

        """

        Parameters
        ----------
        gamma_dic : Dictionary
            Example: dict= {(i1, r1) : value1, (i2, r1): value2,
                            (i3, r1): value3}

        """
        for i in gamma_dic:
            self.gamma['stoich_reaction_coefficient'][self.Number, i]  = gamma_dic[i]



    def set_thetaFactors(self, theta_dic):
        """

        Parameters
        ----------
        theta_dic: Dictionary
            Example:  dict= {(r1,m1): value1}
        """
        for i in theta_dic:
            self.theta['stoich_conversion_factor'][self.Number, i] = theta_dic[i]


    def set_reactionData(self,
                          StoichiometricFactors,
                          ConversionFactors
                          ):

        if self.Type == "Stoich-Reactor":
            print(self.Name)
            self.add_gammaFactors(StoichiometricFactors)
            self.add_thetaFactors(ConversionFactors)


    def fill_parameterList(self):
        super().fill_parameterList()
        # if self.Type == "Stoich-Reactor":
        self.ParameterList.append(self.gamma)
        self.ParameterList.append(self.theta)






