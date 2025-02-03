from pyomo.environ import *


# noinspection PyAttributeOutsideInit
class HumanstructureModel(AbstractModel):
    """
    Class description
    -----------------

    This is a literal copy of optimization_model.py but Mias is renaming every single variable and param to something human-readable.

    """

    def __init__(self, superstructure_input=None, fixedDesign=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if superstructure_input is not None:
            self._set_optionals_from_superstructure(superstructure_input)
        else:
            self._set_optionals_from_external(kwargs)

        # if True, the model will make the binary variables parameters for flow choice, therefore fixing the design of
        # the flow-sheet
        self._fixedDesign = fixedDesign

    def _set_optionals_from_superstructure(self, superstructure_input):
        """
        Parameters
        ----------
        superstructure_input : Superstructure Object

        Description
        -----------
        uses a superstructure object to optionals which are:
                - Heat pump implementation (active/TIN/TOUT)
                - Additional logics (Groups/forces connections)
                - Objective name (NPC/NPE/NPFWD)
        """

        # self.productDriven = superstructure_input.productDriven.lower()
        self.loadType = superstructure_input.loadType

        # list of impact categories should be the same as the set created in the model, see self.IMPACT_CATEGORIES
        self.impact_categories_list = superstructure_input.ImpactCategories['IMPACT_CATEGORIES']

        if superstructure_input.HP_active:
            self.heat_pump_options = {
                "active": superstructure_input.HP_active,
                "t_in": superstructure_input.HP_T_IN["Interval"],
                "t_out": superstructure_input.HP_T_OUT["Interval"],
            }
        else:
            self.heat_pump_options = {
                "active": superstructure_input.HP_active,
                "t_in": 0,
                "t_out": 0}

        self.objective_name = superstructure_input.objective
        self.groups = superstructure_input.groups
        self.connections = superstructure_input.connections

        self.loadID = None
        if self.loadType:  # if it's product or substrate load
            loadName = superstructure_input.loadName
            for unit in superstructure_input.UnitsList:
                if unit.Name == loadName:
                    self.loadID = unit.Number

            if not self.loadID:
                raise ValueError('The load Name {} is not valid, check if it is correctly written in the excel '
                                 'file'.format(loadName))
        else:
            self.loadID = None
        # checkList = []
        # for i in superstructure_input.UnitsList:
        #     if i.Type == "ProductPool" and i.ProductType == "MainProduct":
        #         self.main_pool = i.Number
        #         checkList.append(i.Number)
#
        # # create warning if more than one main product pool is defined and the model is product driven
        # if len(checkList) > 1 and self.loadType == 'Product':
        #     raise ValueError("There is more than one product pool defined as the mainProduct. "
        #                      "Please check the superstructure inputs and select only one main product if the process is"
        #                      "Product driven (see general data tab).")
#
        # if len(checkList) == 0 and self.loadType == 'Product':
        #     raise ValueError("There is no main product pool defined. Please check the superstructure inputs and select "
        #                      "one main product if the process is Product driven (see general data tab).")

    def _set_options_from_external(self, **kwargs):
        print("There is no external parsing implemented at the moment.")


    def create_ModelEquations(self):
        """
        Description
        -------
        Calls single methods to build the model in the order:
            - Sets
            - Mass balances
            - Energy balances
            - Economic functions
            - GWP functions
            - FWD functions
            - Logics
            - Objective function
        """

        self.create_Sets()
        self.create_MassBalances()
        self.create_EnergyBalances()
        self.create_WasteCosts()
        self.create_EconomicEvaluation()
        self.create_EnvironmentalEvaluation()
        self.create_FreshwaterEvaluation()
        self.create_DecisionMaking()
        self.create_ObjectiveFunction()
        self.create_LCAEquations()

    def populateModel(self, Data_file):
        """
        Parameters
        ----------
        Data_file : Dictionary
            Model data in AbstractModel readable file

        Returns
        -------
        PYOMO ConcreteModel
            filled model instance with equations from SuperstructureModel and
            data from Data_file.

        """
        self.ModelInstance = self.create_instance(Data_file)
        return self.ModelInstance

    # Pyomo Model Methods
    # --------------------

    # **** SETS  ****
    # ----------------

    def create_Sets(self):
        """
        Description
        -------
        Creates all needed Sets for the model including, unit operations, components,
        utilities, reactions, heat intervals etc.

        """

        # Process Unit operations
        # -------------
        self.UNIT_PROCESSES = Set()
        self.UU = Set(within=self.UNIT_PROCESSES)
        self.STOICH_REACTORS = Set(within=self.UNIT_PROCESSES)
        self.YIELD_REACTORS = Set(within=self.UNIT_PROCESSES)
        self.SPLITTERS = Set(within=self.UNIT_PROCESSES)
        self.TURBINES = Set(within=self.UNIT_PROCESSES)
        self.FURNACES = Set(within=self.UNIT_PROCESSES)
        self.PRODUCT_POOLS = Set(within=self.UNIT_PROCESSES)
        self.COSTED_UNIT_OPERATIONS = Set(within=self.UNIT_PROCESSES)
        self.RAW_MATERIAL_SOURCES = Set(within=self.UNIT_PROCESSES)
        self.CONNECTED_RAW_MATERIAL_UNIT_OPERATION = Set(within=self.RAW_MATERIAL_SOURCES * self.UNIT_PROCESSES)
        self.DISTRIBUTORS = Set(within=self.UNIT_PROCESSES)
        self.PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS = Set(within=self.DISTRIBUTORS * self.UNIT_PROCESSES)
        self.UNIT_CONNECTIONS = Set(within=self.UNIT_PROCESSES * self.UNIT_PROCESSES)

        # waste Management
        self.WASTE_MANAGEMENT_TYPES = Set(initialize=["Incineration", "Landfill", "WWTP"])

        # impact categories of life cycle assessment
        self.IMPACT_CATEGORIES = Set(initialize=["GWP"])

        # Components
        # ----------
        self.COMPONENTS = Set()
        self.REACTANTS = Set(within=self.COMPONENTS)
        self.YIELD_REACTOR_COMPONENTS = Set(within=self.YIELD_REACTORS * self.COMPONENTS)

        # Reactions, Utilities, Heat intervals
        # ------------------------------------
        self.REACTIONS = Set()
        self.UTILITIES = Set()
        self.HEATING_COOLING_UTILITIES = Set(within=self.UTILITIES)
        self.ENERGY_UTILITIES = Set(within=self.UTILITIES)
        self.HEAT_INTERVALS = Set()

        # Piece-Wise Linear CAPEX
        # -----------------------
        self.J = Set()
        self.JI = Set(within=self.J)

        # Distributor Set for decimal numbers

        def iterator(x):
            nlist = []
            for i in range(x):
                nlist.append(i)
            return nlist

        self.DC_SET = Set(within=self.DISTRIBUTORS * iterator(100))
        #TODO What cursed thing happened such that this was the way to go?
        self.U_DIST_SUB2 = Set(within=self.PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS * self.DISTRIBUTORS * iterator(100))

    # **** MASS BALANCES *****
    # -------------------------

    def create_MassBalances(self):
        """
        Description
        -------
        This method creates the PYOMO parameters and variables
        that are necessary for the general Mass Balances (eg. FLOWS, PHI, MYU etc.).
        Afterwards Masse Balance Equations are written as PYOMO Constraints.

        """

        # Parameter
        # ---------
        self.ProductLoad = Param(initialize=1, mutable=True)
        self.SubstrateLoad = Param(initialize=1, mutable=True)
        self.sourceOrProductLoad = Param(initialize=1, mutable=True)

        # Flow parameters (Split factor, concentrations, full load hours)
        self.split_factor = Param(self.UNIT_CONNECTIONS, self.COMPONENTS, initialize=0, mutable=True)
        self.concentration = Param(self.UNIT_PROCESSES, initialize=0, within=Any, mutable=True)
        self.full_load_hours = Param(self.UNIT_PROCESSES, mutable=True)
        self.min_production = Param(self.PRODUCT_POOLS, initialize=0, mutable=True)
        self.max_production = Param(self.PRODUCT_POOLS, initialize=100000, mutable=True)


        # Reaction parameters(Stoich. / Yield Coefficients)
        self.stoich_reaction_coefficient = Param(self.STOICH_REACTORS, self.COMPONENTS, self.REACTIONS, initialize=0, mutable=True)
        self.stoich_conversion_factor = Param(self.STOICH_REACTORS, self.REACTIONS, self.REACTANTS, initialize=0, mutable=True)
        self.yield_factor_unit_operation = Param(self.YIELD_REACTORS, self.COMPONENTS, initialize=0, mutable=True)
        self.ic_on = Param(self.YIELD_REACTORS, initialize=0) #TODO: Figure this one out

        # Additional slack parameters (Flow choice, upper bounds, )
        self.lhs_concentration_bool = Param(self.UNIT_PROCESSES, self.COMPONENTS, initialize=0)
        self.rhs_concentration_bool = Param(self.UNIT_PROCESSES, self.COMPONENTS, initialize=0)
        self.lhs_concentration_calc_mode = Param(self.UNIT_PROCESSES, initialize=3)
        self.rhs_concentration_calc_mode = Param(self.UNIT_PROCESSES, initialize=3)
        self.names = Param(self.UNIT_PROCESSES, within= Any)
        self.upper_bound_big_m_constraint = Param(self.UNIT_PROCESSES, initialize=100000, mutable=True)

        # upper and lower bounds for source flows
        self.raw_materials_upper_bound = Param(self.RAW_MATERIAL_SOURCES, initialize=100000, mutable=True)
        self.raw_materials_lower_bound = Param(self.RAW_MATERIAL_SOURCES, initialize=0, mutable=True)

        # component composition parameters
        self.component_concentration = Param(self.RAW_MATERIAL_SOURCES, self.COMPONENTS, initialize=0, mutable=True)

        # cost parameters
        self.material_costs = Param(self.RAW_MATERIAL_SOURCES, initialize=0, mutable=True)

        # decimal_numbers help to model the distributor equations
        # it sets the degree of "detail" for the distributor
        self.decimal_numbers = Param(self.DC_SET, mutable=True)

        # Variables
        # --------

        self.Flow = Var(self.UNIT_CONNECTIONS, self.COMPONENTS, within=NonNegativeReals)
        self.Inlet = Var(self.UNIT_PROCESSES, self.COMPONENTS, within=NonNegativeReals)
        self.Outlet = Var(self.UNIT_PROCESSES, self.COMPONENTS, within=NonNegativeReals)
        self.Waste = Var(self.UNIT_PROCESSES, self.COMPONENTS, within=NonNegativeReals)
        self.Waste_Total = Var(self.COMPONENTS, within=NonNegativeReals)
        self.FLOW_ADD = Var(self.CONNECTED_RAW_MATERIAL_UNIT_OPERATION, within=NonNegativeReals)
        self.FLOW_ADD_TOT = Var(self.UNIT_PROCESSES, self.COMPONENTS, within=NonNegativeReals)
        self.FLOW_SUM = Var(self.UNIT_PROCESSES, within=NonNegativeReals)
        self.FLOW_SOURCE = Var(self.RAW_MATERIAL_SOURCES, within=NonNegativeReals)
        self.FLOW_DIST = Var(self.U_DIST_SUB2, self.COMPONENTS, within=NonNegativeReals)
        self.FLOW_FT = Var(self.UNIT_CONNECTIONS, within=NonNegativeReals)

        # to get the fractions that the stream is split into for each DISTRIBUTORS to UNIT_PROCESSES (that is connected)
        # this is used as a variable for the second stage of the stochastic model to get the distribution factor
        # equal over all scenarios
        self.DistFraction = Var(self.PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS, within=NonNegativeReals)

        # Binary Variables for flow choice also 1ste Stage Variables of the stochastic models!
        if self._fixedDesign:
            # Binary but can be any value to avoid errors (for values which aren't exactly 0 or 1)
            self.Y = Param(self.UNIT_PROCESSES, within=AnyWithNone)
            self.Y_DIST = Param(self.U_DIST_SUB2, within=AnyWithNone)
        else:
            self.Y = Var(self.UNIT_PROCESSES, within=Binary)
            self.Y_DIST = Var(self.U_DIST_SUB2, within=Binary)


        # Constraints
        # -----------

        def MassBalance_1_rule(self, u, i):
            return self.Inlet[u, i] == self.Total_Raw_Material_Input[u, i] + sum(self.full_load_hours[uu] / self.full_load_hours[u] * self.Flow[uu, u, i] for uu in self.UU if (uu, u) in self.UNIT_CONNECTIONS)

        def MassBalance_2_rule(self, u, i):
            return self.Total_Raw_Material_Input[u, i] == sum(
                self.Raw_Material_Input[u_s, u] * self.component_concentration[u_s, i]
                for u_s in self.RAW_MATERIAL_SOURCES
                if (u_s, u) in self.CONNECTED_RAW_MATERIAL_UNIT_OPERATION
            )

        def MassBalance_3_rule(self, u_s, u):
            return self.Raw_Material_Input[u_s, u] <= self.upper_bound_big_m_constraint[u] * self.y[u]  # Big REACTANTS constraint

        def MassBalance_4_rule(self, u_s):
            return self.Raw_Material_Input_Source[u_s] == sum(
                self.Raw_Material_Input[u_s, u] * self.full_load_hours[u] / self.full_load_hours[u_s]
                for u in self.UNIT_PROCESSES
                if (u_s, u) in self.CONNECTED_RAW_MATERIAL_UNIT_OPERATION
            )
         # upper and lower bounds for source flows
        def MassBalance_13_rule(self, u_s):
            # bounds defined in tons per year (t/h) hence flow times full loading hours
            if u_s == self.loadID and self.loadType == 'Substrate':
                return self.Raw_Material_Input_Source[self.loadID] <= self.source_or_product_load / self.H
            else:
                return self.Raw_Material_Input_Source[u_s] <= self.raw_materials_upper_bound[u_s]

        def MassBalance_14_rule(self, u_s):
            # bounds defined in tons per year (t/a) hence flow times full loading hours
            if u_s == self.loadID and self.loadType == 'Substrate':
                return self.Raw_Material_Input_Source[self.loadID] >= self.source_or_product_load / self.H
            else:
                return self.Raw_Material_Input_Source[u_s] >= self.raw_materials_lower_bound[u_s]

        def MassBalance_15_rule(self):
            if self.loadType == 'Substrate':
                # if the optimisation is substrate driven the mass flow is predefined, load is in tons/year
                return self.Raw_Material_Input_Source[self.loadID] == self.source_or_product_load / self.H # in tons/h
            else:
                return Constraint.Skip

        # stoichimoetric and yield reactor equations
        def MassBalance_5_rule(self, u, i):
            if u in self.YIELD_REACTORS:
                if self.ic_on[u] == 1:
                    if (u, i) in self.YIELD_REACTOR_COMPONENTS:
                        return (
                            self.Outlet[u, i]
                            == self.Inlet[u, i]
                            + sum(
                                self.Inlet[u, i]
                                for i in self.COMPONENTS
                                if (u, i) not in self.YIELD_REACTOR_COMPONENTS
                            )
                            * self.yield_factor_unit_operation[u, i]
                        )
                    else:
                        return (
                            self.Outlet[u, i]
                            == sum(
                                self.Inlet[u, i]
                                for i in self.COMPONENTS
                                if (u, i) not in self.YIELD_REACTOR_COMPONENTS
                            )
                            * self.yield_factor_unit_operation[u, i]
                        )
                else:
                    return (
                        self.Outlet[u, i]
                        == sum(self.Inlet[u, i] for i in self.COMPONENTS) * self.yield_factor_unit_operation[u, i]
                    )
            elif u in self.STOICH_REACTORS:
                return self.Outlet[u, i] == self.Inlet[u, i] + sum(
                    self.stoich_reaction_coefficient[u, i, r] * self.stoich_conversion_factor[u, r, m] * self.Inlet[u, m]
                    for r in self.REACTIONS
                    for m in self.REACTANTS
                )
            else:
                return self.Outlet[u, i] == self.Inlet[u, i]

        def MassBalance_9_rule(self, u, i):
            return self.Waste[u, i] == self.Outlet[u, i] - sum(
                self.Flow[u, uu, i] for uu in self.UU if (u, uu) in self.UNIT_CONNECTIONS
            )

        def MassBalance_10_rule(self, i):
            return self.Total_Waste[i] == sum(
                self.Waste[u, i] for u in self.UNIT_PROCESSES
            )

        # concentration constraints
        def MassBalance_11_rule(self, u):
            if self.lhs_concentration_calc_mode[u] == 0 and self.rhs_concentration_calc_mode[u] == 0:
                return 1e03 * sum(
                    self.Outlet[u, i] * self.lhs_concentration_bool[u, i] for i in self.COMPONENTS
                ) == 1e03 * self.concentration[u] * sum(
                    self.Outlet[u, i] * self.rhs_concentration_bool[u, i] for i in self.COMPONENTS
                )
            elif self.lhs_concentration_calc_mode[u] == 0 and self.rhs_concentration_calc_mode[u] == 1:
                return 1e03 * sum(
                    self.Outlet[u, i] * self.lhs_concentration_bool[u, i] for i in self.COMPONENTS
                ) == 1e03 * self.concentration[u] * sum(
                    self.Inlet[u, i] * self.rhs_concentration_bool[u, i] for i in self.COMPONENTS
                )
            elif self.lhs_concentration_calc_mode[u] == 1 and self.rhs_concentration_calc_mode[u] == 0:
                return (1e03 * sum(
                    self.Inlet[u, i] * self.lhs_concentration_bool[u, i] for i in self.COMPONENTS)
                        == 1e03 * self.concentration[u] * sum(
                        self.Outlet[u, i] * self.rhs_concentration_bool[u, i] for i in self.COMPONENTS
                ))
            elif self.lhs_concentration_calc_mode[u] == 1 and self.rhs_concentration_calc_mode[u] == 1:
                return 1e03 * sum(self.Inlet[u, i] * self.lhs_concentration_bool[u, i] for i in self.COMPONENTS) == 1e03 * self.concentration[u] * sum(self.Inlet[u, i] * self.rhs_concentration_bool[u, i] for i in self.COMPONENTS)
            else:
                return Constraint.Skip

        def MassBalance_12_rule(self, u):
            return self.Flow_Sum[u] == sum(self.Inlet[u, i] for i in self.COMPONENTS)

        # min max production constraints for product pools
        def MassBalance_14a_rule(self, up):
            # bounds defined in tons per year (t/a) hence flow times full loading hours
            return self.Flow_Sum[up] >= self.min_production[up]

        def MassBalance_14b_rule(self, up):
            # bounds defined in tons per year (t/a) hence flow times full loading hours
            return self.Flow_Sum[up] <= self.max_production[up]

        def MassBalance_6_rule(self, u, uu, i):
            if (u, uu) not in self.PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS:
                    if (u, uu) in self.UNIT_CONNECTIONS:
                        return self.Flow[u, uu, i] <= self.split_factor[u, uu, i] * self.Outlet[
                            u, i
                            ] + self.upper_bound_big_m_constraint[u] * (1 - self.y[uu])
                    else:
                        return Constraint.Skip

            else:
                return self.Flow[u, uu, i] <= sum(
                    self.Flow_Distributor_Decimal[u, uu, uk, k, i]
                    for (uk, k) in self.DISTRIBUTOR_DECIMAL_SET
                    if (u, uu, uk, k) in self.DISTRIBUTOR_DECIMAL_SUBSET
                ) + self.upper_bound_big_m_constraint[u] * (1 - self.y[uu])

        def MassBalance_7_rule(self, u, uu, i):
            if (u,uu) in self.UNIT_CONNECTIONS:
                return self.Flow[u, uu, i] <= self.upper_bound_big_m_constraint[u] * self.y[uu]
            else:
                return Constraint.Skip


        def MassBalance_8_rule(self, u, uu, i):
            if (u, uu) not in self.PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS:
                if (u, uu) in self.UNIT_CONNECTIONS:
                    return self.Flow[u, uu, i] >= self.split_factor[u, uu, i] * self.Outlet[
                        u, i
                        ] - self.upper_bound_big_m_constraint[u] * (1 - self.y[uu])
                else:
                    return Constraint.Skip
            else:
                return self.Flow[u, uu, i] >= sum(
                    self.Flow_Distributor_Decimal[u, uu, uk, k, i]
                    for (uk, k) in self.DISTRIBUTOR_DECIMAL_SET
                    if (u, uu, uk, k) in self.DISTRIBUTOR_DECIMAL_SUBSET
                ) - self.upper_bound_big_m_constraint[u] * (1 - self.y[uu])

        # Distributor Equations

        def MassBalance_15a_rule(self, u, uu, uk, k, i):
            return self.Flow_Distributor_Decimal[u, uu, uk, k, i] <= self.decimal_numbers[
                u, k
            ] * self.Outlet[u, i] + self.upper_bound_big_m_constraint[u] * (1 - self.y_distribution[u, uu, uk, k])

        def MassBalance_15b_rule(self, u, uu, uk, k, i):
            return self.Flow_Distributor_Decimal[u, uu, uk, k, i] >= self.decimal_numbers[
                u, k
            ] * self.Outlet[u, i] - self.upper_bound_big_m_constraint[u] * (1 - self.y_distribution[u, uu, uk, k])

        def MassBalance_15c_rule(self, u, uu, uk, k, i):
            return (
                self.Flow_Distributor_Decimal[u, uu, uk, k, i]
                <= self.upper_bound_big_m_constraint[u] * self.y_distribution[u, uu, uk, k]
            )

        def MassBalance_16_rule(self, u, i):
            return self.Outlet[u, i] == sum(
                self.Flow[u, uu, i] for uu in self.UNIT_PROCESSES if (u, uu) in self.PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS
            )

        def MassBalance_17_rule(self, u, uu):
            return self.Total_Flows[u, uu] == sum(self.Flow[u, uu, i] for i in self.COMPONENTS)


        def MassBalance_Distribution_Factor(self, u, uu):
            return self.Distributor_Fraction[u, uu] == sum(self.decimal_numbers[u, k] * self.y_distribution[u, uu, u, k]
                                                           for u1, k in self.DISTRIBUTOR_DECIMAL_SET if u == u1)


        self.MassBalance_1 = Constraint(self.UNIT_PROCESSES, self.COMPONENTS, rule=MassBalance_1_rule)
        self.MassBalance_2 = Constraint(self.UNIT_PROCESSES, self.COMPONENTS, rule=MassBalance_2_rule)
        self.MassBalance_3 = Constraint(self.CONNECTED_RAW_MATERIAL_UNIT_OPERATION, rule=MassBalance_3_rule)
        self.MassBalance_4 = Constraint(self.RAW_MATERIAL_SOURCES, rule=MassBalance_4_rule)
        self.MassBalance_13 = Constraint(self.RAW_MATERIAL_SOURCES, rule=MassBalance_13_rule)
        self.MassBalance_14 = Constraint(self.RAW_MATERIAL_SOURCES, rule=MassBalance_14_rule)
        #self.MassBalance_15 = Constraint(rule=MassBalance_15_rule)

        self.MassBalance_5 = Constraint(self.UNIT_PROCESSES, self.COMPONENTS, rule=MassBalance_5_rule)
        self.MassBalance_6 = Constraint(self.UNIT_PROCESSES, self.UU, self.COMPONENTS, rule=MassBalance_6_rule)
        self.MassBalance_7 = Constraint(self.UNIT_PROCESSES, self.UU, self.COMPONENTS, rule=MassBalance_7_rule)
        self.MassBalance_8 = Constraint(self.UNIT_PROCESSES, self.UU, self.COMPONENTS, rule=MassBalance_8_rule)
        self.MassBalance_9 = Constraint(self.UNIT_PROCESSES, self.COMPONENTS, rule=MassBalance_9_rule)
        self.MassBalance_10 = Constraint(self.COMPONENTS, rule=MassBalance_10_rule)
        self.MassBalance_11 = Constraint(self.UNIT_PROCESSES, rule=MassBalance_11_rule)
        self.MassBalance_12 = Constraint(self.UNIT_PROCESSES, rule=MassBalance_12_rule)
        self.MassBalance_14a = Constraint(self.PRODUCT_POOLS, rule=MassBalance_14a_rule)
        self.MassBalance_14b = Constraint(self.PRODUCT_POOLS, rule=MassBalance_14b_rule)
        self.MassBalance_15a = Constraint(
            self.U_DIST_SUB2, self.COMPONENTS, rule=MassBalance_15a_rule
        )
        self.MassBalance_15b = Constraint(
            self.U_DIST_SUB2, self.COMPONENTS, rule=MassBalance_15b_rule
        )
        self.MassBalance_15c = Constraint(
            self.U_DIST_SUB2, self.COMPONENTS, rule=MassBalance_15c_rule
        )
        self.MassBalance_16 = Constraint(self.DISTRIBUTORS, self.COMPONENTS, rule=MassBalance_16_rule)
        self.MassBalance_17 = Constraint(self.UNIT_CONNECTIONS, rule=MassBalance_17_rule)

        # Calculates the fractions that go to each stream
        self.Distribution_Equations = Constraint(self.PERMITTED_DISTRIBUTOR_UNIT_COMBINATIONS, rule=MassBalance_Distribution_Factor)



    # **** ENERGY BALANCES *****
    # -------------------------

    def create_EnergyBalances(self):
        """
        Description
        -------
        This method creates the PYOMO parameters and variables
        that are necessary for the general Energy Balances (eg. TAU, REF_FLOW...).
        Afterwards Energy Balance‚ Equations are written as PYOMO Constraints.

        """

        # Parameter
        # ---------

        # Energy demand (El, Heating/Cooling, Interval H and C)
        self.tau = Param(self.UNIT_PROCESSES, self.UTILITIES, initialize=0, within=Any, mutable=True)
        self.tau_h = Param(self.HEATING_COOLING_UTILITIES, self.UNIT_PROCESSES, initialize=0, mutable=True)
        self.tau_c = Param(self.HEATING_COOLING_UTILITIES, self.UNIT_PROCESSES, initialize=0, mutable=True)
        self.beta = Param(self.UNIT_PROCESSES, self.HEATING_COOLING_UTILITIES, self.HEAT_INTERVALS, initialize=0, mutable=True)

        # Slack Parameters (Flow Choice, HEN, Upper bounds)
        self.kappa_1_ut = Param(self.UNIT_PROCESSES, self.UTILITIES, self.COMPONENTS, initialize=0)
        self.kappa_2_ut = Param(self.UNIT_PROCESSES, self.UTILITIES, initialize=3)
        self.kappa_3_heat = Param(self.UNIT_PROCESSES, self.HEAT_INTERVALS, initialize=0)
        self.kappa_3_heat2 = Param(self.UNIT_PROCESSES, self.HEAT_INTERVALS, initialize=0)
        self.alpha_hex = Param(initialize=100000)

        self.Y_HEX = Var(self.HEAT_INTERVALS, within=Binary)

        # Additional unit operations (Heat Pump, EL / Heat Generator)
        self.COP_HP = Param(initialize=0, mutable=True)
        self.Efficiency_TUR = Param(self.TURBINES, initialize=0, mutable=True)
        self.Efficiency_FUR = Param(self.FURNACES, initialize=0, mutable=True)
        self.LHV = Param(self.COMPONENTS, initialize=0, mutable=True)
        self.H = Param()

        # Variables
        # ---------

        # Reference Flows for Demand calculation
        self.REF_FLOW_UT = Var(self.UNIT_PROCESSES, self.UTILITIES)

        # Electricity Demand and Production, Heat Pump

        self.ENERGY_DEMAND = Var(self.UNIT_PROCESSES, self.ENERGY_UTILITIES)
        self.ENERGY_DEMAND_TOT = Var(self.ENERGY_UTILITIES)
        self.EL_PROD_1 = Var(self.TURBINES, within=NonNegativeReals)
        self.ENERGY_DEMAND_HP_EL = Var(within=NonNegativeReals)

        # Heating and cooling demand (Interval, Unit, Resi, Defi, Cooling, Exchange, Production , HP)
        self.ENERGY_DEMAND_HEAT = Var(self.UNIT_PROCESSES, self.HEAT_INTERVALS, within=NonNegativeReals)
        self.ENERGY_DEMAND_COOL = Var(self.UNIT_PROCESSES, self.HEAT_INTERVALS, within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_UNIT = Var(self.UNIT_PROCESSES, within=NonNegativeReals)
        self.ENERGY_DEMAND_COOL_UNIT = Var(self.UNIT_PROCESSES, within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_RESI = Var(self.HEAT_INTERVALS, within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_DEFI = Var(self.HEAT_INTERVALS, within=NonNegativeReals)
        self.ENERGY_DEMAND_COOLING = Var(within=NonNegativeReals)
        self.ENERGY_EXCHANGE = Var(self.HEAT_INTERVALS, within=NonNegativeReals)
        self.EXCHANGE_TOT = Var()
        self.ENERGY_DEMAND_HEAT_PROD_USE = Var(within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_PROD_SELL = Var(within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_PROD = Var(self.FURNACES, within=NonNegativeReals)
        self.ENERGY_DEMAND_HP = Var(within=NonNegativeReals)
        self.ENERGY_DEMAND_HP_USE = Var(within=NonNegativeReals)

        self.MW = Param(self.COMPONENTS, initialize=1, mutable=True)
        self.CP = Param(self.COMPONENTS, initialize=0, mutable=True)

        # Constraints
        # -----------

        # Utilities other than heating and cooling

        def UtilityBalance_1_rule(self, u, ut):
            if self.kappa_2_ut[u, ut] == 1:
                return self.Utility_Reference_Flow[u, ut] == sum(
                    self.Inlet[u, i] * self.heat_calculation_slack_param[u, ut, i] for i in self.COMPONENTS
                )
            elif self.kappa_2_ut[u, ut] == 0:
                return self.Utility_Reference_Flow[u, ut] == sum(
                    self.Outlet[u, i] * self.heat_calculation_slack_param[u, ut, i] for i in self.COMPONENTS
                )
            elif self.kappa_2_ut[u, ut] == 4:
                return self.Utility_Reference_Flow[u, ut] == sum(
                    self.Outlet[u, i] / self.MW[i] * self.heat_calculation_slack_param[u, ut, i]
                    for i in self.COMPONENTS
                )
            elif self.kappa_2_ut[u, ut] == 2:
                return self.Utility_Reference_Flow[u, ut] == sum(
                    self.Inlet[u, i] / self.MW[i] * self.heat_calculation_slack_param[u, ut, i]
                    for i in self.COMPONENTS
                )
            elif self.kappa_2_ut[u, ut] == 5:
                return self.Utility_Reference_Flow[u, ut] == sum(
                    0.000277   # MWh/MJ conversion factor (1/3600) => uc parameter in thesis Phiilpp Kenkel
                    * self.CP[i]
                    * self.Inlet[u, i]
                    * self.heat_calculation_slack_param[u, ut, i]
                    for i in self.COMPONENTS
                )
            elif self.kappa_2_ut[u, ut] == 6:
                return self.Utility_Reference_Flow[u, ut] == sum(
                    0.000277
                    * self.CP[i]
                    * self.Outlet[u, i]
                    * self.heat_calculation_slack_param[u, ut, i]
                    for i in self.COMPONENTS
                )
            else:
                return self.Utility_Reference_Flow[u, ut] == 0

        def UtilityBalance_2_rule(self, u, ut):
            return (self.Energy_Demand[u, ut] == self.Utility_Reference_Flow[u, ut] * self.specific_utility_demand[u, ut])

        def UtilityBalance_3_rule(self, ut):
            if ut == "Electricity":
                return self.Total_Energy_Demand[ut] == sum(
                    self.Energy_Demand[u, ut] * self.full_load_hours[u] for u in self.UNIT_PROCESSES
                ) - sum(self.EL_PROD_1[u] * self.full_load_hours[u] for u in self.TURBINES)
            else:
                return self.Total_Energy_Demand[ut] == sum(
                    self.Energy_Demand[u, ut] * self.full_load_hours[u] for u in self.UNIT_PROCESSES
                )

        # Electrictiy Balance for Production from Turbines

        def ElectricityBalance_1_rule(self, u):
            return self.EL_PROD_1[u] == self.turbine_efficiency[u] * sum(
                self.lower_heating_value[i] * self.Inlet[u, i] for i in self.COMPONENTS
            )

        self.ElectricityBalance_1 = Constraint(
            self.TURBINES, rule=ElectricityBalance_1_rule
        )
        self.UtilityBalance_1 = Constraint(self.UNIT_PROCESSES, self.UTILITIES, rule=UtilityBalance_1_rule)
        self.UtilityBalance_2 = Constraint(
            self.UNIT_PROCESSES, self.ENERGY_UTILITIES, rule=UtilityBalance_2_rule
        )
        self.UtilityBalance_3 = Constraint(self.ENERGY_UTILITIES, rule=UtilityBalance_3_rule)

        # Heat and Cooling Balance (Demand)

        def HeatBalance_1_rule(self, u, hi):
            return self.ENERGY_DEMAND_HEAT[u, hi] == sum(
                self.energy_demand_ration[u, ut, hi] * self.specific_cooling_demand[ut, u] * self.Utility_Reference_Flow[u, ut]
                for ut in self.HEATING_COOLING_UTILITIES
            )

        def HeatBalance_2_rule(self, u, hi):
            return self.ENERGY_DEMAND_COOL[u, hi] == sum(
                self.energy_demand_ration[u, ut, hi] * self.specific_heat_demand[ut, u] * self.Utility_Reference_Flow[u, ut]
                for ut in self.HEATING_COOLING_UTILITIES
            )

        # Heating anc Cooling Balance (Either with or without Heat pump)
        # Rigorous HEN Optimization approach

        if self.heat_pump_options["active"] is True:
            hp_tin = self.heat_pump_options["t_in"]
            hp_tout = self.heat_pump_options["t_out"]

            def HeatBalance_3_rule(self, u, hi):
                k = len(self.HEAT_INTERVALS)
                if hi == 1:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        + self.ENERGY_DEMAND_HEAT_PROD_USE
                        - self.ENERGY_DEMAND_HEAT_RESI[hi]
                        - self.ENERGY_EXCHANGE[hi]
                        == 0
                    )
                elif hi == hp_tin:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1]
                        - self.ENERGY_DEMAND_HEAT_RESI[hi]
                        - self.ENERGY_DEMAND_HP
                        - self.ENERGY_EXCHANGE[hi]
                        == 0
                    )
                elif hi == k:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1]
                        - self.ENERGY_DEMAND_COOLING
                        - self.ENERGY_EXCHANGE[hi]
                        == 0
                    )
                else:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1]
                        - self.ENERGY_EXCHANGE[hi]
                        - self.ENERGY_DEMAND_HEAT_RESI[hi]
                        == 0
                    )

            def HeatBalance_4_rule(self, u, hi):
                if hi == 1:
                    return (
                        sum(
                            self.ENERGY_DEMAND_COOL[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        - self.ENERGY_EXCHANGE[hi]
                        - self.ENERGY_DEMAND_HEAT_DEFI[hi]
                        == 0
                    )
                elif hi == hp_tout:
                    return (
                        sum(
                            self.ENERGY_DEMAND_COOL[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        - self.ENERGY_DEMAND_HEAT_DEFI[hi]
                        - self.ENERGY_EXCHANGE[hi]
                        - self.ENERGY_DEMAND_HP_USE
                        == 0
                    )
                else:
                    return (
                        sum(
                            self.ENERGY_DEMAND_COOL[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        - self.ENERGY_EXCHANGE[hi]
                        - self.ENERGY_DEMAND_HEAT_DEFI[hi]
                        == 0
                    )

            def HeatBalance_8_rule(self):
                return self.ENERGY_DEMAND_HP_USE == self.ENERGY_DEMAND_HP / (
                    1 - (1 / self.heat_pump_performance_coefficient)
                )

            def HeatBalance_9_rule(self):
                return self.ENERGY_DEMAND_HP_EL == self.ENERGY_DEMAND_HP / (
                    self.heat_pump_performance_coefficient - 1
                )

            self.HeatBalance_8 = Constraint(rule=HeatBalance_8_rule)
            self.HeatBalance_9 = Constraint(rule=HeatBalance_9_rule)

        else:
            def HeatBalance_3_rule(self, u, hi):
                k = len(self.HEAT_INTERVALS)
                if hi == 1:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        + self.ENERGY_DEMAND_HEAT_PROD_USE
                        - self.ENERGY_DEMAND_HEAT_RESI[hi]
                        - self.ENERGY_EXCHANGE[hi]
                        == 0
                    )
                elif hi == k:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1]
                        - self.ENERGY_DEMAND_COOLING
                        - self.ENERGY_EXCHANGE[hi]
                        == 0
                    )
                else:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                            for u in self.UNIT_PROCESSES
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1]
                        - self.ENERGY_EXCHANGE[hi]
                        - self.ENERGY_DEMAND_HEAT_RESI[hi]
                        == 0
                    )

            def HeatBalance_4_rule(self, u, hi):
                return (
                    sum(
                        self.ENERGY_DEMAND_COOL[u, hi] * self.full_load_hours[u] / self.H
                        for u in self.UNIT_PROCESSES
                    )
                    - self.ENERGY_EXCHANGE[hi]
                    - self.ENERGY_DEMAND_HEAT_DEFI[hi]
                    == 0
                )

            def HeatBalance_8_rule(self):
                return self.ENERGY_DEMAND_HP_USE == 0

            def HeatBalance_9_rule(self):
                return self.ENERGY_DEMAND_HP_EL == 0

            self.HeatBalance_8 = Constraint(rule=HeatBalance_8_rule)
            self.HeatBalance_9 = Constraint(rule=HeatBalance_9_rule)

        #  Exchange Constraints, Production and Sell etc.
        def HeatBalance_5_rule(self, hi):
            return self.ENERGY_EXCHANGE[hi] <= sum(
                self.ENERGY_DEMAND_COOL[u, hi] * self.full_load_hours[u] / self.H for u in self.UNIT_PROCESSES
            )

        def HeatBalance_6_rule(self, hi):
            if hi == 1:
                return (
                    self.ENERGY_EXCHANGE[hi]
                    <= sum(
                    self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                    for u in self.UNIT_PROCESSES
                    )
                    + self.ENERGY_DEMAND_HEAT_PROD_USE
                )
            else:
                return (
                    self.ENERGY_EXCHANGE[hi]
                    <= sum(
                    self.ENERGY_DEMAND_HEAT[u, hi] * self.full_load_hours[u] / self.H
                    for u in self.UNIT_PROCESSES
                    )
                    + self.ENERGY_DEMAND_HEAT_RESI[hi - 1]
                )

        def HeatBalance_7_rule(self):
            return self.EXCHANGE_TOT == sum(self.ENERGY_EXCHANGE[hi] for hi in self.HEAT_INTERVALS)

        def HeatBalance_12_rule(self, hi):
            return self.ENERGY_EXCHANGE[hi] <= self.y_heat_exchange_network[hi] * self.big_m_upper_bound_hex

        def HeatBalance_13_rule(self, u):
            return self.ENERGY_DEMAND_HEAT_PROD[u] == self.furnace_efficiency[u] * sum(
                self.lower_heating_value[i] * self.Inlet[u, i] for i in self.COMPONENTS
            )

        def HeatBalance_14_rule(self, u):
            return self.ENERGY_DEMAND_HEAT_UNIT[u] == sum(
                self.ENERGY_DEMAND_COOL[u, hi] for hi in self.HEAT_INTERVALS
            ) * self.full_load_hours[u] / self.H

        def HeatBalance_15_rule(self, u):
            return self.ENERGY_DEMAND_COOL_UNIT[u] == sum(
                self.ENERGY_DEMAND_HEAT[u, hi] for hi in self.HEAT_INTERVALS
            ) * self.full_load_hours[u] / self.H

        def HeatBalance_16_rule(self):
            return (
                self.ENERGY_DEMAND_HEAT_PROD_USE
                == sum(
                self.ENERGY_DEMAND_HEAT_PROD[u] * self.full_load_hours[u] / self.H
                for u in self.FURNACES
                )
                - self.ENERGY_DEMAND_HEAT_PROD_SELL
            )

        self.HeatBalance_1 = Constraint(self.UNIT_PROCESSES, self.HEAT_INTERVALS, rule=HeatBalance_1_rule)
        self.HeatBalance_2 = Constraint(self.UNIT_PROCESSES, self.HEAT_INTERVALS, rule=HeatBalance_2_rule)
        self.HeatBalance_3 = Constraint(self.UNIT_PROCESSES, self.HEAT_INTERVALS, rule=HeatBalance_3_rule)
        self.HeatBalance_4 = Constraint(self.UNIT_PROCESSES, self.HEAT_INTERVALS, rule=HeatBalance_4_rule)
        self.HeatBalance_5 = Constraint(self.HEAT_INTERVALS, rule=HeatBalance_5_rule)
        self.HeatBalance_6 = Constraint(self.HEAT_INTERVALS, rule=HeatBalance_6_rule)
        self.HeatBalance_7 = Constraint(rule=HeatBalance_7_rule)

        self.HeatBalance_12 = Constraint(self.HEAT_INTERVALS, rule=HeatBalance_12_rule)
        self.HeatBalance_13 = Constraint(self.FURNACES, rule=HeatBalance_13_rule)
        self.HeatBalance_14 = Constraint(self.UNIT_PROCESSES, rule=HeatBalance_14_rule)
        self.HeatBalance_15 = Constraint(self.UNIT_PROCESSES, rule=HeatBalance_15_rule)
        self.HeatBalance_16 = Constraint(rule=HeatBalance_16_rule)

    # *** Waste Costs ****
    # --------------------
    def create_WasteCosts(self):

        # set parameters
        # initial_waste_cost_factors = {
        #     "Incineration": 0,
        #     "Landfill": 0,
        #     "WWTP": 0
        # }
        self.waste_cost_factor = Param(self.WASTE_MANAGEMENT_TYPES, initialize=0, mutable=True)
        self.waste_type_U = Param(self.UNIT_PROCESSES, initialize='Landfill', mutable=True, within=Any)

        # set variables
        self.WASTE_COST_U = Var(self.UNIT_PROCESSES, within=NonNegativeReals)
        self.WASTE_COST_TOT = Var(within=NonNegativeReals)

        def Cost_Waste_rule(self, u):
            wasteType = self.waste_type_U[u].value
            return (self.WASTE_COST_U[u] == self.full_load_hours[u] *  # units WASTE_COST = k€/year
                    sum(self.Waste[u, i] for i in self.COMPONENTS) * self.waste_cost_factor[wasteType])

        def Cost_Waste_TOT(self):
            return self.WASTE_COST_TOT == sum(self.WASTE_COST_U[u] for u in self.UNIT_PROCESSES)/1000

        # add constraints
        self.Cost_Waste = Constraint(self.UNIT_PROCESSES, rule=Cost_Waste_rule)
        self.Cost_Waste_TOT = Constraint(rule=Cost_Waste_TOT)

    # **** COST BALANCES ****
    # -------------------------

    def create_EconomicEvaluation(self):
        """
        Description
        -------
        This method creates the PYOMO parameters and variables
        that are necessary for the general Cost Calculation (eg. detla_ut, COST_UT etc.).
        Afterward Cost calculation equations are written as PYOMO Constraints.
        """

        # Parameter
        # ---------

        # Specific costs (Utility, raw materials, Product prices)

        self.delta_ut = Param(self.ENERGY_UTILITIES, initialize=0, mutable=True)
        self.delta_q = Param(self.HEAT_INTERVALS, initialize=30, mutable=True)
        self.delta_cool = Param(initialize=15, mutable=True)
        self.ProductPrice = Param(self.PRODUCT_POOLS, initialize=0, mutable=True)

        # Cost factors (CAPEX, Heat Pump)
        self.DC = Param(self.UNIT_PROCESSES, initialize=0, mutable=True)
        self.IDC = Param(self.UNIT_PROCESSES, initialize=0, mutable=True)
        self.ACC_Factor = Param(self.UNIT_PROCESSES, initialize=0, mutable=True)

        self.HP_ACC_Factor = Param(initialize=1, mutable=True)
        self.HP_Costs = Param(initialize=1, mutable=True)

        # Piecewise Linear CAPEX
        self.lin_CAPEX_x = Param(self.COSTED_UNIT_OPERATIONS, self.J, initialize=0)
        self.lin_CAPEX_y = Param(self.COSTED_UNIT_OPERATIONS, self.J, initialize=0)
        self.kappa_1_capex = Param(self.COSTED_UNIT_OPERATIONS, self.COMPONENTS, initialize=0)
        self.kappa_2_capex = Param(self.COSTED_UNIT_OPERATIONS, initialize=5)

        # OPEX factors

        self.K_OM = Param(self.COSTED_UNIT_OPERATIONS, initialize=0.04, mutable=True)

        # Variables
        # ---------

        # Utilitiy Costs ( El, Heat, El-TOT, HEN)
        self.ENERGY_COST = Var(self.ENERGY_UTILITIES)
        self.COST_HEAT = Var(self.HEAT_INTERVALS, initialize=0)
        self.COST_UT = Var(initialize=0)
        self.ELCOST = Var()
        self.HEATCOST = Var(self.HEAT_INTERVALS)
        self.C_TOT = Var()
        self.HENCOST = Var(self.HEAT_INTERVALS, within=NonNegativeReals)
        self.UtCosts = Var()

        # Piece-Wise Linear CAPEX
        self.lin_CAPEX_s = Var(self.COSTED_UNIT_OPERATIONS, self.JI, bounds=(0, 1))
        self.lin_CAPEX_z = Var(self.COSTED_UNIT_OPERATIONS, self.JI, within=Binary)
        self.lin_CAPEX_lambda = Var(self.COSTED_UNIT_OPERATIONS, self.J, bounds=(0, 1))
        self.REF_FLOW_CAPEX = Var(self.COSTED_UNIT_OPERATIONS, within=NonNegativeReals)

        # CAPEX (Units, Returning costs, Heat Pump, Total)
        self.EC = Var(self.COSTED_UNIT_OPERATIONS, within=NonNegativeReals)
        self.FCI = Var(self.COSTED_UNIT_OPERATIONS, within=NonNegativeReals)
        self.ACC = Var(self.COSTED_UNIT_OPERATIONS, within=NonNegativeReals)
        self.to_acc = Param(self.COSTED_UNIT_OPERATIONS, initialize=0, mutable=True)
        self.TO_CAPEX = Var(self.COSTED_UNIT_OPERATIONS, within=NonNegativeReals)
        self.TO_CAPEX_TOT = Var(within=NonNegativeReals)
        self.ACC_HP = Var(within=NonNegativeReals)
        self.TAC = Var()
        self.CAPEX = Var()

        # OPEX (Raw Materials, O&REACTANTS, , UtilitiesTotal, Profits)
        # self.RM_COST = Var(self.COSTED_UNIT_OPERATIONS, within=NonNegativeReals) #not used
        self.RM_COST_TOT = Var()  # Var(within=NonNegativeReals) # can also be negative, e.g. gate fees for handeling waste
        self.M_COST = Var(self.COSTED_UNIT_OPERATIONS)
        self.M_COST_TOT = Var(within=NonNegativeReals)
        # self.O_H = Var()  # doesn't seem to be used
        # self.O_COST = Var()  # doesn't seem to be used
        # self.OM_COST = Var(within=NonNegativeReals)  # doesn't seem to be used
        self.OPEX = Var()
        self.PROFITS = Var(self.PRODUCT_POOLS)
        self.PROFITS_TOT = Var()

        # Constraints
        # -----------

        # CAPEX Calculation (Reference Flow, Piece-Wise linear Lambda Constraints)

        def CapexEquation_1_rule(self, u):
            if self.kappa_2_capex[u] == 1:
                return self.REF_FLOW_CAPEX[u] == sum(
                    self.Inlet[u, i] * self.kappa_1_capex[u, i] for i in self.COMPONENTS
                )
            elif self.kappa_2_capex[u] == 0:
                return self.REF_FLOW_CAPEX[u] == sum(
                    self.Outlet[u, i] * self.kappa_1_capex[u, i] for i in self.COMPONENTS
                )
            elif self.kappa_2_capex[u] == 2:
                return self.REF_FLOW_CAPEX[u] == self.Energy_Demand[u, "Electricity"]

            elif self.kappa_2_capex[u] == 3:
                return self.REF_FLOW_CAPEX[u] == self.ENERGY_DEMAND_HEAT_PROD[u]

            elif self.kappa_2_capex[u] == 4:
                return self.REF_FLOW_CAPEX[u] == self.EL_PROD_1[u]
            else:
                return self.REF_FLOW_CAPEX[u] == 0

        def CapexEquation_2_rule(self, u):
            return (
                sum(
                    self.lin_CAPEX_x[u, j] * self.lin_CAPEX_lambda[u, j] for j in self.J
                )
                == self.REF_FLOW_CAPEX[u]
            )

        def CapexEquation_3_rule(self, u):
            return self.EC[u] == sum(
                self.lin_CAPEX_y[u, j] * self.lin_CAPEX_lambda[u, j] for j in self.J
            )

        def CapexEquation_4_rule(self, u):
            return sum(self.lin_CAPEX_z[u, j] for j in self.JI) == 1

        def CapexEquation_5_rule(self, u, j):
            return self.lin_CAPEX_s[u, j] <= self.lin_CAPEX_z[u, j]

        def CapexEquation_6_rule(self, u, j):
            if j == 1:
                return (
                    self.lin_CAPEX_lambda[u, j]
                    == self.lin_CAPEX_z[u, j] - self.lin_CAPEX_s[u, j]
                )
            elif j == len(self.J):
                return self.lin_CAPEX_lambda[u, j] == self.lin_CAPEX_s[u, j - 1]
            else:
                return (
                    self.lin_CAPEX_lambda[u, j]
                    == self.lin_CAPEX_z[u, j]
                    - self.lin_CAPEX_s[u, j]
                    + self.lin_CAPEX_s[u, j - 1]
                )

        # Fixed Capital investment, Annual capital costs, Heat Pump, Returning costs, Total
        def CapexEquation_7_rule(self, u):
            return self.FCI[u] == self.EC[u] * (1 + self.DC[u] + self.IDC[u])

        def CapexEquation_8_rule(self, u):
            return self.ACC[u] == self.FCI[u] * self.ACC_Factor[u]

        self.ACC_H = Var(within=NonNegativeReals)

        def CapexEquation_9_rule(self):
            return (
                self.ACC_H
                == self.HP_ACC_Factor * self.HP_Costs * self.ENERGY_DEMAND_HP_USE
            )

        def Cap(self):
            return self.ACC_HP == self.ACC_H / 1000

        self.Xap = Constraint(rule=Cap)

        # reoccuring costs of equipment
        # --------------------------------
        def CapexEquation_11_rule(self, u):
            return self.TO_CAPEX[u] == self.to_acc[u] * self.EC[u]

        def CapexEquation_12_rule(self):
            return self.TO_CAPEX_TOT == sum(self.TO_CAPEX[u] for u in self.COSTED_UNIT_OPERATIONS)
        # --------------------------------

        # the three equations below are for the HEN CAPITAL COSTS (CAPEX)
        # not realted to the operating costs of HEN
        # --------------------------------------------------------------------
        def HEN_CostBalance_4_rule(self, hi):
            return self.HENCOST[hi] <= 13.459 * self.ENERGY_EXCHANGE[
                hi
            ] + 3.3893 + self.big_m_upper_bound_hex * (1 - self.y_heat_exchange_network[hi])
        def HEN_CostBalance_4b_rule(self, hi):
            return self.HENCOST[hi] >= 13.459 * self.ENERGY_EXCHANGE[
                hi
            ] + 3.3893 - self.big_m_upper_bound_hex * (1 - self.y_heat_exchange_network[hi])
        def HEN_CostBalance_4c_rule(self, hi):
            return self.HENCOST[hi] <= self.y_heat_exchange_network[hi] * self.big_m_upper_bound_hex
        # --------------------------------------------------------------------

        def CapexEquation_10_rule(self):
            return (
                self.CAPEX
                == sum(self.ACC[u] for u in self.COSTED_UNIT_OPERATIONS)  # annual capital costs
                + self.ACC_HP / 1000  # heat pump capital costs
                + self.TO_CAPEX_TOT  # reoccurring costs of equipment
                + sum(self.HENCOST[hi] for hi in self.HEAT_INTERVALS)  # HEN capital costs
            )

        self.CapexEquation_1 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=CapexEquation_1_rule)
        self.CapexEquation_2 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=CapexEquation_2_rule)
        self.CapexEquation_3 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=CapexEquation_3_rule)
        self.CapexEquation_4 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=CapexEquation_4_rule)
        self.CapexEquation_5 = Constraint(self.COSTED_UNIT_OPERATIONS, self.JI, rule=CapexEquation_5_rule)
        self.CapexEquation_6 = Constraint(self.COSTED_UNIT_OPERATIONS, self.J, rule=CapexEquation_6_rule)
        self.CapexEquation_7 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=CapexEquation_7_rule)
        self.CapexEquation_8 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=CapexEquation_8_rule)
        self.CapexEquation_9 = Constraint(rule=CapexEquation_9_rule)

        self.HEN_CostBalance_4 = Constraint(self.HEAT_INTERVALS, rule=HEN_CostBalance_4_rule)
        self.HEN_CostBalance_4b = Constraint(self.HEAT_INTERVALS, rule=HEN_CostBalance_4b_rule)
        self.HEN_CostBalance_4c = Constraint(self.HEAT_INTERVALS, rule=HEN_CostBalance_4c_rule)

        self.CapexEquation_10 = Constraint(rule=CapexEquation_10_rule)
        self.CapexEquation_11 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=CapexEquation_11_rule)
        self.CapexEquation_12 = Constraint(rule=CapexEquation_12_rule)

        # OPEX Calculation (HEN Costs: Heating / Cooling, CAPEX)

        def HEN_CostBalance_1_rule(self, hi):
            return (
                self.HEATCOST[hi]
                == self.ENERGY_DEMAND_HEAT_DEFI[hi] * self.delta_q[hi] * self.H
            )

        def HEN_CostBalance_2_rule(self):
            return self.UtCosts == (
                sum(self.HEATCOST[hi] for hi in self.HEAT_INTERVALS)
                - self.ENERGY_DEMAND_HEAT_PROD_SELL * self.H * self.delta_q[1] * 0.7
                + self.ENERGY_DEMAND_COOLING * self.H * self.delta_cool
            )

        def HEN_CostBalance_3_rule(self):
            return (
                self.ELCOST
                == self.ENERGY_DEMAND_HP_EL
                * self.delta_ut["Electricity"]
                * self.H
                / 1000
            )

        # selling buying of energy see UtCosts (HEN_CostBalance_2_rule)
        def HEN_CostBalance_6_rule(self):
            return self.C_TOT == self.UtCosts/1000


        self.HEN_CostBalance_1 = Constraint(self.HEAT_INTERVALS, rule=HEN_CostBalance_1_rule)
        self.HEN_CostBalance_2 = Constraint(rule=HEN_CostBalance_2_rule)
        self.HEN_CostBalance_3 = Constraint(rule=HEN_CostBalance_3_rule)
        self.HEN_CostBalance_6 = Constraint(rule=HEN_CostBalance_6_rule)

        # Utility Costs (Electricity/Chilling)

        def Ut_CostBalance_1_rule(self, ut):
            return (
                self.ENERGY_COST[ut]
                == self.Total_Energy_Demand[ut] * self.delta_ut[ut] / 1000 # euro to million euro conversion
            )

        self.Ut_CostBalance_1 = Constraint(self.ENERGY_UTILITIES, rule=Ut_CostBalance_1_rule)

        # Raw Materials and Operating and Maintenance

        def RM_CostBalance_1_rule(self):
            return self.RM_COST_TOT == sum(
                self.material_costs[u_s] * self.Raw_Material_Input_Source[u_s] * self.full_load_hours[u_s] / 1000  # euro to million euro conversion
                for u_s in self.RAW_MATERIAL_SOURCES
            )

        def OM_CostBalance_1_rule(self, u):
            return self.M_COST[u] == self.K_OM[u] * self.FCI[u] # in million euro (M€)

        def OM_CostBalance_2_rule(self):
            return self.M_COST_TOT == sum(self.M_COST[u] for u in self.COSTED_UNIT_OPERATIONS)

        # Total OPEX
        def Opex_1_rule(self): # im M€ (million euro)
            return (
                self.OPEX
                == self.M_COST_TOT  # operating and maintenance costs
                + self.RM_COST_TOT / 1000  # raw material costs
                + sum(self.ENERGY_COST[ut] for ut in self.ENERGY_UTILITIES) / 1000  # utility costs energy
                + self.C_TOT / 1000  # selling or buying of energy (from HEN)
                + self.ELCOST / 1000  # electricity costs for heat pump
                + self.WASTE_COST_TOT / 1000                               # waste costs
            )

        self.RM_CostBalance_1 = Constraint(rule=RM_CostBalance_1_rule)
        self.OM_CostBalance_1 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=OM_CostBalance_1_rule)
        self.OM_CostBalance_2 = Constraint(rule=OM_CostBalance_2_rule)
        self.OpexEquation = Constraint(rule=Opex_1_rule)

        # Profits

        def Profit_1_rule(self, u): # profit per 1000€
            return (
                self.PROFITS[u]
                == sum(self.Inlet[u, i] for i in self.COMPONENTS) * self.ProductPrice[u] / 1000
            )

        def Profit_2_rule(self): # profit per M€ (million euro)
            return (
                self.PROFITS_TOT
                == sum(self.PROFITS[u] for u in self.PRODUCT_POOLS) * self.H / 1000
            )

        self.ProfitEquation_1 = Constraint(self.PRODUCT_POOLS, rule=Profit_1_rule)
        self.ProfitEquation_2 = Constraint(rule=Profit_2_rule)

        # Total Annualized Costs

        def TAC_1_rule(self):
            return self.TAC == (self.CAPEX + self.OPEX - self.PROFITS_TOT) * 1000  # waste costs are in the OPEX

        self.TAC_Equation = Constraint(rule=TAC_1_rule)

    # **** ENVIRONMENTAL BALANCES *****
    # -------------------------

    def create_EnvironmentalEvaluation(self):
        """
        Description
        -------
        This method creates the PYOMO parameters and variables
        that are necessary for the general CO2 Emissions (eg. emission factors etc.).
        Afterwards Emission equations are written as PYOMO Constraints.

        """

        # Parameter
        # --------

        # Emission factors (Utilities, Components, Products, Building of units)
        self.em_fac_ut = Param(self.UTILITIES, initialize=0, mutable=True)
        self.em_fac_comp = Param(self.COMPONENTS, initialize=0, mutable=True)
        self.em_fac_prod = Param(self.PRODUCT_POOLS, initialize=0, mutable=True)
        self.em_fac_unit = Param(self.COSTED_UNIT_OPERATIONS, initialize=0, mutable=True)
        self.em_fac_source = Param(self.RAW_MATERIAL_SOURCES, initialize=0, mutable=True)

        # Lifetime of Units
        self.LT = Param(self.UNIT_PROCESSES, initialize=1, mutable=True)

        # Variables
        # ---------

        self.GWP_UNITS = Var(self.COSTED_UNIT_OPERATIONS)
        self.GWP_CREDITS = Var(self.PRODUCT_POOLS)
        self.GWP_CAPTURE = Var()
        self.GWP_U = Var(self.UNIT_PROCESSES, initialize=0)
        self.GWP_UT = Var(self.UTILITIES)
        self.GWP_TOT = Var()

        # Constraints
        # -----------

        def GWP_1_rule(self, u):
            return self.GWP_U[u] == self.full_load_hours[u] * sum(
                self.Waste[u, i] * self.em_fac_comp[i] for i in self.COMPONENTS
            )

        def GWP_2_rule(self, ut):
            if ut == "Electricity":
                return (
                    self.GWP_UT[ut]
                    == (self.Total_Energy_Demand[ut] + self.ENERGY_DEMAND_HP_EL * self.H)
                    * self.em_fac_ut[ut]
                )
            else:
                return (
                    self.GWP_UT[ut] == self.Total_Energy_Demand[ut] * self.em_fac_ut[ut]
                )

        def GWP_3_rule(self):
            return self.GWP_UT["Heat"] == self.em_fac_ut["Heat"] * self.H * (
                sum(self.ENERGY_DEMAND_HEAT_DEFI[hi] for hi in self.HEAT_INTERVALS)
                - self.ENERGY_DEMAND_HEAT_PROD_SELL * 0.7
            )

        def GWP_5_rule(self):
            return self.GWP_UT["Heat2"] == 0

        def GWP_6_rule(self, u):
            return self.GWP_UNITS[u] == self.em_fac_unit[u] / self.LT[u] * self.y[u]

        def GWP_7_rule(self, u):
            return (
                self.GWP_CREDITS[u]
                == self.em_fac_prod[u]
                * sum(self.Inlet[u, i] for i in self.COMPONENTS)
                * self.full_load_hours[u]
            )

        def GWP_8_rule(self):
            return self.GWP_CAPTURE == sum(
                self.Raw_Material_Input_Source[u_s] * self.full_load_hours[u_s] * self.em_fac_source[u_s]
                for u_s in self.RAW_MATERIAL_SOURCES
            )

        def GWP_4_rule(self):
            return self.GWP_TOT == sum(self.GWP_U[u] for u in self.COSTED_UNIT_OPERATIONS) + sum(
                self.GWP_UT[ut] for ut in self.UTILITIES
            ) - self.GWP_CAPTURE - sum(self.GWP_CREDITS[u] for u in self.PRODUCT_POOLS) + sum(
                self.GWP_UNITS[u] for u in self.COSTED_UNIT_OPERATIONS
            )

        self.EnvironmentalEquation1 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=GWP_1_rule)
        self.EnvironmentalEquation2 = Constraint(self.ENERGY_UTILITIES, rule=GWP_2_rule)
        self.EnvironmentalEquation3 = Constraint(rule=GWP_3_rule)
        self.EnvironmentalEquation4 = Constraint(rule=GWP_4_rule)
        self.EnvironmentalEquation5 = Constraint(rule=GWP_5_rule)
        self.EnvironmentalEquation6 = Constraint(self.COSTED_UNIT_OPERATIONS, rule=GWP_6_rule)
        self.EnvironmentalEquation7 = Constraint(self.PRODUCT_POOLS, rule=GWP_7_rule)
        self.EnvironmentalEquation8 = Constraint(rule=GWP_8_rule)

    # **** FRESH WATER DEMAND EQUATIONS
    # --------------------------------------

    def create_FreshwaterEvaluation(self):
        """

        Description
        -------
        This method creates the PYOMO parameters and variables
        that are necessary for the general Fresh water demand (eg. demand factors etc.).
        Afterwards FWD equations are written as PYOMO Constraints.

        """

        self.FWD_UT1 = Var()
        self.FWD_UT2 = Var()
        self.FWD_S = Var()
        self.FWD_C = Var()
        self.FWD_TOT = Var()

        self.fw_fac_source = Param(self.RAW_MATERIAL_SOURCES, initialize=0, mutable=True)
        self.fw_fac_ut = Param(self.UTILITIES, initialize=0, mutable=True)
        self.fw_fac_prod = Param(self.PRODUCT_POOLS, initialize=0, mutable=True)

        def FWD_1_rule(self):
            return self.FWD_S == sum(
                self.Raw_Material_Input_Source[u_s] * self.fw_fac_source[u_s] * self.full_load_hours[u_s]
                for u_s in self.RAW_MATERIAL_SOURCES
            )

        def FWD_2_rule(self):
            return self.FWD_C == sum(
                sum(self.Inlet[u_p, i] for i in self.COMPONENTS)
                * self.full_load_hours[u_p]
                * self.fw_fac_prod[u_p]
                for u_p in self.PRODUCT_POOLS
            )

        def FWD_3_rule(self):
            return self.FWD_UT1 == sum(
                self.Total_Energy_Demand[ut] * self.fw_fac_ut[ut] for ut in self.ENERGY_UTILITIES
            )

        def FWD_4_rule(self):
            return (
                self.FWD_UT2
                == (
                    sum(self.ENERGY_DEMAND_HEAT_DEFI[hi] for hi in self.HEAT_INTERVALS)
                    - self.ENERGY_DEMAND_HEAT_PROD_SELL * 0.7
                )
                * self.H
                * self.fw_fac_ut["Heat"]
            )

        def FWD_5_rule(self):
            return self.FWD_TOT == self.FWD_UT2 + self.FWD_UT1 - self.FWD_S - self.FWD_C

        self.FreshWaterEquation1 = Constraint(rule=FWD_1_rule)
        self.FreshWaterEquation2 = Constraint(rule=FWD_2_rule)
        self.FreshWaterEquation3 = Constraint(rule=FWD_3_rule)
        self.FreshWaterEquation4 = Constraint(rule=FWD_4_rule)
        self.FreshWaterEquation5 = Constraint(rule=FWD_5_rule)

    # *** LCA EQUATIONS ***
    # ------------------------
    def create_LCAEquations(self):
        """
        Description
        :return:
        """
        # start with impacts of the inflowing components
        # needs to be introduced like component_concentration variable! look how it is passed on
        self.impact_inFlow_components = Param(self.COMPONENTS, self.IMPACT_CATEGORIES, initialize=0, mutable=True)
        self.IMPACT_INPUTS_U_CAT = Var(self.UNIT_PROCESSES, self.IMPACT_CATEGORIES)
        self.IMPACT_INPUTS_PER_CAT = Var(self.IMPACT_CATEGORIES)

        def LCA_Inflow_U_rule(self, u, ImpCat):
            return self.IMPACT_INPUTS_U_CAT[u, ImpCat] == sum(self.Total_Raw_Material_Input[u, i] * self.impact_inFlow_components[i, ImpCat]
                                                              for i in self.COMPONENTS)
        def LCA_All_Inflow_rule(self, ImpCat):
            return self.IMPACT_INPUTS_PER_CAT[ImpCat] == sum(self.IMPACT_INPUTS_U_CAT[u, ImpCat] for u in self.UNIT_PROCESSES) * self.H

        self.LCA_InFlow_Units = Constraint(self.UNIT_PROCESSES, self.IMPACT_CATEGORIES, rule=LCA_Inflow_U_rule)
        self.LCA_InFlow_Total_Per_Catagories = Constraint(self.IMPACT_CATEGORIES, rule=LCA_All_Inflow_rule)

        # now the impacts of energy and heat consumption
        # set the parameters
        self.util_impact_factors = Param(self.UTILITIES, self.IMPACT_CATEGORIES, initialize=0, mutable=True)
        # set the variables
        self.IMPACT_UTILITIES = Var(self.UTILITIES, self.IMPACT_CATEGORIES)
        self.IMPACT_UTILITIES_PER_CAT = Var(self.IMPACT_CATEGORIES)

        # util_impact_factors['electricity'] units: kgCO2/MWh and ENERGY_DEMAND_TOTAL['electricity'] units: MW

        # set the constraints
        def LCA_Utility_rule(self, ut, impCat):
            if ut == "Electricity":
                return (self.IMPACT_UTILITIES[ut, impCat] == (self.Total_Energy_Demand[ut] * self.H + self.ENERGY_DEMAND_HP_EL * self.H)
                        * self.util_impact_factors[ut, impCat])
            elif ut == "Chilling":
                return self.IMPACT_UTILITIES[ut, impCat] == self.Total_Energy_Demand[ut]* self.H * self.util_impact_factors[ut, impCat]

            elif ut == "Heat":
                return (self.IMPACT_UTILITIES[ut, impCat] == self.H * self.util_impact_factors[ut]
                    (sum(self.ENERGY_DEMAND_HEAT_DEFI[hi] for hi in self.HEAT_INTERVALS) - self.ENERGY_DEMAND_HEAT_PROD_SELL))
            else:
                # skip heat 2
                return self.IMPACT_UTILITIES[ut, impCat] == 0
        def LCA_Utility_TOT_rule(self, impCat):
            return self.IMPACT_UTILITIES_PER_CAT[impCat] == sum(self.IMPACT_UTILITIES[ut, impCat] for ut in self.UTILITIES)

        self.LCA_Utilities = Constraint(self.ENERGY_UTILITIES, self.IMPACT_CATEGORIES, rule=LCA_Utility_rule)
        self.LCA_Utilities_TOT = Constraint(self.IMPACT_CATEGORIES, rule=LCA_Utility_TOT_rule)

        # impact of waste
        # set the parameters
        self.waste_impact_fac = Param(self.WASTE_MANAGEMENT_TYPES, self.IMPACT_CATEGORIES, initialize=0, mutable=True)
        # set the variables
        self.WASTE_U = Var(self.UNIT_PROCESSES, self.IMPACT_CATEGORIES)
        self.WASTE_TOT = Var(self.IMPACT_CATEGORIES)
        def LCA_Waste_rule(self, u, impCat):
            wasteType = self.waste_type_U[u].value
            return (self.WASTE_U[u, impCat] == self.full_load_hours[u] * sum(self.Waste[u, i] * self.waste_impact_fac[wasteType, impCat]
                                                                             for i in self.COMPONENTS))
        def LCA_Waste_TOT_rule(self, impCat):
            return self.WASTE_TOT[impCat] == sum(self.WASTE_U[u, impCat] for u in self.UNIT_PROCESSES)

        self.LCA_Waste = Constraint(self.UNIT_PROCESSES, self.IMPACT_CATEGORIES, rule=LCA_Waste_rule)
        self.LCA_Waste_TOT = Constraint(self.IMPACT_CATEGORIES, rule=LCA_Waste_TOT_rule)

        # totla impact per catagorie:  the the sum of all impacts, inflow, utilities and waste
        self.IMPACT_TOT = Var(self.IMPACT_CATEGORIES)
        def LCA_Total_Impact_rule(self, impCat):
            return self.IMPACT_TOT[impCat] == (self.IMPACT_INPUTS_PER_CAT[impCat] + self.IMPACT_UTILITIES_PER_CAT[impCat] + self.WASTE_TOT[impCat]) /self.source_or_product_load

        self.LCA_Total_Impact = Constraint(self.IMPACT_CATEGORIES, rule=LCA_Total_Impact_rule)

    # **** DECISION MAKING EQUATIONS *****
    # -------------------------

    def create_DecisionMaking(self):
        """


        Description
        -------
        This function creates additional (optional) logic contraints of
        the flowsheet topology.

        """

        # Parameter
        # --------

        numbers = [1, 2, 3]

        # Variables
        # ---------

        # Constraints
        # -----------

        def ProcessGroup_logic_1_rule(self, u, uu):

            # this constraint is only relevant if the design is not fixed
            if self._fixedDesign:
                return Constraint.Skip

            ind = False

            for i, j in self.groups.items():

                if u in j and uu in j:
                    return self.y[u] == self.y[uu]
                    ind = True # what is this?? Unreachable code?

            if ind == False:
                return Constraint.Skip

        def ProcessGroup_logic_2_rule(self, u, k):

            # this constraint is only relevant if the design is not fixed
            if self._fixedDesign:
                return Constraint.Skip

            ind = False

            for i, j in self.connections.items():
                if u == i:
                    if j[k]:
                        # todo change logic to sum(self.y[uu] for uu in j[k]) == self.y[u]
                        # so only 1 connection is allowed
                        # also this currently does not work if you want your input to only go into one unit...,
                        # Might have to build that functionality in the SOURCE tab of the Excel file
                        return sum(self.y[uu] for uu in j[k]) >= self.y[u]
                        # ind = True

            if ind == False:
                return Constraint.Skip

        self.ProcessGroup_logic_1 = Constraint(self.UNIT_PROCESSES, self.UU, rule=ProcessGroup_logic_1_rule)

        self.ProcessGroup_logic_2 = Constraint(self.UNIT_PROCESSES, numbers, rule=ProcessGroup_logic_2_rule)


    # **** OBJECTIVE FUNCTIONS *****
    # -------------------------

    def create_ObjectiveFunction(self):
        """
        Description
        -------
        Defines the main product flow and the objetive function.

        """

        # Parameter
        # ---------

        self.ObjectiveFunctionName = Param(within=Any, initialize=self.objective_name)


        # Variables
        # ---------

        self.MainProductFlow = Var(initialize=0)

        self.NPC = Var()
        self.NPFWD = Var()
        self.NPE = Var()
        self.EBIT = Var()
        self.SumOfProductFlows = Var()

        # Constraints
        # -----------

        # Definition of Main Product and Product Load for NPC / NPE Calculation

        def SumOfProducts_rule(self):
            return self.SumOfProductFlows == sum(self.Inlet[U_pp, i]
                                             for U_pp in self.PRODUCT_POOLS
                                             for i in self.COMPONENTS
                                             ) * self.H

        self.SumOfProducts_Equation = Constraint(rule=SumOfProducts_rule)


        def MainProduct_1_rule(self):
            # If product driven, else skip this constraint
            if self.loadType == 'Product':
                return self.MainProductFlow == sum(self.Inlet[self.loadID, i] for i in self.COMPONENTS) * self.H
            else:
                return Constraint.Skip

        def MainProduct_2_rule(self):
            if self.loadType == 'Product':
                return self.MainProductFlow == self.source_or_product_load

            else:
                return Constraint.Skip

        self.MainProduct_Equation_1 = Constraint(rule=MainProduct_1_rule)
        self.MainProduct_Equation_2 = Constraint(rule=MainProduct_2_rule)

        # Definition of specific function

        def Specific_NPC_rule(self): # in € per year (euro/ton/year)
            # product_load is 1 is substrate driven, otherwise it is the target production
            # self.TAC == (self.CAPEX + self.OPEX - self.PROFITS_TOT) * 1000
            return self.NPC == (self.TAC * 1000)/self.source_or_product_load # in € per tonne of product per year (so your target production)


        def Specific_GWP_rule(self):
            return self.NPE == self.GWP_TOT / self.source_or_product_load
            #return self.NPE == self.GWP_TOT

        def Specific_FWD_rule(self):
            return self.NPFWD == self.FWD_TOT / self.source_or_product_load
            #return self.NPFWD == self.FWD_TOT

        def Specific_EBIT_rule(self):
            if self.loadType:  # in €/ton
                return self.EBIT == (-self.TAC * 1000) / self.source_or_product_load # in M€ (million euro)
            else:   # # in Mil €
                return self.EBIT == (self.PROFITS_TOT - self.CAPEX - self.OPEX)

        self.Specific_NPC_rule = Constraint(rule=Specific_NPC_rule)
        self.Specific_GWP_rule = Constraint(rule=Specific_GWP_rule)
        self.Specific_FWD_rule = Constraint(rule=Specific_FWD_rule)
        self.Specific_EBIT_rule = Constraint(rule=Specific_EBIT_rule)

        # Definition of the used Objective Function

        if self.objective_name == "NPC":
            def Objective_rule(self):
                return self.NPC

        elif self.objective_name == "NPE":
            def Objective_rule(self):
                return self.NPE

        elif self.objective_name == "FWD":

            def Objective_rule(self):
                return self.NPFWD

        elif self.objective_name == "EBIT":
                def Objective_rule(self):
                    return self.EBIT

        elif self.objective_name in self.impact_categories_list:
            def Objective_rule(self):
                return self.IMPACT_TOT[self.objective_name]
        else:
            def Objective_rule(self):
                return self.NPC

        if self.objective_name == "EBIT":
            self.Objective = Objective(rule=Objective_rule, sense=maximize)

        else: # want to minimise the other objective functions
            self.Objective = Objective(rule=Objective_rule, sense=minimize)

        self.objective_sense = Var(initialize=0, within=Binary)

        def objective_sense_rule1(self):
            if self.objective_name == "EBIT":
                return self.objective_sense == 1  # 1 for maximizing
            else:
                return self.objective_sense == 0  # 0 for minimizing

        self.objective_sense_rule = Constraint(rule=objective_sense_rule1)
