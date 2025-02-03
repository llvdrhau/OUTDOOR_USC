import pickle


class SuperstructureFrame():
    def __init__(self):

        self.MainProduct = ""
        self.ProductLoad = {'product_load': 0}
        self.objective = ""
        self.productDriver = "no"
        self.OptimimizationMode = ""
        self.ModelName = ""

        # uncertainty parameters for the stochastic problem. filled in if stochastic problem is solved
        self.uncertaintyDict = {}

        # if using mpi-sspy the dictionary is filled with the scenario data files
        self.scearioDataFiles = {}
        self.stochasticMode = None
        self._dataStochastic = None

        # Lists for sets
        # -----

        # Unit Operations
        # ----------------
        self.UnitsList = []
        self.UnitsNumberList = {'UNIT_PROCESSES': []}  # All units
        self.UnitsNumberList2 = {'UU': []}  # All units minus inputs
        self.StoichRNumberList = {'STOICH_REACTORS': []}
        self.YieldRNumberList = {'YIELD_REACTORS': []}
        self.SplitterNumberList = {'SPLITTERS': []}
        self.HeatGeneratorList = {'FURNACES': []}
        self.ElectricityGeneratorList = {'TURBINES': []}
        self.ProductPoolList = {'PRODUCT_POOLS': []}  # Outputs
        self.CostUnitsList = {'COSTED_UNIT_OPERATIONS': []}  # Costs of your inputs
        self.SourceList = {'RAW_MATERIAL_SOURCES': []}  # Sources
        self.SourceSet = {'CONNECTED_RAW_MATERIAL_UNIT_OPERATION': []}  #
        self.YieldSubSet = {'YIELD_REACTOR_COMPONENTS': []}  #
        self.distributor_subset = {'PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS': []}
        self.distributor_list = {'DISTRIBUTORS': []}
        self.decimal_set = {'DISTRIBUTOR_DECIMAL_SET': []}
        self.distributor_subset2 = {'DISTRIBUTOR_DECIMAL_SUBSET': []}

        self.connections_set = {'UNIT_CONNECTIONS': []}
        self.Scenarios = {'SC': []}  # Stochastic, maybe redundant
        self.Odds = {'odds': []}  # Prolly stochastic modeling too

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

        # - Output data structures
        # ------------------------
        self.Data_File = {None: {}}
        self.NI_ParameterList = []
        self.I_ParameterList = []

    def constructSuperstructureFrame(self, centralDataManager):
        """
        Construct the superstructure frame from the central data manager

        :param centralDataManager:
        :return:
        """
        # start general system data
        self.MainProduct = centralDataManager.generalData['MainProduct']

        pass
    def save_frame(self):
        try:
            filename = "data/frames/" + self.ModelName + ".pkl"
            with open(filename, 'wb') as outfile:
                pickle.dump(self, outfile)
            print(self)
        except Exception as e:
            print("Error while saving frame: " + e.__str__())
