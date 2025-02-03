import copy
import math
import pandas as pd
from ..utils.linearizer import capex_calculator


class Superstructure_from_UI():
    """
    Class Description
    -----------------

    This Class has two roles:
        1) It is the main container class for all data which is considered
            as boundary condition data for a given superstructure optimization
            study. This includes e.g. electricity prices, but also lists of
            usable chemical compounds, reactions etc.

        2) It includes methods to include the unit-operation objects (into a list)
            with their specific data and write it into an overall DataFile
            which can be used by the SuperstructureProblem class
            to populate an empty SuperstructureModel class object.

    Its main method is the 'create_DataFile()' method, which is called inside
    the SuperstructureProblems 'solve_optimization_problem()' -
    'setup_model_instance()' methods in order to setup the complete data file.

    Other methods are categorized as:
        - set-methods: Set boundary condition data
        - add-methods: Add additional unit-operations, components, reactions etc.
        - cross-reference-methods: Calculate values which are dependend on
            boundary condition as well as unit-operation data.
        - create_datafile-methods: Methods to set up the DataFile for further processing.

    """

    def __init__(self,
                 ModelName,
                 Objective,
                 MainProduct=None,
                 ProductLoad=None,
                 productDriver='yes',
                 OptimizationMode=None,
                 *args,
                 **kwargs):

        super().__init__()

        # Non-indexed Attribute
        # is the process product driven or not
        self.productDriven = productDriver

        # uncertainty parameters for the stochastic problem. filled in if stochastic problem is solved
        self.uncertaintyDict = {}

        # if using mpi-sspy the dictionary is filled with the scenario data files
        self.scearioDataFiles = {}
        self.stochasticMode = None
        self._dataStochastic = None

        # CONSTANT SETS
        # -------------

        self.OBJECTIVE_SET = {'EBIT', 'NPE', 'NPC', 'FWD'}

        self.OPTIMIZATION_MODE_SET = {'single',
                                      'multi-objective',
                                      'sensitivity',
                                      'cross-parameter sensitivity',
                                      '2-stage-recourse',
                                      'wait and see',
                                      'here and now'}

        self.SENSITIVE_PARAMETERS_SET = {"Split factors (split_factor)",
                                         "Feed Composition (component_concentration)",
                                         "Conversion factor (stoich_conversion_factor)",
                                         "Stoichiometric factor (stoich_reaction_coefficient)",
                                         "Yield factor (yield_factor_unit_operation)",
                                         "Costs (material_costs)",
                                         "Price (ProductPrice)",
                                         "Electricity price (delta_ut)",
                                         "Chilling price (delta_ut)",
                                         "Heating demand (specific_heat_demand)",
                                         "Electricity demand (specific_utility_demand)",
                                         "Reference Capital costs (C_Ref)",
                                         "Component concentration (concentration)",
                                         "Operating and maintenance (K_OM)"}

        self.CECPI_SET = {1994: 368.1, 1995: 381.1, 1996: 381.7, 1997: 386.5,
                          1998: 389.5, 1999: 390.6, 2000: 394.1, 2001: 394.3,
                          2002: 395.6, 2003: 402.0, 2004: 444.2, 2005: 468.2,
                          2006: 499.6, 2007: 525.4, 2008: 575.4, 2009: 521.9,
                          2010: 550.8, 2011: 585.7, 2012: 584.6, 2013: 567.1,
                          2014: 576.1, 2015: 556.8, 2016: 541.7, 2017: 566.1,
                          2018: 603.1, 2019: 607.5, 2020: 596.2, 2021: 708.8,
                          2022: 816.0, 2023: 789.6
                          }

        # to get an updated list use the following website:
        # https://toweringskills.com/financial-analysis/cost-indices/

        # Non-indexed Attributes
        # ----------------------

        # Main input
        # ----------

        if Objective in self.OBJECTIVE_SET:
            self.objective = Objective
            # in this case the flow sheet is determind by the min and max allowable flow rates of the sources
            if productDriver == 'no':
                ProductLoad = 1

                # nice print statments
                # ANSI escape code for bold text
                bold_text = "\033[1m"
                # ANSI escape code for green text
                green_text = "\033[32m"
                # ANSI escape code for resetting text formatting
                reset_text = "\033[0m"
                # Print statements with bold and green formatting
                print(f"{bold_text}{green_text}Notification: The process flows are now dependent on the source flows, "
                      f"make sure the bounds\nof the sources are set correctly on the Excel sheet 'Sources'{reset_text}")
        else:
            Warning('No correct objectives chosen, default objective NPC is simulated')
            self.objective = 'NPC'

        if OptimizationMode in self.OPTIMIZATION_MODE_SET:
            self.optimization_mode = OptimizationMode
        else:
            ValueError('No correct mode chosen, {} is not define in the set of modes: {}'.format(OptimizationMode,
                                                                                                 self.OPTIMIZATION_MODE_SET))
            #self.optimization_mode = 'single'

        self.ModelName = ModelName

        if not isinstance(MainProduct, str):
            if math.isnan(MainProduct) and productDriver == 'yes':
                raise Exception('No Main Product was chosen, please select a main product in the Sheet "Systemblatt"')

        self.MainProduct = MainProduct
        self.ProductLoad = {'product_load': ProductLoad}

        # Lists for sets
        # -----

        # Unit Operations
        # ----------------
        self.UnitsList = []
        self.UnitsNumberList = {'UNIT_PROCESSES': []}  #All units
        self.UnitsNumberList2 = {'UU': []}  #All units minus inputs
        self.StoichRNumberList = {'STOICH_REACTORS': []}
        self.YieldRNumberList = {'YIELD_REACTORS': []}
        self.SplitterNumberList = {'SPLITTERS': []}
        self.HeatGeneratorList = {'FURNACES': []}
        self.ElectricityGeneratorList = {'TURBINES': []}
        self.ProductPoolList = {'PRODUCT_POOLS': []}  #Outputs
        self.CostUnitsList = {'COSTED_UNIT_OPERATIONS': []}  #Costs of your inputs
        self.SourceList = {'RAW_MATERIAL_SOURCES': []}  #Sources
        self.SourceSet = {'CONNECTED_RAW_MATERIAL_UNIT_OPERATION': []}  #
        self.YieldSubSet = {'YIELD_REACTOR_COMPONENTS': []}  #
        self.distributor_subset = {'PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS': []}
        self.distributor_list = {'DISTRIBUTORS': []}
        self.decimal_set = {'DISTRIBUTOR_DECIMAL_SET': []}
        self.distributor_subset2 = {'DISTRIBUTOR_DECIMAL_SUBSET': []}

        self.connections_set = {'UNIT_CONNECTIONS': []}
        self.Scenarios = {'SC': []}  #Stochastic, maybe redundant
        self.Odds = {'odds': []}  #Prolly stochastic modeling too

        # ------------------

        # Heat Balance and Utilities
        # --------------------------
        self.HeatIntervalList = {'HEAT_INTERVALS': []}
        self.HeatUtilitiesList = {'HEATING_COOLING_UTILITIES': []}
        self.Heat_Temperatures = []
        self.HeatIntervals = {}
        self.UtilitiesList = {'UTILITIES': []}
        self.OtherUtilitiesList = {'ENERGY_UTILITIES': []}
        # ---------------------------

        # Others
        # ----------
        self.ComponentsList = {'COMPONENTS': []}
        self.ReactionsList = {'REACTIONS': []}
        self.ReactantsList = {'REACTANTS': []}

        self.LinPointsList = {'J': []}
        self.LinIntervalsList = {'JI': []}
        self.UnitNames = {'names': {}}
        self.UnitNames2 = {'names': {}}  # for the grafical representation
        # --------------

        self.groups = dict()
        self.connections = dict()

        # Databased input load (UNDER CONSTRUCTION)

        self.Database = None

        # Heat pump variables
        # -------------------
        self.HP_Costs = {'HP_Costs': 0}
        self.HP_ACC_Factor = {'HP_ACC_Factor': 0}
        self.COP_HP = {'heat_pump_performance_coefficient': 3}
        self.HP_LT = None
        self.HP_T_IN = {}
        self.HP_T_OUT = {}
        self.HP_active = False
        # -------------------

        #  Cost calculation variables
        # ----------------------------
        self.linearizationDetail = 'real'
        self.IR = {'IR': 0}
        self.H = {'H': 0}
        self.CECPI = {'CECPI': 0}
        self.K_OM = 0
        # ---------------------------

        # For special optimization mode run
        # --------------------------
        self.sensitive_parameters = []
        self.multi_objectives = dict()
        # --------------------------

        # Indexed Attributes
        # ------------------

        # Utility costs
        # --------------
        self.delta_q = {'delta_q': {}}
        self.heat_utilities = {}
        self.delta_cool = {'delta_cool': 14}
        self.delta_ut = {'delta_ut': {}}
        # -------------

        # Additional data
        # ---------------
        self.lhv = {'lower_heating_value': {}}
        self.mw = {'MW': {}}
        self.cp = {'CP': {}}
        self.em_fac_ut = {'em_fac_ut': {}}
        self.em_fac_comp = {'em_fac_comp': {}}
        self.fw_fac_ut = {'fw_fac_ut': {}}
        self.alpha = dict()
        # ---------------

        # -LCA Parameters
        # ---------------
        self.rmh_TAP = {'rmh_TAP':{}}
        self.rmh_GWP1000 = {'rmh_GWP1000':{}}
        self.rmh_FETP = {'rmh_FETP':{}}
        self.rmh_METP = {'rmh_METP':{}}
        self.rmh_TETP = {'rmh_TETP':{}}
        self.rmh_FFP = {'rmh_FFP':{}}
        self.rmh_FEP = {'rmh_FEP':{}}
        self.rmh_MEP = {'rmh_MEP':{}}
        self.rmh_HTPc = {'rmh_HTPc':{}}
        self.rmh_HTPnc = {'rmh_HTPnc':{}}
        self.rmh_IRP = {'rmh_IRP':{}}
        self.rmh_LOP = {'rmh_LOP':{}}
        self.rmh_SOP = {'rmh_SOP':{}}
        self.rmh_ODPinfinite = {'rmh_ODPinfinite':{}}
        self.rmh_PMFP = {'rmh_PMFP':{}}
        self.rmh_HOFP = {'rmh_HOFP':{}}
        self.rmh_EOFP = {'rmh_EOFP':{}}
        self.rmh_WCP = {'rmh_WCP':{}}
        self.reh_ecosystem_quality = {'reh_ecosystem_quality':{}}
        self.reh_human_health = {'reh_human_health':{}}
        self.reh_natural_resources = {'reh_natural_resources':{}}
        self.ced_renewable_energy_resources = {'ced_renewable_energy_resources':{}}
        self.ced_non_renewable_energy_sources = {'ced_non_renewable_energy_sources':{}}

        # - Output data structures
        # ------------------------
        self.Data_File = {None: {}}
        self.NI_ParameterList = []
        self.I_ParameterList = []
        # -----------------------

    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------
    #--------------------------SET PARAMETERS METHODS------------------------------
    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------

    def set_operatingHours(self, hours):
        self.H['H'] = hours

    def set_interestRate(self, IR):
        self.IR['IR'] = IR

    def set_omFactor(self, OM):
        self.K_OM = OM

    def set_cecpi(self, year):
        """
        Parameters
        ----------
        year : Integer
            Years from 1994 up to 2018 can be entered here

        """
        if year not in self.CECPI_SET:
            raise ValueError('Year is not in the range of 1994 to 2018')
        else:
            self.CECPI['CECPI'] = self.CECPI_SET[year]

    def set_heatPump(self,
                     SpecificCosts,
                     LifeTime,
                     COP,
                     T_IN,
                     T_OUT
                     ):
        """

        Parameters
        ----------
        SpecificCosts : Float
            Specific Costs of Heat Pump in €/kW_installed Heat supply.
        LifeTime : Integer
            Lifetime of Heatpump in full years.
        COP : Float
            Coefficient of performance of heat pump, should be higher than 1.
        T_IN : Integer
            Inlettemperature of heat pump (low-ex temperature).
        T_OUT :Integer
            Goal Temperature of Heat Pumpt (e.g. low pressure steam).

        Description
        -------
        If "HP_active" == true, this method sets the values of the heat pump.
        These values are used while initiating the superstructure to find the
        Temperatureintervals in the Heatbalance as well as supplied heat and costs.
        If "HP_active" == false, this method will be skipped, and the model will
        not regard a heat pump in the heat balances.

        """
        try:
            self.HP_active = True
            self.HP_Costs['HP_Costs'] = SpecificCosts
            self.COP_HP['heat_pump_performance_coefficient'] = COP
            self.HP_LT = LifeTime
            self.HP_T_IN['Temperature'] = T_IN
            self.HP_T_OUT['Temperature'] = T_OUT
            self.__set_heatTemperatures(T_IN, T_OUT)

        except:
            print('Please chose for State either On or Off, a non-negative \
                  lifetime and for COP a value > 1')

    def set_linearizationDetail(self, Detail='real'):
        """
        Parameters
        ----------
        Detail : String
            Use: "fine" , "average" or "rough"

        Context
        -------
        Based on the Input different amounts of Intervals are calculated for the
        CAPEX of the process equipment:

            fine     :  300
            average  :  20
            rough    :  10
            real     : New Approach

        """
        self.linearizationDetail = Detail

    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------
    #--------------------------ADD COMPONENTS TO LIST METHODS ---------------------
    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------

    def add_UnitOperations(self, *args):
        """
        Parameters
        ----------
        *args : Either List of Process Objects or Single Objects
            Takes a number of Process Objects and sorts them into the UnitLists

        """

        for i in args:
            if type(i) == list:
                for j in i:
                    if j not in self.UnitsList:
                        self.UnitNames2['names'][j.Number] = j.Name
                        j.fill_unitOperationsList(self)


            else:
                if i not in self.UnitsList:
                    i.fill_unitOperationsList(self)

    def __set_unitNames(self):
        for i in self.UnitsList:
            self.UnitNames['names'][i.Number] = i.Name

    def add_components(self, *args):
        """
        Parameters
        ----------
        *args : Either List of Strings of Single String Arguments
            Takes String Components and sorts them into ComponentsList

        """
        for i in args:
            if type(i) == list:
                for j in i:
                    if j not in self.ComponentsList['COMPONENTS']:
                        self.ComponentsList['COMPONENTS'].append(j)
            else:
                if i not in self.ComponentsList['COMPONENTS']:
                    self.ComponentsList['COMPONENTS'].append(i)

    def add_reactions(self, *args):
        """
        Parameters
        ----------
        *args : Either List of Strings of Single String Arguments
            Takes String Reactions and sorts them into RaactionsList
        """
        for i in args:
            if type(i) == list:
                for j in i:
                    if j not in self.ReactionsList['REACTIONS']:
                        self.ReactionsList['REACTIONS'].append(j)
            else:
                if i not in self.ReactionsList['REACTIONS']:
                    self.ReactionsList['REACTIONS'].append(i)

    def add_reactants(self, *args):

        """
        Parameters
        ----------
        *args : Either List of Strings of Single String Arguments
            Takes String Reactants and sorts them into ReactantsList
        """
        for i in args:
            if type(i) == list:
                for j in i:
                    if j not in self.ReactantsList['REACTANTS']:
                        self.ReactantsList['REACTANTS'].append(j)
            else:
                if i not in self.ReactantsList['REACTANTS']:
                    self.ReactantsList['REACTANTS'].append(i)

    def add_utilities(self, *args):
        """
        Parameters
        ----------
        *args : Either List of Strings of Single String Arguments
            Takes String Utilities and sorts them into UtilitiesList

        """
        for i in args:
            if type(i) == list:
                for j in i:
                    if j not in self.UtilitiesList['UTILITIES']:
                        self.UtilitiesList['UTILITIES'].append(j)
                        if j == 'Heat':
                            self.HeatUtilitiesList['HEATING_COOLING_UTILITIES'].append('Heat2')
                            self.HeatUtilitiesList['HEATING_COOLING_UTILITIES'].append(j)
                            self.UtilitiesList['UTILITIES'].append('Heat2')
                        else:
                            self.OtherUtilitiesList['ENERGY_UTILITIES'].append(j)
            else:
                if i not in self.UtilitiesList['UTILITIES']:
                    self.UtilitiesList['UTILITIES'].append(i)
                    if i == 'Heat':
                        self.HeatUtilitiesList['HEATING_COOLING_UTILITIES'].append(i)
                        self.HeatUtilitiesList['HEATING_COOLING_UTILITIES'].append('Heat2')
                        self.UtilitiesList['UTILITIES'].append('Heat2')
                    else:
                        self.OtherUtilitiesList['ENERGY_UTILITIES'].append(i)

    def set_lhv(self, lhv_dic):
        """
        Parameters
        ----------
        lhv_dic : Dictionary
            Takes Dictionaries of Type {'Component1': LHV_i, 'Component1': LHV_i....}

        """
        for i, j in lhv_dic.items():
            self.lhv['lower_heating_value'][i] = j

    def set_mw(self, mw_dic):
        """
        molecular weight
        Parameters
        ----------
        mw_dic : Dictionary
            Takes Dictionaries of Type {'Component1': MW_i, 'Component1': MW_i....}

        """
        for i, j in mw_dic.items():
            self.mw['MW'][i] = j

    def set_cp(self, cp_dic):
        for i, j in cp_dic.items():
            self.cp['CP'][i] = j

    def set_LCA_parameters(self, lca_dic):
        """
        Parameters
        :param lca_dic: dict{UnitNumber, {parameterName :value}}
        :return:
        """
        for i, j in lca_dic.items():
            self.rmh_TAP['rmh_TAP'][i] = j['rmh_TAP']
            self.rmh_GWP1000['rmh_GWP1000'][i] = j['rmh_GWP1000']
            self.rmh_FETP['rmh_FETP'][i] = j['rmh_FETP']
            self.rmh_METP['rmh_METP'][i] = j['rmh_METP']
            self.rmh_TETP['rmh_TETP'][i] = j['rmh_TETP']
            self.rmh_FFP['rmh_FFP'][i] = j['rmh_FFP']
            self.rmh_FEP['rmh_FEP'][i] = j['rmh_FEP']
            self.rmh_MEP['rmh_MEP'][i] = j['rmh_MEP']
            self.rmh_HTPc['rmh_HTPc'][i] = j['rmh_HTPc']
            self.rmh_HTPnc['rmh_HTPnc'][i] = j['rmh_HTPnc']
            self.rmh_IRP['rmh_IRP'][i] =  j['rmh_IRP']
            self.rmh_LOP['rmh_LOP'][i] =  j['rmh_LOP']
            self.rmh_SOP['rmh_SOP'][i] =  j['rmh_SOP']
            self.rmh_ODPinfinite['rmh_ODPinfinite'][i] = j['rmh_ODPinfinite']
            self.rmh_PMFP['rmh_PMFP'][i] =  j['rmh_PMFP']
            self.rmh_HOFP['rmh_HOFP'][i] =  j['rmh_HOFP']
            self.rmh_EOFP['rmh_EOFP'][i] =  j['rmh_EOFP']
            self.rmh_WCP['rmh_WCP'][i] =  j['rmh_WCP']
            self.reh_ecosystem_quality['reh_ecosystem_quality'][i] = j['reh_ecosystem_quality']
            self.reh_human_health['reh_human_health'][i] = j['reh_human_health']
            self.reh_natural_resources['reh_natural_resources'][i] = j['reh_natural_resources']
            self.ced_renewable_energy_resources['ced_renewable_energy_resources'][i] = j['ced_renewable_energy_resources']
            self.ced_non_renewable_energy_sources['ced_non_renewable_energy_sources'][i] = j['ced_non_renewable_energy_sources']

    def add_linearisationIntervals(self):
        if self.linearizationDetail == "rough":
            n = 10
        elif self.linearizationDetail == "fine":
            n = 301
        elif self.linearizationDetail == 'average':
            n = 20
        else:
            n = 13

        for i in range(1, n):
            self.LinPointsList['J'].append(i)
            self.LinIntervalsList['JI'].append(i)

        self.LinPointsList['J'].append(n)

    def __add_temperatureIntervals(self):
        """
        Description
        -----------

        Takes the Superstructure Python List

            - Heat_Temperatures

        and creates the

            - HeatIntervalsList

        which is a SET Input for the Superstructure Model.



        Context
        -------

        Is called in the Superstructure Method

            - create_DataFile

        after all Temperatures are added to the Grid


        """
        k = len(self.Heat_Temperatures) - 1
        for i in self.Heat_Temperatures:
            self.HeatIntervals[k] = i
            if k != 0:
                self.HeatIntervalList['HEAT_INTERVALS'].append(k)
            k -= 1

    def add_sensi_parameters(self,
                             parameter_name=None,
                             min_value=0,
                             max_value=0,
                             steps=0,
                             metadata=None):

        if parameter_name in self.SENSITIVE_PARAMETERS_SET:
            if metadata is None:
                self.sensitive_parameters.append(
                    (parameter_name, min_value, max_value, steps))
            else:
                self.sensitive_parameters.append(
                    (parameter_name, min_value, max_value, steps, metadata))
        else:
            raise ValueError('Parameter Name {} is not valid for sensitivity analyis'.format(parameter_name))

    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------
    #--------------------------ADD PARAMETERS TO INDEXED DICTIONARYS --------------
    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------

    def __set_deltaQ(self):
        for i, j in self.heat_utilities.items():
            for k, t in self.HeatIntervals.items():
                if t <= i and k < len(self.HeatIntervals) - 1:
                    self.delta_q['delta_q'][k + 1] = j

    def set_deltaUt(self, delta_ut_dic):
        for j, k in delta_ut_dic.items():
            self.delta_ut['delta_ut'][j] = k

    def set_deltaCool(self, delta_cool_value):
        self.delta_cool['delta_cool'] = delta_cool_value

    def set_utilityEmissionsFactor(self, em_fac_ut_dic):
        for i in em_fac_ut_dic:
            self.em_fac_ut['em_fac_ut'][i] = em_fac_ut_dic[i]

    def set_utilityFreshWaterFator(self, fw_fac_ut_dic):
        for i in fw_fac_ut_dic:
            self.fw_fac_ut['fw_fac_ut'][i] = fw_fac_ut_dic[i]

    def set_componentEmissionsFactor(self, em_fac_comp_dic):
        for i in em_fac_comp_dic:
            self.em_fac_comp['em_fac_comp'][i] = em_fac_comp_dic[i]

    def set_multiObjectives(self, Objectives_dictionary):
        self.multi_objectives = Objectives_dictionary

    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------
    #--------------------------CROSS REFERENCES METHODS ---------------------------
    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------

    def __set_processTemperatures(self, *args):

        """
        Description
        -----------
        Takes all Processes assigned to the Superstructur Object and checks
        their Process Temperatures (T) T_IN and T_OUT values.
        From these values it calls

            - add.HeatTemperatures(T)

        in order to set the Temperatures to the Heatintervals, List etc.



        Context
        -------
        Is called from the Superstructure Method

            - create_DataFile()

        after Superstructure Construction in order to create Temperature Grid

        """
        # create a dictionary with all the parameters and the corresponding prices
        dictTempPrices = {'super': 0, 'high': 0, 'medium': 0, 'low': 0}

        for i in self.UnitsList:
            if i.Number in self.CostUnitsList['COSTED_UNIT_OPERATIONS']:
                for j in i.T_IN.values():
                    if j != {}:
                        self.__set_heatTemperatures(j)
                for j in i.T_OUT.values():
                    if j != {}:
                        self.__set_heatTemperatures(j)

    def __set_heatTemperatures(self, *args):
        """
        Parameters
        ----------
        Takes Single or list arguments of Floats which represents Temperatures



        Description
        -----------
        Takes Temperatures and addes them to the Pythonlist (if not already there)

            - Heat_Temperatures

        afterwards sorts the List in Numeric Order



        Context
        -------
        Is called from Methods:

                - add_ProcessTemperatures()
                - add_heatUtilities()

        to fill all Temperatures to a Grid

        """

        for i in args:
            if type(i) == list:
                for j in i:
                    if j not in self.Heat_Temperatures and j is not None:
                        self.Heat_Temperatures.append(j)
            else:
                if i not in self.Heat_Temperatures and i is not None:
                    self.Heat_Temperatures.append(i)
        self.Heat_Temperatures = sorted(self.Heat_Temperatures)

    def set_heatUtilities(self, TemperatureList, CostList):
        """
        Parameters
        ----------
        TemperatureList : Python List Containing Temperatures of Utilities
        CostList        : Python List Containing Costs of Utlities (same Order)

        Description
        -----------
        Takes T and C Values of Utlities an adds them to the Dictionary

            - heat_utilities

        Also calls:

            - __set_heatTemperatures(TemperatureList)

        in order to add Temperatures to the T-Grid



        Context
        -------
        Is called as adding Method to add Utilities. Also Provides Cost Dictionary
        which is used later to calculate Costs of Heat Intervals

        PUBLIC


        """
        for i in range(len(TemperatureList)):
            self.heat_utilities[TemperatureList[i]] = CostList[i]
            self.__set_heatTemperatures(TemperatureList[i])

    def __calc_heatPump(self):
        """


        Description
        -------
        This method is called via preparation of the heat balances.
        If "HP_active" == True, than yearly costs for the heat pump are calculated
        using Lifetime and Interest Rate.
        Afterwards, TIN and TOUT are compared to the HeatIntervals and and the
        corresponding intervals are marked up for the heat balances inside the model.
        If "HP_active" == False Costs, Yearly Factor and COP are set to dummy values
        (This is probably unnessacery).


        """
        if self.HP_active == True:
            ir = self.IR['IR']
            lt = self.HP_LT
            self.HP_ACC_Factor['HP_ACC_Factor'] = ((ir * (1 + ir) ** lt) / ((1 + ir) ** lt - 1))

            for i, j in self.HeatIntervals.items():
                if j == self.HP_T_IN['Temperature']:
                    self.HP_T_IN['Interval'] = i + 1
                elif j == self.HP_T_OUT['Temperature']:
                    self.HP_T_OUT['Interval'] = i + 1

        else:
            self.HP_ACC_Factor['HP_ACC_Factor'] = 0
            self.HP_Costs['HP_Costs'] = 0
            self.COP_HP['heat_pump_performance_coefficient'] = 3

    def __fill_betaParameters(self):
        """
        Parameters
        ----------

        Used Attributes are:

            - self.UnitsList
            - Process Objects of UnitsList
            - self.HeatIntervals       (holding Data on T-Grid)
            - Process.HeatData        (holding Data on specific_utility_demand, TIN and TOUT)

        Sets Attributes:

            - Process.energy_demand_ration       (holding Data on partitioned Temperature Flow)
            - Process.specific_heat_demand      (holds Data on specific Heating Demand)
            - Process.specific_cooling_demand      (holds Data on specific Cooling Demand)


        Description
        -----------

        Takes specific Energy Demand (H/C) as well as Tempertures for every Process
        and checks:
                1. If 0 < specific_utility_demand < 0  -- > If specific_utility_demand > 0 : specific_heat_demand , else specific_cooling_demand
                2. Cross references TIN and TOUT as well as DeltaT with T-Grid
                    and calculates the Split (Portion) of TGrid(k) - TGrid(k-1)
                    based on DeltaT
                3. Sets Splits as energy_demand_ration Attributes
                4. If TIN = TOUT and specific_utility_demand != 0  --> Process is isothermal, energy_demand_ration is
                    1 for on specific Heat Interval
                5. Appends energy_demand_ration to Process ParameterList

        """

        r = len(self.Heat_Temperatures)

        for i in self.UnitsList:
            if i.Number in self.CostUnitsList['COSTED_UNIT_OPERATIONS'] and i.Number not in self.HeatGeneratorList[
                "FURNACES"] and i.Number not in self.ElectricityGeneratorList['TURBINES']:
                for k, j in i.HeatData.items():
                    tau = j['specific_utility_demand']
                    if tau is not None:
                        t_in = j['TIN']
                        t_out = j['TOUT']
                        if tau > 0:
                            DeltaT = t_out - t_in
                            i.specific_heat_demand['specific_heat_demand'][k, i.Number] = tau
                            i.specific_cooling_demand['specific_cooling_demand'][k, i.Number] = 0
                            for t, s in self.HeatIntervals.items():
                                if t_in > s:
                                    i.energy_demand_ration['energy_demand_ration'][i.Number, k, t] = 0
                                else:
                                    if t_out == s and t_out == t_in:
                                        i.energy_demand_ration['energy_demand_ration'][i.Number, k, t] = 1
                                    else:
                                        if t != 0:
                                            if t_out >= self.HeatIntervals[t - 1]:
                                                i.energy_demand_ration['energy_demand_ration'][i.Number, k, t] = (self.HeatIntervals[
                                                                                      t - 1] - s) / DeltaT
                                            else:
                                                i.energy_demand_ration['energy_demand_ration'][i.Number, k, t] = 0
                        else:
                            DeltaT = t_in - t_out
                            i.specific_heat_demand['specific_heat_demand'][k, i.Number] = 0
                            i.specific_cooling_demand['specific_cooling_demand'][k, i.Number] = -tau
                            for t, s in self.HeatIntervals.items():
                                if t_out > s:
                                    i.energy_demand_ration['energy_demand_ration'][i.Number, k, t] = 0
                                else:
                                    if t_out == s and t_out == t_in:
                                        i.energy_demand_ration['energy_demand_ration'][i.Number, k, t + 1] = 1
                                    else:
                                        if t != 0:
                                            if t_in >= self.HeatIntervals[t - 1]:
                                                i.energy_demand_ration['energy_demand_ration'][i.Number, k, t] = (self.HeatIntervals[
                                                                                      t - 1] - s) / DeltaT
                                            else:
                                                i.energy_demand_ration['energy_demand_ration'][i.Number, k, t] = 0
                i.ParameterList.append(i.energy_demand_ration)

    def __calc_capexLinearizationParameters(self):
        """
        Description
        -----------
        Takes all Process Units as well as the Intervals Values and
        calculates the piece-wise linearization of the CAPEX

        Uses the Side Module

            - capex_calculator()


        """
        for i in self.UnitsList:
            if i.Number in self.CostUnitsList['COSTED_UNIT_OPERATIONS']:
                aa = i.Number
                (i.lin_CAPEX_x, i.lin_CAPEX_y) = capex_calculator(i, self.CECPI, Detail=self.linearizationDetail)

    def __calc_accFactorParameter(self):
        """
        Description
        -----------
        Takes all Process Units and calculates the annual capex factor which is
        used in the Superstructure Model

        """
        for i in self.UnitsList:
            if i.Number in self.CostUnitsList['COSTED_UNIT_OPERATIONS']:
                i.ACC_Factor['ACC_Factor'][i.Number] = i.calc_ACCFactor(self.IR)

    def __set_turnoverParameter(self):

        for i in self.UnitsList:
            if i.Number in self.CostUnitsList['COSTED_UNIT_OPERATIONS']:
                i.turn_over_acc['to_acc'][i.Number] = i.calc_turnoverACC(self.IR)

    def __set_optionalFLH(self):
        for x in self.UnitsList:
            if x.FLH['full_load_hours'][x.Number] is None:
                x.FLH['full_load_hours'][x.Number] = self.H['H']

    def __set_optionalKOM(self):
        for x in self.UnitsList:
            if x.Number in self.CostUnitsList['COSTED_UNIT_OPERATIONS']:
                if x.K_OM['K_OM'][x.Number] is None:
                    x.K_OM['K_OM'][x.Number] = self.K_OM

    def __scan_unit_connections(self):

        data_file = self.Data_File[None]
        connector_data = data_file['split_factor']

        for i in connector_data.keys():
            connection = (i[0], i[1][0])

            if connection not in self.connections_set['UNIT_CONNECTIONS']:
                self.connections_set['UNIT_CONNECTIONS'].append(connection)

        for i in self.distributor_subset['PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS']:
            if i not in self.connections_set['UNIT_CONNECTIONS']:
                self.connections_set['UNIT_CONNECTIONS'].append(i)

    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------
    #--------------------------CREATE DATA-FILE METHODS ---------------------------
    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------

    # Fill Parameter List of Superstructure

    def __fill_nonIndexedParameterList(self):
        """
        Fills List with non-indexed Model-important parameters

        """

        self.NI_ParameterList.append(self.UnitsNumberList)
        self.NI_ParameterList.append(self.UnitsNumberList2)
        self.NI_ParameterList.append(self.StoichRNumberList)
        self.NI_ParameterList.append(self.YieldRNumberList)
        self.NI_ParameterList.append(self.SplitterNumberList)
        self.NI_ParameterList.append(self.HeatGeneratorList)
        self.NI_ParameterList.append(self.ElectricityGeneratorList)
        self.NI_ParameterList.append(self.ProductPoolList)
        self.NI_ParameterList.append(self.CostUnitsList)
        self.NI_ParameterList.append(self.SourceList)
        self.NI_ParameterList.append(self.SourceSet)
        self.NI_ParameterList.append(self.ComponentsList)
        self.NI_ParameterList.append(self.ReactantsList)
        self.NI_ParameterList.append(self.ReactionsList)
        self.NI_ParameterList.append(self.UtilitiesList)
        self.NI_ParameterList.append(self.HeatUtilitiesList)
        self.NI_ParameterList.append(self.HeatIntervalList)
        self.NI_ParameterList.append(self.LinPointsList)
        self.NI_ParameterList.append(self.LinIntervalsList)
        self.NI_ParameterList.append(self.H)
        self.NI_ParameterList.append(self.IR)
        self.NI_ParameterList.append(self.CECPI)
        self.NI_ParameterList.append(self.delta_cool)
        self.NI_ParameterList.append(self.COP_HP)
        self.NI_ParameterList.append(self.HP_ACC_Factor)
        self.NI_ParameterList.append(self.HP_Costs)
        self.NI_ParameterList.append(self.YieldSubSet)

        self.NI_ParameterList.append(self.distributor_list)
        self.NI_ParameterList.append(self.distributor_subset)
        self.NI_ParameterList.append(self.decimal_set)
        self.NI_ParameterList.append(self.distributor_subset2)
        self.NI_ParameterList.append(self.OtherUtilitiesList)
        self.NI_ParameterList.append(self.ProductLoad)
        self.NI_ParameterList.append(self.Scenarios)

    def __fill_indexedParameterList(self):
        """

        Fills List with indexed Model-important parameters

        """

        self.I_ParameterList.append(self.delta_q)
        self.I_ParameterList.append(self.em_fac_ut)
        self.I_ParameterList.append(self.em_fac_comp)
        self.I_ParameterList.append(self.fw_fac_ut)
        self.I_ParameterList.append(self.lhv)
        self.I_ParameterList.append(self.mw)
        self.I_ParameterList.append(self.UnitNames)
        self.I_ParameterList.append(self.cp)
        self.I_ParameterList.append(self.delta_ut)
        self.I_ParameterList.append(self.Odds)

    # Add the Parameters from the Lists to the Model-Ready Data File
    # ---------------

    def __fill_nonIndexedParameters(self):
        """
        Description
        -----------
        First calls Function to Fill non-indexed Parameter List
        Afterwards returns Parameters into die Data_File that is to be used
        for initialization of the AbstractModel

        """
        self.__fill_nonIndexedParameterList()
        for i in self.NI_ParameterList:
            for j in i:
                self.Data_File[None][j] = {None: i[j]}

    # Indexed Parameters / Dictionaries

    def __fill_indexedParameters(self):
        """
        Description
        -----------

        First calls __fill_indexedParameterList to fill indexed parameters from Superstructure
        Parameters, then fills Data_File with these Parameters.

        """

        self.__set_unitNames()

        self.__fill_indexedParameterList()
        x = self.I_ParameterList
        for i in x:
            for j, k in i.items():
                try:
                    self.Data_File[None][j].update(k)
                except:
                    self.Data_File[None][j] = k

    # Parameters origin from Process Units

    def __fill_processParameterList(self):
        """
        Description
        -----------

        Goes through all Processes and add the Parameters in their ParameterList
        to the Model-Ready DataFile

        """

        for z in self.UnitsList:
            z.fill_parameterList()
            x = z.ParameterList
            for i in x:
                for j, k in i.items():
                    try:
                        self.Data_File[None][j].update(k)
                    except:
                        self.Data_File[None][j] = copy.copy(k)

            self.__scan_unit_connections()

            for j in self.connections_set:
                self.Data_File[None][j] = {None: self.connections_set[j]}

    def __prepare_capexEquations(self):
        """
        Description
        ----------

        First adds Linearization Intervals, based on input (fine,average, rough).
        Afterwards, Caluculates piece-wise linear CAPEX for every Process Unit.
        At last calculates annual Cost Factor which is needed in the Model



        """

        self.add_linearisationIntervals()

        self.__calc_capexLinearizationParameters()

        self.__calc_accFactorParameter()

        self.__set_optionalFLH()

        self.__set_optionalKOM()

        self.__set_turnoverParameter()

    def __prepare_heatEquations(self):
        """
        Description
        -----------
        Fills Temperature Grid and calculates Heat Utility costs of different
        Heat intervals by calling:

            - add_ProcessTemperatures()
            - __add_temperatureIntervals()
            - __set_deltaQ()



        """

        self.__set_processTemperatures()

        self.__add_temperatureIntervals()

        self.__calc_heatPump()

        self.__set_deltaQ()

        self.__fill_betaParameters()

    # UNDER CONSTRUCTION --> Later input via predefined databases

    def load_data_from_txt(self, txt_name=None):
        try:
            f = open(txt_name, 'r')
            data = f.read()
            f.close()
            self.Data_File = eval(data)
        except:
            pass

    def add_DataBase(self, txt_file):
        self.Database = txt_file

    # ------

    # Create Data File
    # -----------------

    def create_DataFile(self):
        """
        Description
        -----------
        First prepares Data for Heatbalances (T-Grid, Costs...)

            - preprace_HeatBalances()


        Afterwards prepares Data for Cost equation (Lin Intervals, Piece-wise
        linear costs...) by callingcalling:

            - __prepare_capexEquations()

        At last creates the Data File for the Superstructure Model by calling:

            - __fill_nonIndexedParameters()
            - __fill_indexedParameters()
            - __fill_processParameterList()
            #


        Returns
        -------
        Data_File:   File with Superstructure Model ready Data

        """

        self.load_data_from_txt(self.Database)

        # heat balances
        self.__prepare_heatEquations()
        # capex equations
        self.__prepare_capexEquations()

        # mass balance equations
        self.__fill_nonIndexedParameters()
        self.__fill_indexedParameters()
        self.__fill_processParameterList()

        return self.Data_File

    def set_unit_uncertainty(self, uncertaintyObject, parameterName, oldDict):
        """"
        This function created the sets needed to define the uncertainty of a unit
        Inputs:
            uncertaintyObject: the object that contains the uncertainty information
            parameterName: the name of the parameter that we want to change
            oldDict: the dictionary that contains the old values of the parameter

        Output:
            newCompostionDict: the dictionary that contains the new values of the parameter
        """

        UncMatrix = uncertaintyObject.UncertaintyMatrix
        ScenarioNames = uncertaintyObject.ScenarioNames
        parameterDict = uncertaintyObject.LableDict[parameterName]

        composition = oldDict
        compostionDict = composition[parameterName]
        newCompostionDict = {parameterName: {}}

        for key, value in compostionDict.items():
            if key in parameterDict.keys():
                # if the variable is in the parameter dictionary, it means that it is a scenario sensitive parameter
                # and we need to change it based on the uncertainty matrix
                columnNameMatrix = parameterDict[key]
                uncertaintySeries = UncMatrix[columnNameMatrix]
                for i, sc in enumerate(ScenarioNames):
                    if not isinstance(key, tuple):
                        # the key is not a tuple in the case of raw material costs and product prices
                        new_tuple = (key, sc)
                    else:
                        new_tuple = key + (sc,)

                    # set the new value of the parameter
                    newValue = value + value * uncertaintySeries[i]
                    if (('split_factor' in parameterName or 'stoich_conversion_factor' in parameterName or 'yield_factor_unit_operation' in parameterName)
                        and newValue > 1):
                        newCompostionDict[parameterName][new_tuple] = 1  # split factors can not be greater than 1
                    else:
                        newCompostionDict[parameterName][new_tuple] = newValue


            else:
                # if the variable is not in the parameter dictionary,
                # it means that the variable does not need to change for the scenarios
                for i, sc in enumerate(ScenarioNames):
                    if not isinstance(key, tuple):
                        # the key is not a tuple in the case of raw material costs and product prices
                        new_tuple = (key, sc)
                    else:
                        new_tuple = key + (sc,)
                    newCompostionDict[parameterName][new_tuple] = value

        return newCompostionDict

    def polish_source_uncertainty(self, newDict, oldDict, uncertaintyObject):
        """
        This function creates the dictionary for the composition of the inlet streams of the source units.
        The difference between set_unit_uncertainty and set_source_uncertainty is that the source units the sum of the
        composition should be 1 So when a composition is change the other compositions should be changed accordingly to
        keep the sum of the component fractions equal to 1. the change is equally distributed between the components that
        are not changed.
        Inputs:
            uncertaintyObject: the object that contains the uncertainty information
            parameterName: the name of the parameter that we want to change
            oldDict: the dictionary that contains the old values of the parameter

        Output:
            newCompostionDict: the dictionary that contains the new values of the parameter
        """
        changeDict = {}
        ScenarioNames = uncertaintyObject.ScenarioNames
        PhiExclusionList = uncertaintyObject.PhiExclusionList
        newDictUnpacked = newDict['component_concentration']
        oldDict = oldDict['component_concentration']
        for sc in ScenarioNames:
            compositionSum = sum(newDictUnpacked[(key[0], key[1], sc)] for key in oldDict.keys())
            if compositionSum != 1:
                changedList = []
                diffList = []
                for key in oldDict.keys():
                    difference = newDictUnpacked[(key[0], key[1], sc)] - oldDict[key]
                    if difference != 0:
                        diffList.append(difference)
                    else:
                        if key not in PhiExclusionList:
                            changedList.append(key)

                for i in changedList:
                    updatedValue = oldDict[i] + sum(diffList) / len(changedList)
                    # todo the massbalances should be modified. It is possible that the updated value is
                    #  negative which is physically not possible, for simplicity we set it to 0 but this does not comply
                    #  with the conservation of mass

                    if updatedValue < 0:
                        updatedValue = 0

                    changeDict[(i[0], i[1], sc)] = updatedValue

        # update the newDict with the changeDict values
        for keys in changeDict.keys():
            newDict['component_concentration'][keys] = changeDict[keys]

        return newDict

    def set_uncertainty_data(self, uncertaintyObject):
        """
        Sets the parameters of the units based on the uncertainty object
        Inputs:
            uncertaintyObject: the object that contains the uncertainty information
        Output:
            Updated units list
        """
        # set the list of Scenarios so the set can be declared in pyomo
        self.Scenarios = {'SC': uncertaintyObject.ScenarioNames}
        self.Odds = {'odds': {sc: uncertaintyObject.ScenarioProbabilities[i]
                              for i, sc in enumerate(uncertaintyObject.ScenarioNames)}}

        for unit in self.UnitsList:

            if unit.Type == "ProductPool":

                # update the product prices
                newPriceDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='ProductPrice',
                                                         oldDict=unit.ProductPrice)
                unit.ProductPrice = newPriceDict

            elif unit.Type == "Source":

                # update the composition
                newCompostionDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                              parameterName='component_concentration',
                                                              oldDict=unit.Composition)

                # update the composition to keep the sum of the fractions equal to 1
                polishedDict = self.polish_source_uncertainty(newDict=newCompostionDict,
                                                              oldDict=unit.Composition,
                                                              uncertaintyObject=uncertaintyObject)

                unit.Composition = polishedDict

                # update the material cost prices
                newPriceDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='material_costs',
                                                         oldDict=unit.MaterialCosts)
                unit.MaterialCosts = newPriceDict

            elif unit.Type == "Distributor":
                newDistributionDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                                parameterName='decimal_numbers',
                                                                oldDict=unit.decimal_numbers)
                unit.decimal_numbers = newDistributionDict

            elif unit.Type == "PhysicalProcess":
                newSplitDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='split_factor',
                                                         oldDict=unit.split_factor)
                unit.split_factor = newSplitDict


            elif unit.Type == "Stoich-Reactor":
                # here we need to change 3 paramerter:
                # 1) split_factor (splitfactor)
                newSplitDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='split_factor',
                                                         oldDict=unit.split_factor)
                unit.split_factor = newSplitDict

                # 2) stoich_reaction_coefficient (stoichiometry)
                newGammaDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='stoich_reaction_coefficient',
                                                         oldDict=unit.stoich_reaction_coefficient)
                unit.stoich_reaction_coefficient = newGammaDict

                # 3) stoich_conversion_factor (conversion)
                newThetaDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='stoich_conversion_factor',
                                                         oldDict=unit.stoich_conversion_factor)
                unit.stoich_conversion_factor = newThetaDict

            elif unit.Type == "Yield-Reactor":
                # modify the split factor
                newSplitDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='split_factor',
                                                         oldDict=unit.split_factor)
                unit.split_factor = newSplitDict

                # 2) modify the yield_factor_unit_operation (yield)
                newXiDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                      parameterName='yield_factor_unit_operation',
                                                      oldDict=unit.yield_factor_unit_operation)
                unit.yield_factor_unit_operation = newXiDict

            elif unit.Type == "HeatGenerator" or unit.Type == "ElectricityGenerator" or unit.Type == "CombinedHeatAndPower":
                # update the split factors
                newSplitDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='split_factor',
                                                         oldDict=unit.split_factor)
                unit.split_factor = newSplitDict

                # update the stoich_reaction_coefficient
                newGammaDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='stoich_reaction_coefficient',
                                                         oldDict=unit.stoich_reaction_coefficient)
                unit.stoich_reaction_coefficient = newGammaDict

                # update the stoich_conversion_factor
                newThetaDict = self.set_unit_uncertainty(uncertaintyObject=uncertaintyObject,
                                                         parameterName='stoich_conversion_factor',
                                                         oldDict=unit.stoich_conversion_factor)
                unit.stoich_conversion_factor = newThetaDict

            else:
                raise ValueError("The unit type {} is not recognized".format(unit.Type))

        print("Uncertainty data is set")

    # --------------------------------------------------------------------------------------------------------------
    # Methods for mpi-sppy
    # --------------------------------------------------------------------------------------------------------------
    def set_uncertainty_data_mpisspy(self, uncertaintyObject):
        """
         In this function, we set the uncertainty data for the mpisspy model based on the uncertainty object. mpi-sppy
         is a parallel implementation of stochastic programming. The function is similar to the set_uncertainty_data

        :param uncertaintyObject:
        :return: scearioDataFiles: a dictionary that contains the data files for each scenario
        """

        # set the list of Scenarios so the set can be declared in pyomo
        self.Scenarios = {'SC': uncertaintyObject.ScenarioNames}
        self.Odds = {'odds': {sc: uncertaintyObject.ScenarioProbabilities[i]
                              for i, sc in enumerate(uncertaintyObject.ScenarioNames)}}

        # uncertainty data
        uncertaintyMatrix = uncertaintyObject.UncertaintyMatrix
        uncertaintyDict = self.invert_dictionary(uncertaintyObject.LableDict)
        phiExcludeList = uncertaintyObject.PhiExclusionList

        # make the base case data_file of the model
        baseCaseDataFile = self.create_DataFile()
        unitNames = baseCaseDataFile[None]['names']

        scenarioDataFiles = {}
        newUncertaintyMatrix = pd.DataFrame()

        for rowIndex, scenario in enumerate(self.Scenarios['SC']):
            dataFileScenario = copy.deepcopy(baseCaseDataFile)
            adjustedPhiDict = {}
            # get the row of the uncertaintyMatrix corresponding to the rowIndex (int)
            row = uncertaintyMatrix.iloc[rowIndex]
            # loop over each row of the uncertainty matrix

            for j, value in row.items():
                # Split the string by the last underscore and remove it
                parameterName = '_'.join(j.split('_')[:-1])

                index = uncertaintyDict[parameterName][j]
                # get the basecase value of the parameter
                currentValue = baseCaseDataFile[None][parameterName][index]
                # get the value of the parameter for the current scenario
                newValue = currentValue * (1 + value)

                # constrain to be equal to 1, otherwise mass balance problems will occur
                constrained_parameters = ('split_factor', 'stoich_conversion_factor', 'stoich_reaction_coefficient', 'component_concentration', 'yield_factor_unit_operation')
                if parameterName in constrained_parameters:
                    if newValue > 1:
                        newValue = 1  # constrain to be equal to 1, otherwise mass balance problems will occur

                # make a new column name, depending on the parameter name
                if parameterName == 'specific_heat_demand':
                    unitNumber = index[1]  # unit number is the second element of the index tuple
                    columnName = parameterName + ' ' + str(unitNames[unitNumber])

                elif parameterName == 'delta_ut':
                    columnName = 'ElectricityPrice'

                elif isinstance(index, tuple):
                    unitNumber = index[0]
                    compound = str(index[1])
                    columnName = parameterName + ' ' + str(unitNames[unitNumber]) + ' ' + compound

                else:
                    # the index is not a tuple in the case of raw material costs and product prices
                    columnName = parameterName + '_' + str(unitNames[index])

                newUncertaintyMatrix.at[rowIndex, columnName] = newValue

                # update the data file with the new value
                dataFileScenario[None][parameterName][index] = newValue
                # keep a dictionary of the compostition of the source units, so later the other fractions can be updated
                # so the sum of the fractions is equal to 1
                if parameterName == 'component_concentration':  # component_concentration being the parameter name for the composition of the source units
                    adjustedPhiDict[index] = newValue

                # update the composition of the source units to keep the sum of the fractions equal to 1, do this for each scenario
                if adjustedPhiDict:
                    dataFileScenario = self.adjust_phi_data(adjustedPhiDict, dataFileScenario, baseCaseDataFile,
                                                            phiExcludeList)

            scenarioDataFiles[scenario] = dataFileScenario

        # add the new uncertainty matrix, dataFiles and stochasticMode to the superstructure object
        self.uncertaintyMatrix = newUncertaintyMatrix
        self.scenarioDataFiles = scenarioDataFiles
        self.stochasticMode = 'mpi-sppy'
        #print('pause')
        return scenarioDataFiles

    def invert_dictionary(self, originalDict):
        """
        Inverts the keys and values of the given dictionary, allowing for non-unique values.
        If a value is not unique or unhashable, the resulting key will map to a list of original keys.

        Parameters:
        originalDict (dict): The dictionary to be inverted.

        Returns:
        dict: A new dictionary with values as keys and original keys as values (lists in case of duplicates).
        """
        invertedDict = {}
        for key, dict in originalDict.items():
            subInvertedDict = {}
            for sub_key, value in dict.items():
                if value not in invertedDict:
                    subInvertedDict[value] = sub_key
                    invertedDict[key] = subInvertedDict
        return invertedDict

    def adjust_phi_data(self, adjustedPhiDict, dataFile, baseCaseDataFile, phiExcludeList):
        """
           Adjust the composition of the source units to keep the sum of the fractions equal to 1.

           This method modifies the data file of the model by adjusting the composition of the source units
           based on the new values provided in `adjustedPhiDict`. The sum of the fractions for the source
           units is maintained at 1. Certain sources can be excluded from adjustment as specified in
           `phiExcludeList`.

           Parameters:
           ----------
           adjustedPhiDict : dict
               A dictionary containing the new values of the parameter `component_concentration` for each source unit.
               The keys are the source unit identifiers, and the values are the new `component_concentration` values.

           dataFile : dict
               The data file of the model that will be adjusted.

           baseCaseDataFile : dict
               The base case data file of the model, used as a reference.

           phiExcludeList : list
               A list of source components identifiers that should be excluded from the adjustment process.

           Returns:
           -------
           dataFileAdjusted : dict
               The data file of the model with the updated composition of the source units.
           """

        def split_dictionary(instance):
            """
            spilt dictionary for each source unit (indicated by the first element of the key)
            """
            if isinstance(instance, dict):
                splitDict = {}
                for key, value in instance.items():
                    if key[0] not in splitDict:
                        splitDict[key[0]] = {}
                    splitDict[key[0]][(key[0], key[1])] = value
                return splitDict

            elif isinstance(instance, list):
                splitDict = {}
                for key in instance:
                    if key[0] not in splitDict:
                        splitDict[key[0]] = []
                    splitDict[key[0]].append(key)
                return splitDict

        def reajust_composition(originalSourceDict, newPhiDict, toAdjustDict):
            """
            Re-adjusts the composition of source units to ensure the sum of fractions equals 1.

            This function takes the original composition of source units, applies new adjustments to certain
            compounds, and ensures the total composition remains consistent at 100%. It handles cases where
            certain compounds should not be adjusted based on an exclusion criterion.

            Parameters:
            ----------
            originalSourceDict : dict
                Dictionary containing the original composition of the source units.
                Keys are source unit identifiers, and values are dictionaries with compounds and their fractions.

            newPhiDict : dict
                Dictionary containing the new adjusted values for the source units.
                Keys are source unit identifiers, and values are dictionaries with compounds and their new fractions.

            toAdjustDict : dict
                Dictionary specifying which parts of the composition need to be adjusted for each source unit.
                Keys are source unit identifiers, and values are dictionaries with compounds and their fractions that need adjustment.

            Returns:
            -------
            dict
                A dictionary with the adjusted composition of the source units, where the total fraction for each unit is equal to 1.

            Raises:
            ------
            ValueError
                If the total new percentages exceed 100% or if the new percentages are too high and cannot be adjusted to 100%.

            """
            returnDict = {}

            for unit in newPhiDict:
                # get the original composition of the source unit
                originalComposition = originalSourceDict[unit]
                # get the new composition of the source unit
                newComposition = newPhiDict[unit]
                # get the composition of the source unit that needs to be adjusted
                toAdjustComposition = toAdjustDict[unit]

                adjustDict = {}
                for compound in toAdjustComposition:
                    if compound not in newComposition:
                        # these compounds are from the excluded list, so they should not be adjusted!
                        # keep the original values in other words
                        adjustDict.update({compound: originalComposition[compound]})
                    else:
                        # these compounds are changed due to uncertainty
                        adjustDict.update({compound: newComposition[compound]})

                totalAdjusted = sum(adjustDict.values())
                if totalAdjusted > 1:
                    raise ValueError("Total new percentages exceeds 100 %")

                totalOtherComponents = sum(originalComposition.values()) - sum(
                    originalComposition[idx] for idx in adjustDict.keys())
                totalNewOtherComponents = 1 - totalAdjusted

                if totalNewOtherComponents < 0:
                    raise ValueError("New percentages are too high, total cannot exceed 100%")

                    # Calculate adjustment factor
                adjustmentFactor = totalNewOtherComponents / totalOtherComponents if totalOtherComponents != 0 else 0

                # Adjust the composition of the source unit
                addDict = {
                    i: originalComposition[i] * adjustmentFactor if i not in adjustDict else adjustDict[i]
                    for i in originalComposition
                }

                returnDict.update(addDict)
                check = sum(addDict.values())
                if check > 1.000000001:
                    raise ValueError("Total new percentages exceeds 100 %, please check for errors")

            return returnDict

        # -------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------

        # get the original source dictionary
        originalSourceDict = baseCaseDataFile[None]['component_concentration']
        sourceDict = split_dictionary(originalSourceDict)

        # get the adjusted source dictionary and split it
        newPhiDict = split_dictionary(adjustedPhiDict)

        # get the adjusted source list
        adjustedPhiList = list(adjustedPhiDict.keys()) + phiExcludeList  # add the excluded sources to the list
        adjustedPhiDict = split_dictionary(adjustedPhiList)

        dictNewCompositions = reajust_composition(originalSourceDict=sourceDict,
                                                  newPhiDict=newPhiDict,
                                                  toAdjustDict=adjustedPhiDict)

        for key in dictNewCompositions:
            dataFile[None]['component_concentration'][key] = dictNewCompositions[key]

        return dataFile

        #for source, dict in sourceDict.items():

    def check_uncertainty_data(self):
        """
        check the uncertainty data by printing the min, max, and mean of each uncertain parameter

        :return: prints the min, max, and mean of each uncertain parameter
        """
        uncertaintyMatrix = self.uncertaintyMatrix
        print('')
        # print in blue color
        print('\033[94m' + 'Uncertainty Data' + '\033[0m')
        print('Printing the min, max, and mean of each uncertain parameter\n')
        for column in uncertaintyMatrix.columns:
            print(column)
            print('min:', uncertaintyMatrix[column].min())
            print('mean:', uncertaintyMatrix[column].mean())
            print('max:', uncertaintyMatrix[column].max())
            print('---------------------------------')
