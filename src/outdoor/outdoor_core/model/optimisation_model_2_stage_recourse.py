""""
Created on 10/10/2023
@Author: Lucas Van der Hauwaert, Philipp Kenkel
Email: Lucas.vanderhauwaert@usc.es
"""

from pyomo.environ import *



class SuperstructureModel_2_Stage_recourse(AbstractModel):
    """
    Class description
    -----------------

    This class holds the mathematical model equations to describe a superstructure
    model. It defines classical modeling components like sets, parameter, variables
    and constraints. The model created is a two-stage recourse model with

    The model includes mass balances, energy balances including detailed
    heat integration based on heat intervals, cost functions using piece-wise
    linear capital costs and operational costs based on utilities, raw materials,
    operating and maintenance and other aspects. Additionally GWP and fresh
    water demand are calculated.

    """



    def __init__(self, superstructure_input=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if superstructure_input is not None:
            self._set_optionals_from_superstructure(superstructure_input)
        else:
            self._set_optionals_from_external(kwargs)

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

        self.productDriven = superstructure_input.productDriven

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

        for i in superstructure_input.UnitsList:
            if i.Type == "ProductPool" and i.ProductType == "MainProduct":
                self.main_pool = i.Number

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
        self.create_EconomicEvaluation()
        self.create_EnvironmentalEvaluation()
        self.create_FreshwaterEvaluation()
        self.create_DecisionMaking()
        self.create_ObjectiveFunction()

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
        self.U = Set()
        self.UU = Set(within=self.U)
        self.U_STOICH_REACTOR = Set(within=self.U)
        self.U_YIELD_REACTOR = Set(within=self.U)
        self.U_SPLITTER = Set(within=self.U)
        self.U_TUR = Set(within=self.U)
        self.U_FUR = Set(within=self.U)
        self.U_PP = Set(within=self.U)
        self.U_C = Set(within=self.U)
        self.U_S = Set(within=self.U)
        self.U_SU = Set(within=self.U_S * self.U)
        self.U_DIST = Set(within=self.U)
        self.U_DIST_SUB = Set(within=self.U_DIST * self.U)

        self.U_CONNECTORS = Set(within=self.U * self.U)


        # Components
        # ----------
        self.I = Set()
        self.M = Set(within=self.I)
        self.YC = Set(within=self.U_YIELD_REACTOR * self.I)

        # Reactions, Utilities, Heat intervals
        # ------------------------------------
        self.R = Set()
        self.UT = Set()
        self.H_UT = Set(within=self.UT)
        self.U_UT = Set(within=self.UT)
        self.HI = Set()

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

        self.DC_SET = Set(within=self.U_DIST * iterator(100))

        self.U_DIST_SUB2 = Set(within=self.U_DIST_SUB * self.U_DIST * iterator(100))


        # Set to describe the scenarios of the 2 stage linear recourse problems
        self.SC = Set()

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

        # uncertain parameters !! dependent on the scenario
        # ------------------------------------------------
        # Flow parameters Split factor
        self.phi = Param(self.U_S, self.I, self.SC, initialize=0)
        # Stoich. Coefficients
        self.gamma = Param(self.U_STOICH_REACTOR, self.I, self.R, self.SC, initialize=0)
        # Conversion Coefficients
        self.theta = Param(self.U_STOICH_REACTOR, self.R, self.M, self.SC, initialize=0)
        # Yield Coefficients
        self.xi = Param(self.U_YIELD_REACTOR, self.I, self.SC, initialize=0)
        # split factors
        self.myu = Param(self.U_CONNECTORS, self.I, self.SC, initialize=0)
        # cost parameters raw material
        self.materialcosts = Param(self.U_S, self.SC, initialize=0)
        # uncertain product prices
        self.ProductPrice = Param(self.U_PP, self.SC, initialize=0)


        # Flow parameters (Split factor, concentrations, full load hours)
        self.conc = Param(self.U, initialize=0, within= Any)
        self.flh = Param(self.U)
        self.MinProduction = Param(self.U_PP, initialize=0)
        self.MaxProduction = Param(self.U_PP, initialize=100000)

        # Decision variable of the Fist recourse stage, thus not dependent on the scenario
        # --------------------------------------------
        # Binary variable for the selection of units
        self.Y = Var(self.U, within=Binary)

        # Decision variable of the second recourse stage
        # ------------------------------------------------
        # Decimal_numbers help to model the distributor equations
        # it sets the degree of "detail" for the distributor
        self.Decimal_numbers = Param(self.DC_SET, self.SC)
        # Binary variable for the selection of splits factors
        self.Y_DIST = Var(self.U_DIST_SUB2, self.SC, within=Binary)


        # Inernt components switch
        self.ic_on = Param(self.U_YIELD_REACTOR, initialize=0)

        # Additional slack parameters (Flow choice, upper bounds, )
        self.kappa_1_lhs_conc = Param(self.U, self.I, initialize=0)
        self.kappa_1_rhs_conc = Param(self.U, self.I, initialize=0)
        self.kappa_2_lhs_conc = Param(self.U, initialize=3)
        self.kappa_2_rhs_conc = Param(self.U, initialize=3)
        self.Names = Param(self.U, within=Any)
        self.alpha = Param(self.U, initialize=100000)

        # upper and lower bounds for source flows
        self.ul = Param(self.U_S, initialize=100000)
        self.ll = Param(self.U_S, initialize=0)







        # Variables
        # --------

        self.FLOW = Var(self.U_CONNECTORS, self.I, self.SC, within=NonNegativeReals)
        self.FLOW_IN = Var(self.U, self.I, self.SC, within=NonNegativeReals)
        self.FLOW_OUT = Var(self.U, self.I, self.SC, within=NonNegativeReals)
        self.FLOW_WASTE = Var(self.U, self.I, self.SC, within=NonNegativeReals)
        self.FLOW_WASTE_TOTAL = Var(self.I, self.SC, within=NonNegativeReals)
        self.FLOW_ADD = Var(self.U_SU,self.SC,  within=NonNegativeReals)
        self.FLOW_ADD_TOT = Var(self.U, self.I, self.SC, within=NonNegativeReals)
        self.FLOW_SUM = Var(self.U, self.SC, within=NonNegativeReals)

        self.FLOW_SOURCE = Var(self.U_S, self.SC, within=NonNegativeReals)

        self.FLOW_DIST = Var(self.U_DIST_SUB2, self.I, self.SC, within=NonNegativeReals)

        self.FLOW_FT = Var(self.U_CONNECTORS, self.SC, within=NonNegativeReals)

        # Constraints
        # -----------

        def MassBalance_1_rule(self, u, i, sc):
            return self.FLOW_IN[u, i, sc] == self.FLOW_ADD_TOT[u, i, sc] + sum(self.flh[uu] / self.flh[u] * self.FLOW[uu, u, i, sc] for uu in self.UU if (uu,u) in self.U_CONNECTORS)

        def MassBalance_2_rule(self, u, i, sc):
            return self.FLOW_ADD_TOT[u, i, sc] == sum( self.FLOW_ADD[u_s, u, sc] * self.phi[u_s, i, sc]
                for u_s in self.U_S
                if (u_s, u) in self.U_SU
            )

        # todo, you could make these equations not depend on the scenario, but only the unit operation, check if this makes sense
        # for the time being also depends on the scenario
        # ----------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------

        def MassBalance_3_rule(self, u_s, u, sc):
            return self.FLOW_ADD[u_s, u, sc] <= self.alpha[u] * self.Y[u]  # Big M constraint

        def MassBalance_4_rule(self, u_s,sc):
            return self.FLOW_SOURCE[u_s, sc] == sum(
                self.FLOW_ADD[u_s, u, sc] * self.flh[u] / self.flh[u_s]
                for u in self.U
                if (u_s, u) in self.U_SU
            )
         # upper and lower bounds for source flows
        def MassBalance_13_rule(self, u_s, sc):
            # if you want to place the bounds according to t/y: self.FLOW_SOURCE[u_s, sc] * self.flh[u_s] <= self.ul[u_s]
            return self.FLOW_SOURCE[u_s, sc]  <= self.ul[u_s]

        def MassBalance_14_rule(self, u_s, sc):
            # if you want to place the bounds according to t/y: self.FLOW_SOURCE[u_s, sc] * self.flh[u_s] >= self.ll[u_s]
            return self.FLOW_SOURCE[u_s, sc]  >= self.ll[u_s]
        # ----------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------


        # stoichimoetric and yield reactor equations
        def MassBalance_5_rule(self, u, i, sc):
            if u in self.U_YIELD_REACTOR:
                if self.ic_on[u] == 1:
                    if (u, i) in self.YC:
                        return (
                            self.FLOW_OUT[u, i, sc]
                            == self.FLOW_IN[u, i, sc]
                            + sum(self.FLOW_IN[u, i, sc]
                                for i in self.I
                                if (u, i) not in self.YC
                            )
                            * self.xi[u, i, sc]
                        )
                    else:
                        return (
                            self.FLOW_OUT[u, i, sc]
                            == sum(
                                self.FLOW_IN[u, i, sc]
                                for i in self.I
                                if (u, i) not in self.YC
                            )
                            * self.xi[u, i, sc]
                        )
                else:
                    return (
                        self.FLOW_OUT[u, i,sc]
                        == sum(self.FLOW_IN[u, i, sc] for i in self.I) * self.xi[u, i, sc]
                    )
            elif u in self.U_STOICH_REACTOR:
                return self.FLOW_OUT[u, i, sc] == self.FLOW_IN[u, i, sc] + sum(
                    self.gamma[u, i, r, sc] * self.theta[u, r, m, sc] * self.FLOW_IN[u, m, sc]
                    for r in self.R
                    for m in self.M
                )
            else:
                return self.FLOW_OUT[u, i, sc] == self.FLOW_IN[u, i,sc]

        def MassBalance_9_rule(self, u, i, sc):
            return self.FLOW_WASTE[u, i, sc] == self.FLOW_OUT[u, i, sc] - sum(
                self.FLOW[u, uu, i, sc] for uu in self.UU if (u,uu) in self.U_CONNECTORS
            )

        def MassBalance_10_rule(self, i, sc):
            return self.FLOW_WASTE_TOTAL[i, sc] == sum(
                self.FLOW_WASTE[u, i, sc] for u in self.U
            )

        # concentration constraints
        def MassBalance_11_rule(self, u, sc):
            if self.kappa_2_lhs_conc[u] == 0 and self.kappa_2_rhs_conc[u] == 0:
                return 1e03 * sum(
                    self.FLOW_OUT[u, i, sc] * self.kappa_1_lhs_conc[u, i, sc] for i in self.I
                ) == 1e03 * self.conc[u] * sum(
                    self.FLOW_OUT[u, i, sc] * self.kappa_1_rhs_conc[u, i] for i in self.I
                )
            elif self.kappa_2_lhs_conc[u] == 0 and self.kappa_2_rhs_conc[u] == 1:
                return 1e03 * sum(
                    self.FLOW_OUT[u, i, sc] * self.kappa_1_lhs_conc[u, i] for i in self.I
                ) == 1e03 * self.conc[u] * sum(
                    self.FLOW_IN[u, i,sc] * self.kappa_1_rhs_conc[u, i] for i in self.I
                )
            elif self.kappa_2_lhs_conc[u] == 1 and self.kappa_2_rhs_conc[u] == 0:
                return 1e03 * sum(
                    self.FLOW_IN[u, i, sc] * self.kappa_1_lhs_conc[u, i] for i in self.I
                ) == 1e03 * self.conc[u] * sum(
                    self.FLOW_OUT[u, i, sc] * self.kappa_1_rhs_conc[u, i] for i in self.I
                )
            elif self.kappa_2_lhs_conc[u] == 1 and self.kappa_2_rhs_conc[u] == 1:
                return 1e03 * sum(self.FLOW_IN[u, i, sc] * self.kappa_1_lhs_conc[u, i] for i in self.I ) == 1e03 * self.conc[u] * sum(self.FLOW_IN[u, i, sc] * self.kappa_1_rhs_conc[u, i] for i in self.I)
            else:
                return Constraint.Skip

        def MassBalance_12_rule(self, u, sc):
            return self.FLOW_SUM[u, sc] == sum(self.FLOW_IN[u, i, sc] for i in self.I)

        def MassBalance_14a_rule(self, up, sc):
            # if you want to place the bounds according to t/y: self.FLOW_SUM[up, sc] * self.flh[up] >= self.MinProduction[up]
            return self.FLOW_SUM[up, sc] >= self.MinProduction[up]

        def MassBalance_14b_rule(self, up, sc):
            # if you want to place the bounds according to t/y: self.FLOW_SUM[up, sc] * self.flh[up] <= self.MaxProduction[up]
            return self.FLOW_SUM[up, sc]  <= self.MaxProduction[up]

        def MassBalance_6_rule(self, u, uu, i, sc):
            if (u, uu) not in self.U_DIST_SUB:
                    if (u, uu) in self.U_CONNECTORS:
                        return self.FLOW[u, uu, i, sc] <= self.myu[u, uu, i, sc] * self.FLOW_OUT[
                            u, i, sc
                            ] + self.alpha[u] * (1 - self.Y[uu])
                    else:
                        return Constraint.Skip

            else:
                return self.FLOW[u, uu, i, sc] <= sum(
                    self.FLOW_DIST[u, uu, uk, k, i, sc]
                    for (uk, k) in self.DC_SET
                    if (u, uu, uk, k) in self.U_DIST_SUB2
                ) + self.alpha[u] * (1 - self.Y[uu])

        def MassBalance_7_rule(self, u, uu, i, sc):
            if (u,uu) in self.U_CONNECTORS:
                return self.FLOW[u, uu, i, sc] <= self.alpha[u] * self.Y[uu]
            else:
                return Constraint.Skip


        def MassBalance_8_rule(self, u, uu, i, sc):
            if (u, uu) not in self.U_DIST_SUB:
                if (u, uu) in self.U_CONNECTORS:
                    return self.FLOW[u, uu, i, sc] >= self.myu[u, uu, i, sc] * self.FLOW_OUT[
                        u, i, sc
                        ] - self.alpha[u] * (1 - self.Y[uu])
                else:
                    return Constraint.Skip
            else:
                return self.FLOW[u, uu, i, sc] >= sum(
                    self.FLOW_DIST[u, uu, uk, k, i, sc]
                    for (uk, k) in self.DC_SET
                    if (u, uu, uk, k) in self.U_DIST_SUB2
                ) - self.alpha[u] * (1 - self.Y[uu])

        # Distributor Equations

        def MassBalance_15a_rule(self, u, uu, uk, k, i, sc):
            return self.FLOW_DIST[u, uu, uk, k, i, sc] <= self.Decimal_numbers[
                u, k, sc
            ] * self.FLOW_OUT[u, i, sc] + self.alpha[u] * (1 - self.Y_DIST[u, uu, uk, k, sc])

        def MassBalance_15b_rule(self, u, uu, uk, k, i, sc):
            return self.FLOW_DIST[u, uu, uk, k, i, sc] >= self.Decimal_numbers[
                u, k, sc
            ] * self.FLOW_OUT[u, i, sc] - self.alpha[u] * (1 - self.Y_DIST[u, uu, uk, k, sc])

        def MassBalance_15c_rule(self, u, uu, uk, k, i, sc):
            return (
                self.FLOW_DIST[u, uu, uk, k, i, sc]
                <= self.alpha[u] * self.Y_DIST[u, uu, uk, k, sc]
            )

        def MassBalance_16_rule(self, u, i, sc):
            return self.FLOW_OUT[u, i, sc] == sum(
                self.FLOW[u, uu, i, sc] for uu in self.U if (u, uu) in self.U_DIST_SUB
            )

        def MassBalance_17_rule(self, u, uu, sc):
            return self.FLOW_FT[u, uu, sc] == sum(self.FLOW[u, uu, i, sc] for i in self.I)

        self.MassBalance_1 = Constraint(self.U, self.I, self.SC, rule=MassBalance_1_rule)
        self.MassBalance_2 = Constraint(self.U, self.I, self.SC, rule=MassBalance_2_rule)
        self.MassBalance_3 = Constraint(self.U_SU, self.SC,  rule=MassBalance_3_rule)
        self.MassBalance_4 = Constraint(self.U_S, self.SC, rule=MassBalance_4_rule)
        self.MassBalance_13 = Constraint(self.U_S, self.SC,  rule=MassBalance_13_rule)
        self.MassBalance_14 = Constraint(self.U_S, self.SC,  rule=MassBalance_14_rule)

        self.MassBalance_5 = Constraint(self.U, self.I, self.SC,  rule=MassBalance_5_rule)
        self.MassBalance_6 = Constraint(self.U, self.UU, self.I, self.SC, rule=MassBalance_6_rule)
        self.MassBalance_7 = Constraint(self.U, self.UU, self.I, self.SC, rule=MassBalance_7_rule)
        self.MassBalance_8 = Constraint(self.U, self.UU, self.I, self.SC, rule=MassBalance_8_rule)
        self.MassBalance_9 = Constraint(self.U, self.I, self.SC, rule=MassBalance_9_rule)
        self.MassBalance_10 = Constraint(self.I, self.SC, rule=MassBalance_10_rule)
        self.MassBalance_11 = Constraint(self.U, self.SC, rule=MassBalance_11_rule)
        self.MassBalance_12 = Constraint(self.U, self.SC, rule=MassBalance_12_rule)
        self.MassBalance_14a = Constraint(self.U_PP, self.SC, rule=MassBalance_14a_rule)
        self.MassBalance_14b = Constraint(self.U_PP, self.SC, rule=MassBalance_14b_rule)
        self.MassBalance_15a = Constraint(self.U_DIST_SUB2, self.I, self.SC, rule=MassBalance_15a_rule)
        self.MassBalance_15b = Constraint(
            self.U_DIST_SUB2, self.I, self.SC, rule=MassBalance_15b_rule
        )
        self.MassBalance_15c = Constraint(
            self.U_DIST_SUB2, self.I, self.SC, rule=MassBalance_15c_rule
        )
        self.MassBalance_16 = Constraint(self.U_DIST, self.I, self.SC, rule=MassBalance_16_rule)
        self.MassBalance_17 = Constraint(self.U_CONNECTORS, self.SC, rule=MassBalance_17_rule)

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
        self.tau = Param(self.U, self.UT, initialize=0, within= Any)
        self.tau_h = Param(self.H_UT, self.U, initialize=0)
        self.tau_c = Param(self.H_UT, self.U, initialize=0)
        self.beta = Param(self.U, self.H_UT, self.HI, initialize=0)

        # Slack Parameters (Flow Choice, HEN, Upper bounds)
        self.kappa_1_ut = Param(self.U, self.UT, self.I, initialize=0)
        self.kappa_2_ut = Param(self.U, self.UT, initialize=3)
        self.kappa_3_heat = Param(self.U, self.HI, initialize=0)
        self.kappa_3_heat2 = Param(self.U, self.HI, initialize=0)
        self.alpha_hex = Param(initialize=100000)
        self.Y_HEX = Var(self.HI, within=Binary)

        # Additional unit operations (Heat Pump, EL / Heat Generator)
        self.COP_HP = Param(initialize=0)
        self.Efficiency_TUR = Param(self.U_TUR, initialize=0)
        self.Efficiency_FUR = Param(self.U_FUR, initialize=0)
        self.LHV = Param(self.I, initialize=0)
        self.H = Param()

        # Variables
        # ---------

        # Second stage recourse variables
        # -------------------------------------------------------------------------------------------------
        # Reference Flows for Demand calculation
        self.REF_FLOW_UT = Var(self.U, self.UT, self.SC)


        # Electricity Demand and Production, Heat Pump

        self.ENERGY_DEMAND = Var(self.U, self.U_UT, self.SC)
        self.ENERGY_DEMAND_TOT = Var(self.U_UT, self.SC)
        self.EL_PROD_1 = Var(self.U_TUR, self.SC, within=NonNegativeReals)

        # Heat Demand and Production of Heat Pump
        self.ENERGY_DEMAND_HP_EL = Var(self.SC, within=NonNegativeReals)

        # Heating and cooling demand (Interval, Unit, Resi, Defi, Cooling, Exchange, Production , HP)
        self.ENERGY_DEMAND_HEAT = Var(self.U, self.HI, self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_COOL = Var(self.U, self.HI, self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_UNIT = Var(self.U, self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_COOL_UNIT = Var(self.U, self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_RESI = Var(self.HI, self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_DEFI = Var(self.HI, self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_COOLING = Var(self.SC, within=NonNegativeReals)
        self.ENERGY_EXCHANGE = Var(self.HI, self.SC, within=NonNegativeReals)
        self.EXCHANGE_TOT = Var(self.SC)
        self.ENERGY_DEMAND_HEAT_PROD_USE = Var(self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_PROD_SELL = Var(self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_HEAT_PROD = Var(self.U_FUR, self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_HP = Var(self.SC, within=NonNegativeReals)
        self.ENERGY_DEMAND_HP_USE = Var(self.SC, within=NonNegativeReals)
        # -------------------------------------------------------------------------------------------------


        # molecular weight and heat capacity parameters
        self.MW = Param(self.I, initialize=1)
        self.CP = Param(self.I, initialize=0)

        # Constraints
        # -----------

        # Utilities other than heating and cooling

        def UtilityBalance_1_rule(self, u, ut, sc):
            if self.kappa_2_ut[u, ut] == 1:
                return self.REF_FLOW_UT[u, ut, sc] == sum(
                    self.FLOW_IN[u, i, sc] * self.kappa_1_ut[u, ut, i] for i in self.I
                )
            elif self.kappa_2_ut[u, ut] == 0:
                return self.REF_FLOW_UT[u, ut, sc] == sum(
                    self.FLOW_OUT[u, i, sc] * self.kappa_1_ut[u, ut, i] for i in self.I
                )
            elif self.kappa_2_ut[u, ut] == 4:
                return self.REF_FLOW_UT[u, ut, sc] == sum(
                    self.FLOW_OUT[u, i, sc] / self.MW[i] * self.kappa_1_ut[u, ut, i]
                    for i in self.I
                )
            elif self.kappa_2_ut[u, ut] == 2:
                return self.REF_FLOW_UT[u, ut, sc] == sum(
                    self.FLOW_IN[u, i, sc] / self.MW[i] * self.kappa_1_ut[u, ut, i]
                    for i in self.I
                )
            elif self.kappa_2_ut[u, ut] == 5:
                return self.REF_FLOW_UT[u, ut, sc] == sum(
                    0.000277
                    * self.CP[i]
                    * self.FLOW_IN[u, i, sc]
                    * self.kappa_1_ut[u, ut, i]
                    for i in self.I
                )
            elif self.kappa_2_ut[u, ut] == 6:
                return self.REF_FLOW_UT[u, ut, sc] == sum(
                    0.000277
                    * self.CP[i]
                    * self.FLOW_OUT[u, i, sc]
                    * self.kappa_1_ut[u, ut, i]
                    for i in self.I
                )
            else:
                return self.REF_FLOW_UT[u, ut, sc] == 0

        def UtilityBalance_2_rule(self, u, ut, sc):
            return (
                self.ENERGY_DEMAND[u, ut, sc] == self.REF_FLOW_UT[u, ut, sc] * self.tau[u, ut]
            )

        def UtilityBalance_3_rule(self, ut, sc):
            if ut == "Electricity":
                if self.heat_pump_options["active"] is True:
                    # todo make sure this does not have any unintended side effects
                    return self.ENERGY_DEMAND_TOT[ut, sc] == sum(
                        self.ENERGY_DEMAND[u, ut, sc] * self.flh[u] for u in self.U
                    ) - sum(self.EL_PROD_1[u, sc] * self.flh[u] for u in self.U_TUR) + self.ENERGY_DEMAND_HP_EL[sc]
                else:
                    return self.ENERGY_DEMAND_TOT[ut,sc] == sum(
                        self.ENERGY_DEMAND[u, ut, sc] * self.flh[u] for u in self.U
                    ) - sum(self.EL_PROD_1[u, sc] * self.flh[u] for u in self.U_TUR)
            else:
                return self.ENERGY_DEMAND_TOT[ut, sc] == sum(
                    self.ENERGY_DEMAND[u, ut, sc] * self.flh[u] for u in self.U
                )

        # Electrictiy Balance for Production from Turbines

        def ElectricityBalance_1_rule(self, u, sc):
            return self.EL_PROD_1[u, sc] == self.Efficiency_TUR[u] * sum(
                self.LHV[i] * self.FLOW_IN[u, i, sc] for i in self.I
            )

        self.ElectricityBalance_1 = Constraint(self.U_TUR, self.SC, rule=ElectricityBalance_1_rule)
        self.UtilityBalance_1 = Constraint(self.U, self.UT, self.SC, rule=UtilityBalance_1_rule)
        self.UtilityBalance_2 = Constraint(self.U, self.U_UT, self.SC, rule=UtilityBalance_2_rule)
        self.UtilityBalance_3 = Constraint(self.U_UT, self.SC, rule=UtilityBalance_3_rule)

        # Heat and Cooling Balance (Demand)

        def HeatBalance_1_rule(self, u, hi, sc):
            return self.ENERGY_DEMAND_HEAT[u, hi, sc] == sum(
                self.beta[u, ut, hi] * self.tau_c[ut, u] * self.REF_FLOW_UT[u, ut, sc]
                for ut in self.H_UT
            )

        def HeatBalance_2_rule(self, u, hi, sc):
            return self.ENERGY_DEMAND_COOL[u, hi, sc] == sum(
                self.beta[u, ut, hi] * self.tau_h[ut, u] * self.REF_FLOW_UT[u, ut, sc]
                for ut in self.H_UT
            )

        # Heating anc Cooling Balance (Either with or without Heat pump)
        # Rigorous HEN Optimization approach

        if self.heat_pump_options["active"] is True:
            hp_tin = self.heat_pump_options["t_in"]
            hp_tout = self.heat_pump_options["t_out"]

            def HeatBalance_3_rule(self, u, hi, sc):
                k = len(self.HI)
                if hi == 1:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        + self.ENERGY_DEMAND_HEAT_PROD_USE[sc]
                        - self.ENERGY_DEMAND_HEAT_RESI[hi, sc]
                        - self.ENERGY_EXCHANGE[hi, sc]
                        == 0
                    )
                elif hi == hp_tin:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1, sc]
                        - self.ENERGY_DEMAND_HEAT_RESI[hi, sc]
                        - self.ENERGY_DEMAND_HP[sc]
                        - self.ENERGY_EXCHANGE[hi, sc]
                        == 0
                    )
                elif hi == k:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1, sc]
                        - self.ENERGY_DEMAND_COOLING[sc]
                        - self.ENERGY_EXCHANGE[hi, sc]
                        == 0
                    )
                else:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1, sc]
                        - self.ENERGY_EXCHANGE[hi, sc]
                        - self.ENERGY_DEMAND_HEAT_RESI[hi, sc]
                        == 0
                    )

            def HeatBalance_4_rule(self, u, hi, sc):
                if hi == 1:
                    return (
                        sum(
                            self.ENERGY_DEMAND_COOL[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        - self.ENERGY_EXCHANGE[hi, sc]
                        - self.ENERGY_DEMAND_HEAT_DEFI[hi, sc]
                        == 0
                    )
                elif hi == hp_tout:
                    return (
                        sum(
                            self.ENERGY_DEMAND_COOL[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        - self.ENERGY_DEMAND_HEAT_DEFI[hi, sc]
                        - self.ENERGY_EXCHANGE[hi, sc]
                        - self.ENERGY_DEMAND_HP_USE[sc]
                        == 0
                    )
                else:
                    return (
                        sum(
                            self.ENERGY_DEMAND_COOL[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        - self.ENERGY_EXCHANGE[hi, sc]
                        - self.ENERGY_DEMAND_HEAT_DEFI[hi, sc]
                        == 0
                    )

            def HeatBalance_8_rule(self, sc):
                return self.ENERGY_DEMAND_HP_USE[sc] == self.ENERGY_DEMAND_HP[sc] / (
                    1 - (1 / self.COP_HP)
                )

            def HeatBalance_9_rule(self, sc):
                return self.ENERGY_DEMAND_HP_EL[sc] == self.ENERGY_DEMAND_HP[sc] / (
                    self.COP_HP - 1
                )

            self.HeatBalance_8 = Constraint(self.SC, rule=HeatBalance_8_rule)
            self.HeatBalance_9 = Constraint(self.SC, rule=HeatBalance_9_rule)

        else:

            def HeatBalance_3_rule(self, u, hi, sc):
                k = len(self.HI)
                if hi == 1:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        + self.ENERGY_DEMAND_HEAT_PROD_USE[sc]
                        - self.ENERGY_DEMAND_HEAT_RESI[hi, sc]
                        - self.ENERGY_EXCHANGE[hi, sc]
                        == 0
                    )
                elif hi == k:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1, sc]
                        - self.ENERGY_DEMAND_COOLING[sc]
                        - self.ENERGY_EXCHANGE[hi, sc]
                        == 0
                    )
                else:
                    return (
                        sum(
                            self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                            for u in self.U
                        )
                        + self.ENERGY_DEMAND_HEAT_RESI[hi - 1, sc]
                        - self.ENERGY_EXCHANGE[hi,sc]
                        - self.ENERGY_DEMAND_HEAT_RESI[hi, sc]
                        == 0
                    )

            def HeatBalance_4_rule(self, u, hi, sc):
                return (
                    sum(
                        self.ENERGY_DEMAND_COOL[u, hi, sc] * self.flh[u] / self.H
                        for u in self.U
                    )
                    - self.ENERGY_EXCHANGE[hi, sc]
                    - self.ENERGY_DEMAND_HEAT_DEFI[hi, sc]
                    == 0
                )

            def HeatBalance_8_rule(self, sc):
                return self.ENERGY_DEMAND_HP_USE[sc] == 0

            def HeatBalance_9_rule(self, sc):
                return self.ENERGY_DEMAND_HP_EL[sc] == 0

            self.HeatBalance_8 = Constraint(self.SC, rule=HeatBalance_8_rule)
            self.HeatBalance_9 = Constraint(self.SC, rule=HeatBalance_9_rule)

        #  Exchange Constraints, Production and Sell etc.
        def HeatBalance_5_rule(self, hi, sc):
            return self.ENERGY_EXCHANGE[hi, sc] <= sum(
                self.ENERGY_DEMAND_COOL[u, hi, sc] * self.flh[u] / self.H for u in self.U
            )

        def HeatBalance_6_rule(self, hi, sc):
            if hi == 1:
                return (
                    self.ENERGY_EXCHANGE[hi, sc]
                    <= sum(
                        self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                        for u in self.U
                    )
                    + self.ENERGY_DEMAND_HEAT_PROD_USE[sc]
                )
            else:
                return (
                    self.ENERGY_EXCHANGE[hi, sc]
                    <= sum(
                        self.ENERGY_DEMAND_HEAT[u, hi, sc] * self.flh[u] / self.H
                        for u in self.U
                    )
                    + self.ENERGY_DEMAND_HEAT_RESI[hi - 1, sc]
                )

        def HeatBalance_7_rule(self, sc):
            return self.EXCHANGE_TOT[sc] == sum(self.ENERGY_EXCHANGE[hi, sc] for hi in self.HI)

        def HeatBalance_12_rule(self, hi, sc):
            return self.ENERGY_EXCHANGE[hi, sc] <= self.Y_HEX[hi] * self.alpha_hex

        def HeatBalance_13_rule(self, u, sc):
            return self.ENERGY_DEMAND_HEAT_PROD[u, sc] == self.Efficiency_FUR[u] * sum(
                self.LHV[i] * self.FLOW_IN[u, i, sc] for i in self.I
            )

        def HeatBalance_14_rule(self, u, sc):
            return self.ENERGY_DEMAND_HEAT_UNIT[u, sc] == sum(
                self.ENERGY_DEMAND_COOL[u, hi, sc] for hi in self.HI
            )

        def HeatBalance_15_rule(self, u, sc):
            return self.ENERGY_DEMAND_COOL_UNIT[u, sc] == sum(
                self.ENERGY_DEMAND_HEAT[u, hi, sc] for hi in self.HI
            )

        def HeatBalance_16_rule(self, sc):
            return (
                self.ENERGY_DEMAND_HEAT_PROD_USE[sc]
                == sum(
                    self.ENERGY_DEMAND_HEAT_PROD[u, sc] * self.flh[u] / self.H
                    for u in self.U_FUR
                )
                - self.ENERGY_DEMAND_HEAT_PROD_SELL[sc]
            )

        self.HeatBalance_1 = Constraint(self.U, self.HI, self.SC, rule=HeatBalance_1_rule)
        self.HeatBalance_2 = Constraint(self.U, self.HI, self.SC,rule=HeatBalance_2_rule)
        self.HeatBalance_3 = Constraint(self.U, self.HI, self.SC, rule=HeatBalance_3_rule)
        self.HeatBalance_4 = Constraint(self.U, self.HI, self.SC, rule=HeatBalance_4_rule)
        self.HeatBalance_5 = Constraint(self.HI, self.SC, rule=HeatBalance_5_rule)
        self.HeatBalance_6 = Constraint(self.HI, self.SC, rule=HeatBalance_6_rule)
        self.HeatBalance_7 = Constraint(self.SC, rule=HeatBalance_7_rule)

        self.HeatBalance_12 = Constraint(self.HI, self.SC, rule=HeatBalance_12_rule)
        self.HeatBalance_13 = Constraint(self.U_FUR, self.SC, rule=HeatBalance_13_rule)
        self.HeatBalance_14 = Constraint(self.U, self.SC, rule=HeatBalance_14_rule)
        self.HeatBalance_15 = Constraint(self.U, self.SC, rule=HeatBalance_15_rule)
        self.HeatBalance_16 = Constraint(self.SC,rule=HeatBalance_16_rule)

    # **** COST BALANCES *****
    # -------------------------

    def create_EconomicEvaluation(self):
        """
        Description
        -------
        This method creates the PYOMO parameters and variables
        that are necessary for the general Cost Calculation (eg. detla_ut, COST_UT etc.).
        Afterwards Cost calculation equations are written as PYOMO Constraints.
        """

        # Parameter
        # ---------

        # Scenario with max costs associated with it
        #self.SC_MAX = Param()
        # 'sc1' wil always be the max cost scenario

        # Specific costs (Utility, raw materials, Product prices)

        self.delta_ut = Param(self.U_UT, initialize=0)
        self.delta_q = Param(self.HI, initialize=30)
        self.delta_cool = Param(initialize=15)



        # Cost factors (CAPEX, Heat Pump)
        self.DC = Param(self.U, initialize=0)
        self.IDC = Param(self.U, initialize=0)
        self.ACC_Factor = Param(self.U, initialize=0)

        self.HP_ACC_Factor = Param(initialize=1)
        self.HP_Costs = Param(initialize=1)

        # Piecewise Linear CAPEX
        self.lin_CAPEX_x = Param(self.U_C, self.J, initialize=0)
        self.lin_CAPEX_y = Param(self.U_C, self.J, initialize=0)
        self.kappa_1_capex = Param(self.U_C, self.I, initialize=0)
        self.kappa_2_capex = Param(self.U_C, initialize=5)

        # OPEX factors

        self.K_OM = Param(self.U_C, initialize=0.04)

        # Variables
        # ---------

        # Piece-Wise Linear CAPEX
        self.lin_CAPEX_s = Var(self.U_C, self.JI, within=NonNegativeReals)
        self.lin_CAPEX_z = Var(self.U_C, self.JI, within=Binary)
        self.lin_CAPEX_lambda = Var(self.U_C, self.J, bounds=(0, 1))
        self.REF_FLOW_CAPEX = Var(self.U_C, within=NonNegativeReals)

        # CAPEX (Units, Returning costs, Heat Pump, Total)
        self.EC = Var(self.U_C, within=NonNegativeReals)
        self.FCI = Var(self.U_C, within=NonNegativeReals)
        self.ACC = Var(self.U_C, within=NonNegativeReals)
        self.to_acc = Param(self.U_C, initialize=0)
        self.TO_CAPEX = Var(self.U_C, within=NonNegativeReals)
        self.TO_CAPEX_TOT = Var(within=NonNegativeReals)
        self.ACC_HP = Var(within=NonNegativeReals)
        self.HENCOST = Var(self.HI, within=NonNegativeReals)

        self.CAPEX = Var()

        # OPEX (Raw Materials, O&M, , UtilitiesTotal, Profits) depends on the scenarios
        self.RM_COST = Var(self.U_C, within=NonNegativeReals)
        self.RM_COST_TOT = Var(self.SC, within=NonNegativeReals)
        self.M_COST = Var(self.U_C)
        self.M_COST_TOT = Var(within=NonNegativeReals)
        self.O_H = Var()
        self.O_COST = Var()
        self.OM_COST = Var(within=NonNegativeReals)
        self.OPEX = Var(self.SC)

        # Utilitiy Costs ( El, Heat, El-TOT, HEN)
        self.ENERGY_COST = Var(self.U_UT, self.SC)
        self.COST_HEAT = Var(self.HI)
        self.COST_UT = Var(self.SC)
        self.ELCOST = Var(self.SC)
        self.HEATCOST = Var(self.HI, self.SC)
        self.C_TOT = Var(self.SC)

        self.UtCosts = Var(self.SC)

        # variables depended on the scenarios
        self.PROFITS = Var(self.U_PP, self.SC)
        self.PROFITS_TOT = Var(self.SC)
        self.TAC = Var(self.SC)


        # Constraints
        # -----------

        # CAPEX Calculation (Reference Flow, Piece-Wise linear Lambda Constraints)

        def CapexEquation_1_rule(self, u):
            if self.kappa_2_capex[u] == 1:
                return self.REF_FLOW_CAPEX[u] == sum(
                    self.FLOW_IN[u, i, 'sc1'] * self.kappa_1_capex[u, i] for i in self.I
                )
            elif self.kappa_2_capex[u] == 0:
                return self.REF_FLOW_CAPEX[u] == sum(
                    self.FLOW_OUT[u, i, 'sc1'] * self.kappa_1_capex[u, i] for i in self.I
                )
            elif self.kappa_2_capex[u] == 2:
                return self.REF_FLOW_CAPEX[u] == self.ENERGY_DEMAND[u, "Electricity", 'sc1']

            elif self.kappa_2_capex[u] == 3:
                return self.REF_FLOW_CAPEX[u] == self.ENERGY_DEMAND_HEAT_PROD[u, 'sc1']

            elif self.kappa_2_capex[u] == 4:
                return self.REF_FLOW_CAPEX[u] == self.EL_PROD_1[u, 'sc1']
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
                == self.HP_ACC_Factor * self.HP_Costs * self.ENERGY_DEMAND_HP_USE['sc1']
            )

        def Cap(self):
            return self.ACC_HP == self.ACC_H / 1000000

        self.Xap = Constraint(rule=Cap)


        # heat exchanger costs
        def HEN_CostBalance_CAPEX_1_rule(self, hi):
            return (self.HENCOST[hi] <= 13.459 * self.ENERGY_EXCHANGE[hi, 'sc1']
                    + 3.3893 + self.alpha_hex * (1 - self.Y_HEX[hi])) # sc1 max energy exchange scenario

        def HEN_CostBalance_CAPEX_2_rule(self, hi):
            return (self.HENCOST[hi] >= 13.459 * self.ENERGY_EXCHANGE[hi, 'sc1']
                    + 3.3893 - self.alpha_hex * (1 - self.Y_HEX[hi])) # sc1 max energy exchange scenario

        def HEN_CostBalance_CAPEX_3_rule(self, hi):
            return self.HENCOST[hi] <= self.Y_HEX[hi] * self.alpha_hex

        self.CapexEquation_HEN_1 = Constraint(self.HI, rule=HEN_CostBalance_CAPEX_1_rule)
        self.CapexEquation_HEN_2 = Constraint(self.HI, rule=HEN_CostBalance_CAPEX_2_rule)
        self.CapexEquation_HEN_3 = Constraint(self.HI, rule=HEN_CostBalance_CAPEX_3_rule)

        def CapexEquation_11_rule(self, u):
            return self.TO_CAPEX[u] == self.to_acc[u] * self.EC[u]

        def CapexEquation_12_rule(self): # reoccurring costs of equipment
            return self.TO_CAPEX_TOT == sum(self.TO_CAPEX[u] for u in self.U_C)

        def CapexEquation_10_rule(self):
            return (
                self.CAPEX
                == sum(self.ACC[u] for u in self.U_C)       # annual capital costs
                + self.ACC_HP                               # heat pump capital costs
                + self.TO_CAPEX_TOT                         # reoccurring costs of equipment
                + sum(self.HENCOST[hi] for hi in self.HI)   # HEN capital costs
            )

        self.CapexEquation_1 = Constraint(self.U_C, rule=CapexEquation_1_rule)
        self.CapexEquation_2 = Constraint(self.U_C, rule=CapexEquation_2_rule)
        self.CapexEquation_3 = Constraint(self.U_C, rule=CapexEquation_3_rule)
        self.CapexEquation_4 = Constraint(self.U_C, rule=CapexEquation_4_rule)
        self.CapexEquation_5 = Constraint(self.U_C, self.JI, rule=CapexEquation_5_rule)
        self.CapexEquation_6 = Constraint(self.U_C, self.J, rule=CapexEquation_6_rule)
        self.CapexEquation_7 = Constraint(self.U_C, rule=CapexEquation_7_rule)
        self.CapexEquation_8 = Constraint(self.U_C, rule=CapexEquation_8_rule)
        self.CapexEquation_9 = Constraint(rule=CapexEquation_9_rule)
        self.CapexEquation_10 = Constraint(rule=CapexEquation_10_rule)
        self.CapexEquation_11 = Constraint(self.U_C, rule=CapexEquation_11_rule)
        self.CapexEquation_12 = Constraint(rule=CapexEquation_12_rule)


        # OPEX Calculation (HEN Costs: Heating / Cooling, CAPEX)

        def HEN_CostBalance_1_rule(self, hi, sc):
            return (
                self.HEATCOST[hi, sc]
                == self.ENERGY_DEMAND_HEAT_DEFI[hi, sc] * self.delta_q[hi] * self.H
            )

        def HEN_CostBalance_2_rule(self, sc):
            return self.UtCosts[sc] == (
                sum(self.HEATCOST[hi, sc] for hi in self.HI)
                - self.ENERGY_DEMAND_HEAT_PROD_SELL[sc] * self.H * self.delta_q[1] * 0.7
                + self.ENERGY_DEMAND_COOLING[sc] * self.H * self.delta_cool
            )

        def HEN_CostBalance_3_rule(self, sc):
            return (
                self.ELCOST[sc]
                == self.ENERGY_DEMAND_HP_EL[sc]
                * self.delta_ut["Electricity"]
                * self.H
                / 1000
            )

        # selling buying of energy see UtCosts (HEN_CostBalance_2_rule)
        def HEN_CostBalance_6_rule(self, sc):
            return self.C_TOT[sc] == self.UtCosts[sc]/1000000 # euro to million euro conversion


        self.HEN_CostBalance_1 = Constraint(self.HI, self.SC, rule=HEN_CostBalance_1_rule)
        self.HEN_CostBalance_2 = Constraint(self.SC,rule=HEN_CostBalance_2_rule)
        self.HEN_CostBalance_3 = Constraint(self.SC,rule=HEN_CostBalance_3_rule)
        self.HEN_CostBalance_6 = Constraint(self.SC, rule=HEN_CostBalance_6_rule)

        # Utility Costs (Electricity/Chilling)

        def Ut_CostBalance_1_rule(self, ut, sc):
            return (
                self.ENERGY_COST[ut, sc]
                == self.ENERGY_DEMAND_TOT[ut, sc] * self.delta_ut[ut] / 1000000 # euro to million euro conversion
            )

        self.Ut_CostBalance_1 = Constraint(self.U_UT, self.SC, rule=Ut_CostBalance_1_rule)

        # Raw Materials and Operating and Maintenance

        # RM = Raw Materials
        def RM_CostBalance_1_rule(self,sc):
            return self.RM_COST_TOT[sc] == sum(
                self.materialcosts[u_s, sc] * self.FLOW_SOURCE[u_s, sc] * self.flh[u_s] / 1000000 # m€ to million euro conversion
                for u_s in self.U_S)

        # OM = Operation and maintenance not dependent on the scenarios but the fixed capital costs
        def OM_CostBalance_1_rule(self, u):
            return self.M_COST[u] == self.K_OM[u] * self.FCI[u]

        def OM_CostBalance_2_rule(self):
            return self.M_COST_TOT == sum(self.M_COST[u] for u in self.U_C)

        # Total OPEX
        def Opex_1_rule(self, sc):
            return (
                self.OPEX[sc]
                == self.M_COST_TOT                                    # operating and maintenance
                + self.RM_COST_TOT[sc]                                # raw materials
                + sum(self.ENERGY_COST[ut,sc] for ut in self.U_UT)    # utilities electricity and chilling
                + self.C_TOT[sc]                                      # HEN
                + self.ELCOST[sc]                                     # electricity
            )

        self.RM_CostBalance_1 = Constraint(self.SC, rule=RM_CostBalance_1_rule)
        self.OM_CostBalance_1 = Constraint(self.U_C, rule=OM_CostBalance_1_rule)
        self.OM_CostBalance_2 = Constraint(rule=OM_CostBalance_2_rule)
        self.OpexEquation = Constraint(self.SC, rule=Opex_1_rule)

        # Profits

        def Profit_1_rule(self, u, sc):
            return (
                self.PROFITS[u, sc]
                == sum(self.FLOW_IN[u, i, sc] for i in self.I) * self.ProductPrice[u,sc] / 1000000 # m€ to million euro conversion
            )

        def Profit_2_rule(self, sc):
            return (
                self.PROFITS_TOT[sc] == sum(self.PROFITS[u, sc] for u in self.U_PP) * self.H
            )

        self.ProfitEquation_1 = Constraint(self.U_PP, self.SC, rule=Profit_1_rule)
        self.ProfitEquation_2 = Constraint(self.SC, rule=Profit_2_rule)

        # Total Annualized Costs

        def TAC_1_rule(self, sc):
            return self.TAC[sc] == (self.CAPEX + self.OPEX[sc] - self.PROFITS_TOT[sc])

        self.TAC_Equation = Constraint(self.SC, rule=TAC_1_rule)


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
        self.em_fac_ut = Param(self.UT, initialize=0)
        self.em_fac_comp = Param(self.I, initialize=0)
        self.em_fac_prod = Param(self.U_PP, initialize=0)
        self.em_fac_unit = Param(self.U_C, initialize=0)
        self.em_fac_source = Param(self.U_S, initialize=0)

        # Lifetime of Units
        self.LT = Param(self.U, initialize=1)

        # Variables
        # ---------

        self.GWP_UNITS = Var(self.U_C)
        self.GWP_CREDITS = Var(self.U_PP, self.SC)
        self.GWP_CAPTURE = Var(self.SC)
        self.GWP_U = Var(self.U, self.SC)
        self.GWP_UT = Var(self.UT, self.SC)
        self.GWP_TOT = Var(self.SC)

        # Constraints
        # -----------

        def GWP_1_rule(self, u, sc):
            return self.GWP_U[u, sc] == self.flh[u] * sum(
                self.FLOW_WASTE[u, i, sc] * self.em_fac_comp[i] for i in self.I
            )

        def GWP_2_rule(self, ut, sc):
            if ut == "Electricity":
                return (
                    self.GWP_UT[ut, sc]
                    == (self.ENERGY_DEMAND_TOT[ut, sc] + self.ENERGY_DEMAND_HP_EL[sc] * self.H)
                    * self.em_fac_ut[ut]
                )
            else:
                return (
                    self.GWP_UT[ut, sc] == self.ENERGY_DEMAND_TOT[ut, sc] * self.em_fac_ut[ut]
                )

        def GWP_3_rule(self, sc):
            return self.GWP_UT["Heat", sc] == self.em_fac_ut["Heat"] * self.H * (
                sum(self.ENERGY_DEMAND_HEAT_DEFI[hi, sc] for hi in self.HI)
                - self.ENERGY_DEMAND_HEAT_PROD_SELL[sc] * 0.7
            )

        def GWP_5_rule(self, sc):
            return self.GWP_UT["Heat2", sc] == 0

        def GWP_6_rule(self, u):
            return self.GWP_UNITS[u] == self.em_fac_unit[u] / self.LT[u] * self.Y[u] # what is this ???????

        def GWP_7_rule(self, u, sc):
            return (
                self.GWP_CREDITS[u, sc]
                == self.em_fac_prod[u]
                * sum(self.FLOW_IN[u, i, sc] for i in self.I) # todo check if this is correct, should be a nested sum (only the productpools are relevant I belive) see page 53 eq 3.80
                * self.flh[u]
            )

        def GWP_8_rule(self, sc):
            return self.GWP_CAPTURE[sc] == sum(
                self.FLOW_SOURCE[u_s, sc] * self.flh[u_s] * self.em_fac_source[u_s]
                for u_s in self.U_S
            )

        def GWP_4_rule(self, sc):
            return self.GWP_TOT[sc] == sum(self.GWP_U[u, sc] for u in self.U_C) + sum(
                self.GWP_UT[ut, sc] for ut in self.UT
            ) - self.GWP_CAPTURE[sc] - sum(self.GWP_CREDITS[u,sc] for u in self.U_PP) + sum(
                self.GWP_UNITS[u] for u in self.U_C
            )

        self.EnvironmentalEquation1 = Constraint(self.U_C, self.SC, rule=GWP_1_rule)
        self.EnvironmentalEquation2 = Constraint(self.U_UT, self.SC, rule=GWP_2_rule)
        self.EnvironmentalEquation3 = Constraint(self.SC, rule=GWP_3_rule)
        self.EnvironmentalEquation4 = Constraint(self.SC, rule=GWP_4_rule)
        self.EnvironmentalEquation5 = Constraint(self.SC, rule=GWP_5_rule)

        self.EnvironmentalEquation6 = Constraint(self.U_C, rule=GWP_6_rule)

        self.EnvironmentalEquation7 = Constraint(self.U_PP, self.SC, rule=GWP_7_rule)
        self.EnvironmentalEquation8 = Constraint(self.SC, rule=GWP_8_rule)

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

        self.FWD_UT1 = Var(self.SC)
        self.FWD_UT2 = Var(self.SC)
        self.FWD_S = Var(self.SC)
        self.FWD_C = Var(self.SC)
        self.FWD_TOT = Var(self.SC)

        self.fw_fac_source = Param(self.U_S, initialize=0)
        self.fw_fac_ut = Param(self.UT, initialize=0)
        self.fw_fac_prod = Param(self.U_PP, initialize=0)

        def FWD_1_rule(self, sc):
            return self.FWD_S[sc] == sum(
                self.FLOW_SOURCE[u_s, sc] * self.fw_fac_source[u_s] * self.flh[u_s]
                for u_s in self.U_S
            )

        def FWD_2_rule(self, sc):
            return self.FWD_C[sc] == sum(
                sum(self.FLOW_IN[u_p, i, sc] for i in self.I)
                * self.flh[u_p]
                * self.fw_fac_prod[u_p]
                for u_p in self.U_PP
            )

        def FWD_3_rule(self,sc):
            return self.FWD_UT1[sc] == sum(
                self.ENERGY_DEMAND_TOT[ut, sc] * self.fw_fac_ut[ut] for ut in self.U_UT
            )

        def FWD_4_rule(self, sc):
            return (
                self.FWD_UT2[sc]
                == (
                    sum(self.ENERGY_DEMAND_HEAT_DEFI[hi, sc] for hi in self.HI)
                    - self.ENERGY_DEMAND_HEAT_PROD_SELL[sc] * 0.7
                )
                * self.H
                * self.fw_fac_ut["Heat"]
            )

        def FWD_5_rule(self, sc):
            return self.FWD_TOT[sc] == self.FWD_UT2[sc] + self.FWD_UT1[sc] - self.FWD_S[sc] - self.FWD_C[sc]

        self.FreshWaterEquation1 = Constraint(self.SC, rule=FWD_1_rule)
        self.FreshWaterEquation2 = Constraint(self.SC, rule=FWD_2_rule)
        self.FreshWaterEquation3 = Constraint(self.SC, rule=FWD_3_rule)
        self.FreshWaterEquation4 = Constraint(self.SC, rule=FWD_4_rule)
        self.FreshWaterEquation5 = Constraint(self.SC, rule=FWD_5_rule)

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

            ind = False

            for i, j in self.groups.items():

                if u in j and uu in j:
                    return self.Y[u] == self.Y[uu]
                    ind = True

            if ind == False:
                return Constraint.Skip

        def ProcessGroup_logic_2_rule(self, u, k):

            ind = False

            for i, j in self.connections.items():
                if u == i:
                    if j[k]:
                        return sum(self.Y[uu] for uu in j[k]) >= self.Y[u]
                        ind = True

            if ind == False:
                return Constraint.Skip

        self.ProcessGroup_logic_1 = Constraint(
            self.U, self.UU, rule=ProcessGroup_logic_1_rule
        )

        self.ProcessGroup_logic_2 = Constraint(
            self.U, numbers, rule=ProcessGroup_logic_2_rule
        )


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

        self.ProductLoad = Param()
        self.odds = Param(self.SC)


        # Variables
        # ---------

        self.MainProductFlow = Var(self.SC)

        self.NPC = Var(self.SC)
        self.NPFWD = Var(self.SC)
        self.NPE = Var(self.SC)
        self.EBIT = Var(self.SC)
        self.SumOfProductFlows = Var(self.SC)

        # add the final objective values
        self.NPC_final = Var()
        self.NPFWD_final = Var()
        self.NPE_final = Var()
        self.EBIT_final = Var()

        # Constraints
        # -----------

        # Definition of Main Product and Product Load for NPC / NPE Calculation

        def SumOfProducts_rule(self, sc):
            return self.SumOfProductFlows[sc] == sum(self.FLOW_IN[U_pp, i, sc]
                                             for U_pp in self.U_PP
                                             for i in self.I
                                             ) * self.H

        self.SumOfProducts_Equation = Constraint(self.SC, rule=SumOfProducts_rule)



        def MainProduct_1_rule(self, sc):
            # If the EBIT is chosen as objective function, skip this constraint
            if self.productDriven == "no":
                return Constraint.Skip
            else:
                return (
                    self.MainProductFlow[sc]
                    == sum(self.FLOW_IN[self.main_pool, i, sc] for i in self.I) * self.H
                )
        def MainProduct_2_rule(self, sc):
            if self.productDriven == "no":
                return Constraint.Skip
            else:
                return self.MainProductFlow[sc] == self.ProductLoad

        self.MainProduct_Equation_1 = Constraint(self.SC, rule=MainProduct_1_rule)
        self.MainProduct_Equation_2 = Constraint(self.SC, rule=MainProduct_2_rule)

        # Definition of specific function

        def Specific_NPC_rule(self, sc):# in € per year (euro/ton/year)
            # ProductLoad is 1 is substrate driven, otherwise it is the target production
            return self.NPC[sc] == self.TAC[sc] * 1000 * 1000 / self.ProductLoad # in euro per tonne of product per year (so your target production)


        def Specific_GWP_rule(self, sc):
            return self.NPE[sc] == self.GWP_TOT[sc] / self.ProductLoad
            #return self.NPE == self.GWP_TOT

        def Specific_FWD_rule(self, sc):
            return self.NPFWD[sc] == self.FWD_TOT[sc] / self.ProductLoad
            #return self.NPFWD == self.FWD_TOT

        def Specific_EBIT_rule(self, sc):
            return self.EBIT[sc] == (self.PROFITS_TOT[sc] - self.OPEX[sc] - self.CAPEX)

        self.Specific_NPC_rule = Constraint(self.SC, rule=Specific_NPC_rule)
        self.Specific_GWP_rule = Constraint(self.SC, rule=Specific_GWP_rule)
        self.Specific_FWD_rule = Constraint(self.SC, rule=Specific_FWD_rule)
        self.Specific_EBIT_rule = Constraint(self.SC, rule=Specific_EBIT_rule)

        # Definition of the possible Objective Functions
        def NPC_rule(self):
            return self.NPC_final == ((self.CAPEX + sum(self.odds[sc] * (self.OPEX[sc] - self.PROFITS_TOT[sc])
                                    for sc in self.SC)) * 1000 * 1000) / self.ProductLoad  # in from Mil. euro to Euro

        def GWP_rule(self):
            return self.NPE_final == sum(self.odds[sc] * self.GWP_TOT[sc] / self.ProductLoad for sc in self.SC)
        def FWD_rule(self):
            return self.NPFWD_final == sum(self.odds[sc] * self.FWD_TOT[sc] / self.ProductLoad for sc in self.SC)
        def EBIT_rule(self):
            return self.EBIT_final == (sum(self.odds[sc] * (self.PROFITS_TOT[sc] - self.OPEX[sc]) for sc in self.SC) - self.CAPEX)

        self.NPC_rule = Constraint(rule=NPC_rule)
        self.GWP_rule = Constraint(rule=GWP_rule)
        self.FWD_rule = Constraint(rule=FWD_rule)
        self.EBIT_rule = Constraint(rule=EBIT_rule)

        # set the objective function
        if self.objective_name == "NPC":

            def Objective_rule(self):
                return self.NPC_final

        elif self.objective_name == "NPE":

            def Objective_rule(self):
                return self.NPE_final

        elif self.objective_name == "FWD":

            def Objective_rule(self):
                return self.NPFWD_final

        elif self.objective_name == "EBIT":
                def Objective_rule(self):
                    return self.EBIT_final

        else:
            print("Objective function could not be recognised, \n"
                  "The default objective function is NPC (Net Production Costs) has been selected")
            def Objective_rule(self):
                return self.NPC_final

        if self.objective_name == "EBIT":
            self.Objective = Objective(rule=Objective_rule, sense=maximize)

        else:  # want to minimise the other objective functions
            self.Objective = Objective(rule=Objective_rule, sense=minimize)





