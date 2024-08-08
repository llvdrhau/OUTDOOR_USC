import pickle


class SuperstructureFrame():
    def __init__(self):
        self.MainProduct = ""
        self.ProductLoad = {'ProductLoad': 0}
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
        self.UnitsNumberList = {'U': []}  # All units
        self.UnitsNumberList2 = {'UU': []}  # All units minus inputs
        self.StoichRNumberList = {'U_STOICH_REACTOR': []}
        self.YieldRNumberList = {'U_YIELD_REACTOR': []}
        self.SplitterNumberList = {'U_SPLITTER': []}
        self.HeatGeneratorList = {'U_FUR': []}
        self.ElectricityGeneratorList = {'U_TUR': []}
        self.ProductPoolList = {'U_PP': []}  # Outputs
        self.CostUnitsList = {'U_C': []}  # Costs of your inputs
        self.SourceList = {'U_S': []}  # Sources
        self.SourceSet = {'U_SU': []}  #
        self.YieldSubSet = {'YC': []}  #
        self.distributor_subset = {'U_DIST_SUB': []}
        self.distributor_list = {'U_DIST': []}
        self.decimal_set = {'DC_SET': []}
        self.distributor_subset2 = {'U_DIST_SUB2': []}

        self.connections_set = {'U_CONNECTORS': []}
        self.Scenarios = {'SC': []}  # Stochastic, maybe redundant
        self.Odds = {'odds': []}  # Prolly stochastic modeling too

        # ------------------

        # Heat Balance and Utilities
        # --------------------------
        self.HeatIntervalList = {'HI': []}
        self.HeatUtilitiesList = {'H_UT': []}
        self.Heat_Temperatures = []
        self.HeatIntervals = {}
        self.UtilitiesList = {'UT': []}
        self.OtherUtilitiesList = {'U_UT': []}
        # ---------------------------

        # Others
        # ----------
        self.ComponentsList = {'I': []}
        self.ReactionsList = {'R': []}
        self.ReactantsList = {'M': []}

        self.LinPointsList = {'J': []}
        self.LinIntervalsList = {'JI': []}
        self.UnitNames = {'Names': {}}
        self.UnitNames2 = {'Names': {}}  # for the grafical representation
        # --------------

        self.groups = dict()
        self.connections = dict()

        # Databased input load (UNDER CONSTRUCTION)

        self.Database = None

        # Heat pump variables
        # -------------------
        self.HP_Costs = {'HP_Costs': 0}
        self.HP_ACC_Factor = {'HP_ACC_Factor': 0}
        self.COP_HP = {'COP_HP': 3}
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
        self.lhv = {'LHV': {}}
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

    def save_frame(self):
        try:
            filename = "data/frames/" + self.ModelName + ".pkl"
            with open(filename, 'wb') as outfile:
                pickle.dump(self, outfile)
            print(self)
        except Exception as e:
            print("Error while saving frame: " + e.__str__())
