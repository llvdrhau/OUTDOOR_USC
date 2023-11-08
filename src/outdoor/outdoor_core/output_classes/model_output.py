#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 12:19:11 2021

@author: philippkenkel


Function list:
    - fill data
    - fill information
    - tidy data
    - save results /print results
    - save data
    - save file
    - return chosen
    - collect results
"""


from tabulate import tabulate
import os
import datetime
import cloudpickle as pic
import random as rnd
import numpy as np
import itertools

class ModelOutput:

    """
    Class description
    ----------------

    This class is the main output class. It includes the case data such as
    used solver, calculation time, metadata etc.
    It also includes methods to
        - fill data into its own structure from the given pyomo model instance
        - Save data as .txt-file
        - Save the output as pickle file
        - Collect main results and display them in the console


    """

    def __init__(self, model_instance=None, optimization_mode = None, solver_name=None, run_time=None, gap = None):
        self._data = {}
        self._solver = None
        self._run_time = None
        self._case_time = None
        self._objective_function = None
        self._product_load = None
        self._optimality_gap = None
        self._case_numner = None
        self._meta_data = dict()

        self._optimization_mode_set = {
            "Sensitivity analysis",
            "Single 2-stage recourse optimization",
            "Single run optimization",
        }

        if optimization_mode in self._optimization_mode_set:
            self._optimization_mode = optimization_mode
        else:
            raise Exception("Optimization mode not supported")



        if model_instance is not None:
            self._fill_data(model_instance)
        if solver_name is not None and run_time is not None:
            self._fill_information(solver_name, run_time, gap)

# -----------------------------------------------------------------------------
# -------------------------Private methods ------------------------------------
# -----------------------------------------------------------------------------

    def _fill_data(self, instance):
        """

        Parameters
        ----------
        instance : SupstructureModel Class objective that is already solved


        Description
        -------
        Goes through all block of the Model object and extracts the data
        (Parameter, Variables, Sets, Objectives) to a Python dictionary
        that is called ProcessDesign._data

        """

        for i in instance.component_objects():


            if "pyomo.core.base.var.SimpleVar" in str(type(i)):

                self._data[i.local_name] = i.value

            elif "pyomo.core.base.var.ScalarVar" in str(type(i)):
                self._data[i.local_name] = i.value

            elif "pyomo.core.base.param.SimpleParam" in str(type(i)):
                self._data[i.local_name] = i.value

            elif "pyomo.core.base.param.ScalarParam" in str(type(i)):

                self._data[i.local_name] = i.value

            elif "pyomo.core.base.param.IndexedParam" in str(type(i)):

                self._data[i.local_name] = i.extract_values()

            elif "pyomo.core.base.var.IndexedVar" in str(type(i)):
                self._data[i.local_name] = i.extract_values()

            elif "pyomo.core.base.set.SetProduct_OrderedSet" in str(type(i)):
                self._data[i.local_name] = i.ordered_data()

            elif "pyomo.core.base.sets.SimpleSet" in str(type(i)):

                self._data[i.local_name] = i.value_list

            elif "pyomo.core.base.sets.ScalarSet" in str(type(i)):

                self._data[i.local_name] = i.value_list

            elif "pyomo.core.base.set.OrderedScalarSet" in str(type(i)):
                self._data[i.local_name] = i.ordered_data()

            elif "pyomo.core.base.objective.SimpleObjective" in str(type(i)):

                self._data["Objective Function"] = i.expr.to_string()

            elif "pyomo.core.base.objective.ScalarObjective" in str(type(i)):

                self._data["Objective Function"] = i.expr.to_string()
            else:
                continue

    def _fill_information(self, solver_name, run_time, gap):
        """
        Parameters
        ----------
        solver_name : String
        run_time : Float

        Description
        -------
        Fills important case data of the ProcessDesign Object:
            Solver name, Run time, Case time, Solved Objective function,
            Yearly Product load

        """
        self._solver = solver_name
        self._run_time = run_time
        self._case_time = datetime.datetime.now()
        self._case_time = str(self._case_time)
        self._objective_function = self._data["Objective Function"]
        self._product_load = self._data["MainProductFlow"]
        self._optimality_gap = gap
        self._case_number = self._case_time[0:10] + '--Nr ' + str(rnd.randint(1,10000))


        self._meta_data['Solver name'] = solver_name
        self._meta_data['Run time'] = run_time
        self._meta_data['Optimality gap'] = gap
        self._meta_data['Objective function'] = self._data['Objective Function']
        self._meta_data['Case identifier'] = str(self._case_number)


    def _tidy_data(self):
        """
        Description
        -----------
        Runs through data file and clears all zero values which are not important
        to save memory space.

        """

        temp = dict()
        exeptions = ["Y", "Y_DIST", "lin_CAPEX_z", "Y_HEX"]
        for i, j in self._data.items():
            if "index" not in i:
                if type(j) == dict:
                    temp[i] = dict()
                    for k, m in j.items():
                        if i not in exeptions:
                            if m != 0:
                                temp[i][k] = m
                        else:
                            temp[i][k] = m
                else:
                    temp[i] = j
        self._data = temp

    # Extracting methods to get important results

    def _collect_basic_results(self):
        """
        Description
        ----------
        Calls all collector methods to fill ProcessResults.results dictionary
        with all important results

        Returns
        -------
        TYPE: results dictionary
        """

        model_results = dict()

        basic_results = dict()

        basic_results["Basic results"] = {}
        basic_results["units"] = {}

        basic_results["Basic results"]["Objective Function"] = self._objective_function
        basic_results["units"]["Objective Function"] = 'aa'

        basic_results["Basic results"]["Yearly product load"] = self._product_load

        basic_results["Basic results"]["Solver run time"] = '{} seconds'.format(round(self._run_time,2))

        basic_results["Basic results"]["Solver name"] = self._solver

        basic_results["Basic results"]["Earnings Before Tax income"] = "{} Mil. Euro".format(round(self._data["EBIT"], 3))

        if self._product_load:
            basic_results["Basic results"]["Net production costs"] = "{} euro/ton".format(round(self._data["NPC"], 2))
        else:
            basic_results["Basic results"]["Net production costs"] = "{} euro/ton".format(round(self._data["NPC"]/ self._data['SumOfProductFlows'], 2))


        if self._product_load:
            basic_results["Basic results"]["Net production GHG emissions"] = "{} CO2-eq/ton".format(round(self._data["NPE"], 2))
        else:
            basic_results["Basic results"]["Net production GHG emissions"] = "{} CO2-eq/ton".format(round(self._data["NPE"] / self._data['SumOfProductFlows'], 2))


        if self._product_load:
            basic_results["Basic results"]["Net present FWD"] = "{} H2O-eq/ton".format(round(self._data["NPFWD"], 2))
        else:
            basic_results["Basic results"]["Net production FWD"] = "{} H2O-eq/ton".format(round(self._data["NPFWD"]/ self._data['SumOfProductFlows'], 2))

        model_results.update(basic_results)

        chosen_technologies = {"Chosen technologies": self.return_chosen()}
        model_results.update(chosen_technologies)

        return model_results

    def _collect_capitalcost_shares(self):
        """
        Decription
        ----------
        Collects data from the ProcessResults._data dictionary.
        Data that is collected are the shares (in %) of different unit-operations
        in the total annual capital investment. Data is returned as dictionary

        Returns
        -------
        capitalcost_shares : Dictionary

        """
        model_data = self._data

        capitalcost_shares = {"Capital costs shares": {}}

        total_costs = model_data["CAPEX"]

        capitalcost_shares["Capital costs shares"]["Heat pump"] = round(
            model_data.get("ACC_HP", 0) / total_costs * 100, 2
        )

        for i, j in model_data["ACC"].items():
            if j >= 1e-3:
                index_name = model_data["Names"][i]
                capitalcost_shares["Capital costs shares"][index_name] = round(
                    (j + model_data.get("TO_CAPEX", 0).get(i, 0)) / total_costs * 100, 2
                )

        return capitalcost_shares

    def _collect_economic_results(self):
        """
        Description
        -----------
        Collects data from the ProcessResults._data dictionary.
        Data that is collected are base economic values, and depict the shares
        of the total costs of:
            CAPEX (all unit-operations)
            Raw material purchase
            Electricity costs
            Chilling costs
            Heat integration costs (Heating, Cooling utilities as well as HEN)
            Operating and Maintenance
            Waste water treatment
            Profits from Byproducts

        Returns
        -------
        economic_results : Dictionary

        """

        model_data = self._data

        economic_results = {"Economic results": {}}

        total_costs = model_data["TAC"] / 1000

        profits = 0
        wwt = 0

        for i, j in model_data["PROFITS"].items():
            if j < 0:
                wwt -= j * model_data["H"] / 1000
            else:
                profits -= j * model_data["H"] / 1000

        economic_results["Economic results"]["CAPEX share"] = round(
            model_data.get("CAPEX", 0) / total_costs * 100, 2
        )

        economic_results["Economic results"]["Raw material consumption share"] = round(
            model_data.get("RM_COST_TOT", 0) / 1000 / total_costs * 100, 2
        )

        economic_results["Economic results"]["Operating and Maintanence share"] = round(
            model_data.get("M_COST_TOT", 0) / total_costs * 100, 2
        )

        economic_results["Economic results"]["Electricity share"] = round(
            (
                model_data.get("ENERGY_COST", 0).get("Electricity", 0)
                + model_data.get("ELCOST", 0)
            )
            / 1000
            / total_costs
            * 100,
            2,
        )

        economic_results["Economic results"]["Chilling share"] = round(
            model_data.get("ENERGY_COST", 0).get("Chilling", 0)
            / 1000
            / total_costs
            * 100,
            2,
        )

        economic_results["Economic results"]["Heat integration share"] = round(
            model_data.get("C_TOT", 0) / 1000 / total_costs * 100, 2
        )

        economic_results["Economic results"]["Waste treatment share"] = round(
            wwt / total_costs * 100, 2
        )

        economic_results["Economic results"]["Profits share"] = round(
            profits / total_costs * 100, 2
        )

        return economic_results

    def _collect_electricity_shares(self):
        """
        Description
        -----------
        Collects data from the ProcessResults._data dictionary.
        Data that is collected are the shares (in %) of different unit-operations
        in the total electricity demand.

        Returns
        -------
        electricity_shares : Dictionary


        """
        model_data = self._data

        electricity_shares = {"Electricity demand shares": {}}

        total_el = model_data.get("ENERGY_DEMAND_HP_EL", 0) * model_data["H"]

        for i, j in model_data["ENERGY_DEMAND"].items():
            if i[1] == "Electricity" and j >= 1e-05:
                total_el += j * model_data.get("flh", 0).get(i[0], 0)

        electricity_shares["Electricity demand shares"][
            "Heatpump electricity share"
        ] = round(
            model_data.get("ENERGY_DEMAND_HP_EL", 0) * model_data["H"] / total_el * 100,
            2,
        )

        for i, j in model_data["ENERGY_DEMAND"].items():
            if i[1] == "Electricity" and j >= 1e-05:
                index_name = model_data["Names"][i[0]]
                electricity_shares["Electricity demand shares"][index_name] = round(
                    j * model_data.get("flh", 0).get(i[0], 0) / total_el * 100, 2
                )

        return electricity_shares

    def _collect_heatintegration_results(self):
        """
        Description
        -----------

        Collects data from the ProcessResults._data dictionary.
        Data that is collected are basic heat integration data:
            Total heating / cooling demand (in MW)
            Total heat recovery (from unit-operations) (in MW)
            Total High pressure steam production, internal (in MW)
            Total internal usage of this HP steam (rest is sold to market)
            Total Heat supplied by High Temperature heat pump (in MW)
            Net heating and cooling demand (in MW)

        Returns
        -------
        heatintegration_results : Dictionary


        """
        model_data = self._data

        heatintegration_results = {"Heating and cooling": {}}

        total_heating = 0
        total_cooling = 0
        net_heating = 0
        steam = 0

        for i in model_data["ENERGY_DEMAND_HEAT_UNIT"].values():
            if i >= 1e-05:
                total_heating += i

        for i in model_data["ENERGY_DEMAND_COOL_UNIT"].values():
            if i >= 1e-05:
                total_cooling += i

        for i in model_data["ENERGY_DEMAND_HEAT_PROD"].values():
            if i >= 1e-05:
                steam += i

        for i in model_data["ENERGY_DEMAND_HEAT_DEFI"].values():
            if i >= 1e-05:
                net_heating += i

        heatintegration_results["Heating and cooling"]["Total heating demand"] = round(
            total_heating, 2
        )

        heatintegration_results["Heating and cooling"]["Total cooling demand"] = round(
            total_cooling, 2
        )

        heatintegration_results["Heating and cooling"]["Total heat recovery"] = round(
            model_data["EXCHANGE_TOT"], 2
        )

        heatintegration_results["Heating and cooling"]["HP Steam produced"] = round(
            steam, 2
        )

        heatintegration_results["Heating and cooling"][
            "Internally used HP Steam"
        ] = round(model_data.get("ENERGY_DEMAND_HEAT_PROD_USE", 0), 2)

        heatintegration_results["Heating and cooling"][
            "High temperature heat pump heat supply"
        ] = round(model_data.get("ENERGY_DEMAND_HP_USE", 0), 2)

        heatintegration_results["Heating and cooling"]["Net heating demand"] = round(
            net_heating, 2
        )

        heatintegration_results["Heating and cooling"]["Net cooling demand"] = round(
            model_data.get("ENERGY_DEMAND_COOLING", 0), 2
        )

        return heatintegration_results

    def _collect_GHG_results(self):
        """
        Description
        -----------
        Collects data from the ProcessResults._data dictionary.
        Data that is collected are the annual GHG emissions from:
            Direct emissions in unit-operations (sum in t/y)
            Indirect emissions from Electricity and Chilling (sum in t/y)
            Indirect emissions from Heat (sum in t/y)
            Emissions from building the plant (t/y)
            Emissions from buying raw materials / Negative emissions
                from carbon capture (t/y)
            Avoided burden credits from byproduct selling (t/y)

        Returns
        -------
        GHG_results : Dictionary

        """
        model_data = self._data

        GHG_results = {"Green house gas emission shares": {}}

        ghg_d = 0
        ghg_b = 0
        ghg_ab = 0

        for i in model_data["GWP_U"].values():
            if i is not None and i >= 1e-05:
                ghg_d += i

        for i in model_data["GWP_UNITS"].values():
            if i is not None and i >= 1e-05:
                ghg_b += i

        for i in model_data["GWP_CREDITS"].values():
            if i is not None and i >= 1e-05:
                ghg_ab += i

        GHG_results["Green house gas emission shares"]["Direct emissions"] = round(
            ghg_d, 0
        )

        GHG_results["Green house gas emission shares"]["Electricity"] = round(
            model_data.get("GWP_UT", 0).get("Electricity", 0), 0
        )

        GHG_results["Green house gas emission shares"]["Heat"] = round(
            model_data.get("GWP_UT", 0).get("Heat", 0), 0
        )

        GHG_results["Green house gas emission shares"]["Chilling"] = round(
            model_data.get("GWP_UT", 0).get("Chilling", 0), 0
        )

        GHG_results["Green house gas emission shares"][
            "Plant building emissions"
        ] = round(ghg_b, 0)

        GHG_results["Green house gas emission shares"][
            "Raw Materials / Carbon Capture"
        ] = round(-model_data["GWP_CAPTURE"], 0)

        GHG_results["Green house gas emission shares"][
            "Avoided burden for byproducts"
        ] = round(-ghg_ab, 0)

        return GHG_results

    def _collect_FWD_results(self):
        """
        Description
        -----------
        Collects data from the ProcessResults._data dictionary.
        Data that is collected are the annual fresh water demand from:
            Indirect demand from Electricity and Chilling (sum in t/y)
            Indirect demand from Heat (sum in t/y)
            Demand from buying raw materials
            Avoided burden credits from byproduct selling (t/y)

        Returns
        -------
        FWD_results: Dictionary
        """

        model_data = self._data

        FWD_results = {"Fresh water demand shares": {}}

        FWD_results["Fresh water demand shares"][
            "Indirect demand from raw materials"
        ] = round(-model_data.get("FWD_S", 0), 0)

        FWD_results["Fresh water demand shares"][
            "Utilities (Electricity and chilling)"
        ] = round(model_data.get("FWD_UT1", 0), 0)

        FWD_results["Fresh water demand shares"]["Utilities (Heating)"] = round(
            model_data.get("FWD_UT2", 0), 0
        )

        FWD_results["Fresh water demand shares"][
            "Avoided burden from byproducds"
        ] = round(-model_data.get("FWD_C", 0), 0)

        return FWD_results

    def _collect_energy_data(self):

        model_data = self._data

        energy_data = {"Energy data": {}}

        heat_demand = model_data["ENERGY_DEMAND_HEAT_UNIT"]
        cool_demand = model_data["ENERGY_DEMAND_COOL_UNIT"]

        total_el = model_data.get("ENERGY_DEMAND_HP_EL", 0) * model_data["H"]

        for i, j in model_data["ENERGY_DEMAND"].items():
            if i[1] == "Electricity" and abs(j) >= 1e-05:
                total_el += j * model_data.get("flh", 0).get(i[0], 0)

        energy_data["Energy data"]["heat"] = heat_demand
        energy_data["Energy data"]["cooling"] = cool_demand
        energy_data["Energy data"]["electricity"] = total_el

        return energy_data

    def _collect_mass_flows(self):

        model_data = self._data
        mass_flow_data = {"Mass flows": {}}

        for i, j in model_data["FLOW_FT"].items():
            if j > 1e-04:
                mass_flow_data["Mass flows"][i] = round(j, 2)

        for i, j in model_data["FLOW_ADD"].items():
            if j > 1e-04:
                mass_flow_data["Mass flows"][i] = round(j, 2)

        return mass_flow_data

    def _collect_techno_economic_results(self):
        self.results = dict()

        model_data = self.model_output._data

        base_data = self.model_output._collect_results()

        self.results.update(base_data)
        chosen_technologies = {"Chosen technologies": self.model_output.return_chosen()}
        self.results.update(chosen_technologies)

        self.results.update(self._collect_economic_results(model_data))
        self.results.update(self._collect_capitalcost_shares(model_data))
        self.results.update(self._collect_electricity_shares(model_data))
        self.results.update(self._collect_heatintegration_results(model_data))
        self.results.update(self._collect_energy_data(model_data))

        return self.results

    def _collect_environmental_data(self):

        self.results = dict()
        model_data = self.model_output._data
        self.results.update(self._collect_GHG_results(model_data))
        self.results.update(self._collect_FWD_results(model_data))

        return self.results

    def _collect_results(self):
        """
        Description
        ----------
        Calls all collector methods to fill ProcessResults.results dictionary
        with all important results

        Returns
        -------
        TYPE: results dictionary


        """

        self.results = {}

        self.results.update(self._collect_basic_results())

        chosen_technologies = {'Chosen technologies': self.return_chosen()}
        self.results.update(chosen_technologies)

        self.results.update(self._collect_economic_results())
        self.results.update(self._collect_capitalcost_shares())
        self.results.update(self._collect_electricity_shares())
        self.results.update(self._collect_heatintegration_results())
        self.results.update(self._collect_GHG_results())
        self.results.update(self._collect_FWD_results())
        self.results.update(self._collect_energy_data())
        self.results.update(self._collect_mass_flows())

    def _save_results(self, model_results, path):
        """
        Parameters
        ----------
        path : String type of where to save the results as .txt file

        Decription
        -------
        Collects all important results from the ProcessResults Class object and
        saves the data as tables in a text file.

        """
        all_results = model_results

        if not os.path.exists(path):
            os.makedirs(path)

        path = path + "/results" + self._case_number + ".txt"


        with open(path, encoding="utf-8", mode="w") as f:

            for i, j in all_results.items():
                table = tabulate(j.items())

                f.write("\n")
                f.write(i)
                f.write("-------- \n")
                f.write(table)
                f.write("\n")
                f.write("\n \n")

            print("")

    def _print_results(self, model_data):
        """
        Description
        -------
        Collects all important results data and prints them as tables to the
        console.

        """

        all_results = model_data

        for i, j in all_results.items():
            print("")
            print("")
            print(i)
            print("--------------")
            print(tabulate(j.items()))
            print("")

# -----------------------------------------------------------------------------
# -------------------------Public methods -------------------------------------
# -----------------------------------------------------------------------------

    def get_results(self, pprint=True, savePath=None):
        """

        Parameters
        ----------
        pprint : Boolean, optional, default is True
            DESCRIPTION: Defines if results should be printed to console
        save : String, optional
            DESCRIPTION: Defines path where results should be saved, if kept
            blank results are not saved as .txt-file.

        Description
        -----------
        Collects the most important model results
        by calling private function '_collect_results'.
        Afterwards optionally prints them and saves them.

        """
        self._collect_results()
        model_results = self.results

        if pprint is True:
            self._print_results(model_results)

        if savePath is not None:
            self._save_results(model_results, savePath)

    def save_data(self, path):
        """
        Parameters
        ----------
        path : String type of where to save the complete data as .txt file


        Decription
        -------
        Collects all data from the ProcessResults Class object and saves the
        data as tables in a text file.

        """

        if not os.path.exists(path):
            os.makedirs(path)

        path = path + "/" + "input_file " + self._case_number + "_data.txt"

        with open(path, encoding="utf-8", mode="w") as f:

            for i, j in self._data.items():
                f.write(f"{i}: {j} \n \n")

    def save_file(self, path, option="raw"):
        """
        Parameters
        ----------
        path : String type of where to save the ProcessResults object as pickle
            class object.
        option: String, default is 'raw' which saves all data also including zero
            values. If this value is set to 'tidy' an cleaning algorithm deletes
            zero values which saves data space.

        Description
        ----------
        Saves the output file as a pickle-file, which can be laoded into an
        Analyzer-Object on another machine or at a different time.

        """
        if option == "tidy":
            self._tidy_data()

        path = path + "/" + "data_file " + self._case_number + ".pkl"

        with open(path, "wb") as output:
            pic.dump(self, output)

    def return_chosen(self):
        """
        Returns
        -------
        chosen : Dictionary

        Description
        -----------
        Checks in the data structure which unit-operations are chosen based on
        binary variables and minimal mass flows. Afterwards saves the results
        and returns a dictionary with the chosen index numbers and defined names.

        """
        flow = self._data["FLOW_SUM"]
        flow_s = self._data["FLOW_SOURCE"]

        # if the key of flow is a tuple then the solution id from the stochastic model
        # Extract the maximum value of the flows for each scenario
        if isinstance(list(flow.keys())[0], tuple):
            flow = self.find_max_value_of_scenarios(dict=flow, unitNr=self._data['U'])
            flow_s = self.find_max_value_of_scenarios(dict=flow_s, unitNr=self._data['U_S'])


        y = self._data["Y"]
        names = self._data["Names"]
        chosen = {}

        for i, j in y.items():
            if j == 1:
                try:
                    if flow[i] >= 0.001:
                        chosen[i] = names[i]
                except:
                    pass

            else:
                try:
                    if flow_s[i] >= 0.001:
                        chosen[i] = names[i]
                except:
                    pass

        return chosen

    def find_max_value_of_scenarios(self, dict, unitNr =None):
        """"
        if the data is encased in a tuple (unitNr, ScenarioNr) then this function splits the data into a dictionary that
        contains the maximum value of each unitNr across all scenarios
        """
        scenario_values = self._data['SC']

        if unitNr is  None:
            units = self._data['U']
        else:
            units = unitNr

        unitDict = {}
        for u in units:
            scList = []
            for s in scenario_values:
                scList.append(dict[u, s])
            unitDict[u] = max(scList)
        return unitDict
class StochasticModelOutput(ModelOutput):
    """
    collect results of the stochastic model
    """
    def __init__(self, model_instance=None, optimization_mode=None, solver_name=None, run_time=None, gap=None):
        super().__init__(model_instance, optimization_mode, solver_name, run_time, gap)
        self.uncertaintyDict = {}
        self.VSS = 0 # value of stochastic solution
        self.EVPI = 0 # expected value of perfect information
        self.infeasibleScenarios = []
        self.DefaultScenario = 'sc1' # if no scenario is specified then this is the default scenario to caluclate the max CAPEX
        # this should get the data using the parent class from the model instance
        # self._data = model_instance._data

    def get_results(self, pprint=True, savePath=None):
        """

        Parameters
        ----------
        pprint : Boolean, optional, default is True
            DESCRIPTION: Defines if results should be printed to console
        save : String, optional
            DESCRIPTION: Defines path where results should be saved, if kept
            blank results are not saved as .txt-file.

        Description
        -----------
        Collects the most important model results
        by calling private function '_collect_results'.
        Afterwards optionally prints them and saves them.

        """

        self._collect_results()
        model_results = self.results

        if pprint is True:
            self._print_results(model_results)

        if savePath is not None:
            self._save_results(model_results, savePath)

    def _collect_results(self):
        """
        Description
        ----------
        Calls all collector methods to fill ProcessResults.results dictionary
        with all important results

        Returns
        -------
        TYPE: results dictionary
        """

        self.results = {}

        self.results.update(self._collect_basic_results())

        chosen_technologies = {'Chosen technologies': self.return_chosen()}
        self.results.update(chosen_technologies)

        self.results.update(self._collect_scenario_data())

        # self.results.update(self._collect_economic_results())
        # self.results.update(self._collect_capitalcost_shares())
        # self.results.update(self._collect_mass_flows())

        # self.results.update(self._collect_electricity_shares())
        # self.results.update(self._collect_heatintegration_results())
        # self.results.update(self._collect_GHG_results())
        # self.results.update(self._collect_FWD_results())
        # self.results.update(self._collect_energy_data())
    def _collect_basic_results(self):
        """
        Description
        ----------
        Calls all collector methods to fill ProcessResults.results dictionary
        with all important results

        Returns
        -------
        TYPE: results dictionary
        """

        model_results = dict()

        basic_results = dict()

        basic_results["Basic results"] = {}

        objectiveFunctionName = self._objective_function
        if objectiveFunctionName == 'EBIT_final':
            unitsObjecive = 'Mil Euros'
        elif objectiveFunctionName == 'NPC_final':
            unitsObjecive = 'Euros'
        elif objectiveFunctionName == 'NPE_final':
            unitsObjecive = 'CO2-eq'
        elif objectiveFunctionName == 'NPFWD_final':
            unitsObjecive = 'H2O-eq'
        else:
            unitsObjecive = 'Unknown'

        basic_results["Basic results"]["Objective Function"] = self._objective_function
        valueObjectiveFunction = round(self._data[self._objective_function], 2)
        basic_results["Basic results"]["Expected Objective value"] = "{} {}".format(valueObjectiveFunction, unitsObjecive)
        defaultScenario = self.DefaultScenario

        if self._product_load[defaultScenario]:
            # the product load is not a variable that changes per scenario
            # so take the first result in the dictionary
            basic_results["Basic results"]["Yearly product load"] = self._product_load[defaultScenario]
        else:
            avgProductLoad = round(sum(self._data['SumOfProductFlows'].values()) / len(self._data['SumOfProductFlows'].values()), 2)
            basic_results["Basic results"]["Average Yearly product load"] = "{} tons".format(avgProductLoad)



        # retrive the VSS and EVPI
        basic_results["Basic results"]["VSS"] = "{} {}".format(round(self.VSS, 2), unitsObjecive )
        basic_results["Basic results"]["EVPI"] = "{} {}".format(round(self.EVPI, 2), unitsObjecive)


        basic_results["Basic results"]["Solver run time"] = "{} s".format(round(self._run_time,2)) # in seconds
        basic_results["Basic results"]["Solver name"] = self._solver

        # get the min, max and mean of the EBIT
        basic_results["Basic results"]["Earnings Before Tax income"] = {}
        minEBIT = round(min(self._data["EBIT"].values()), 2)
        meanEBIT = round(sum(self._data["EBIT"].values()) / len(self._data["EBIT"].values()), 2)
        maxEBIT = round(max(self._data["EBIT"].values()), 2)
        basic_results["Basic results"]["Earnings Before Tax income"] = "Min:{} Mean:{} Max:{} Mil Euros".format(minEBIT, meanEBIT, maxEBIT)


        # get the min, max and mean of the Net production costs
        basic_results["Basic results"]["Net production costs"] = {}
        if self._product_load[defaultScenario]: # if the product load is not zero
            #get the min, max and mean of the NPC
            minNPC = round(min(self._data["NPC"].values()), 2)
            meanNPC = round(sum(self._data["NPC"].values()) / len(self._data["NPC"].values()), 2)
            maxNPC = round(max(self._data["NPC"].values()), 2)
            basic_results["Basic results"]["Net production costs"] = "Min:{} Mean:{} Max:{} Euros/Ton".format(minNPC, meanNPC, maxNPC)

        else: # dived by the sum of the product flows
            # Convert the values of both dictionaries to lists
            npc_values = list(self._data["NPC"].values())
            product_flows_values = list(self._data['SumOfProductFlows'].values())
            npcList = [npc / product_flow for npc, product_flow in zip(npc_values, product_flows_values)]

            minNCP = round(min(npcList), 2)
            meanNCP = round(sum(npcList)/len(npcList), 2)
            maxNCP = round(max(npcList), 2)
            basic_results["Basic results"]["Net production costs"] = "Min:{} Mean:{} Max:{} Euros/Ton".format(minNCP, meanNCP, maxNCP)


        # get the min, max and mean of the NPE
        basic_results["Basic results"]["Net production GHG emissions"] = {}
        if self._product_load[defaultScenario]: # if the product load is not zero
            minNPE = round(min(self._data["NPE"].values()), 2)
            meanNPE = round(sum(self._data["NPE"].values()) / len(self._data["NPE"].values()), 2)
            maxNPE = round(max(self._data["NPE"].values()), 2)
            basic_results["Basic results"]["Net production GHG emissions"] = "Min:{} Mean:{} Max:{} CO2-eq/Ton".format(minNPE, meanNPE, maxNPE)


        else: # dived by the sum of the product flows
            # Convert the values of both dictionaries to lists
            npe_values = list(self._data["NPE"].values())
            product_flows_values = list(self._data['SumOfProductFlows'].values())
            npeList = [npe / product_flow for npe, product_flow in zip(npe_values, product_flows_values)]

            minNPE = round(min(npeList), 2)
            meanNPE = round(sum(npeList)/len(npeList), 2)
            maxNPE = round(max(npeList), 2)
            basic_results["Basic results"]["Net production GHG emissions"] = "Min:{} Mean:{} Max:{} CO2-eq/Ton".format(minNPE, meanNPE, maxNPE)


        #get the min, max and mean of the NPFWD
        basic_results["Basic results"]["Net present FWD"] = {}
        if self._product_load[defaultScenario]: # if the product load is not zero
            minFWD = round(min(self._data["NPFWD"].values()), 3)
            meanFWD = round(sum(self._data["NPFWD"].values()) / len(self._data["NPFWD"].values()), 3)
            maxFWD = round(max(self._data["NPFWD"].values()), 3)
            basic_results["Basic results"]["Net present FWD"] = "Min:{} Mean:{} Max:{} H2O-eq/Ton".format(minFWD, meanFWD, maxFWD)
        else:
            # Convert the values of both dictionaries to lists
            npfwd_values = list(self._data["NPFWD"].values())
            product_flows_values = list(self._data['SumOfProductFlows'].values())
            npfwdList = [npfwd / product_flow for npfwd, product_flow in zip(npfwd_values, product_flows_values)]

            minFWD  = round(min(npfwdList), 3)
            meanFWD = round(sum(npfwdList)/len(npfwdList), 3)
            maxFWD = round(max(npfwdList), 3)
            basic_results["Basic results"]["Net present FWD"] = "Min:{} Mean:{} Max:{} H2O-eq/Ton".format(minFWD, meanFWD, maxFWD)



        model_results.update(basic_results)

        # chosen_technologies = {"Chosen technologies": self.return_chosen()}
        # model_results.update(chosen_technologies)

        return model_results

    def _collect_scenario_data(self, uncertainParameterList=None):
        """
        Discription: Collects the scenario data from the model and checks which scenarios are fesaible and returns the
        bounds of the feasible paramerter space """


        scenario_results = dict()
        scenario_results["Scenario Analysis"] = {}
        nScenarios = len(self._data['SC'])
        nInitialScenarios = nScenarios + len(self.infeasibleScenarios)
        percentFeasible = round(nScenarios/nInitialScenarios * 100, 2)

        scenario_results["Scenario Analysis"]["Total Inital Scenarios"] = nInitialScenarios
        scenario_results["Scenario Analysis"]["Percent Feasible"] = "{} {}".format(percentFeasible, '%')

        uncertaintyDict = self.uncertaintyDict  # get the uncertainty dictionary

        if uncertainParameterList is None:
            uncertainParameterList = ['phi', 'myu', 'xi', 'materialcosts', 'ProductPrice', 'gamma', 'theta']


        for parameter in uncertainParameterList:
            pointerStart = 0
            pointerEnd = nScenarios
            paramDict = self._data[parameter]
            steps = int(len(paramDict) / nScenarios)
            keysUncertainParams = uncertaintyDict[parameter].keys()
            keysUncertainParams = self.upack_tuples(keysUncertainParams)
            for _ in range(0, steps):

                selectionDict = itertools.islice(paramDict.items(), pointerStart, pointerEnd)
                # the parameters per scenario are grouped together in the data structure,
                # hence the pointer is moved up to get the appropriate data
                pointerStart += nScenarios
                pointerEnd += nScenarios

                selectionList = list(selectionDict)
                # parameterName = list(selectionDict.keys())[0]
                minParam = min(selectionList,
                               key=lambda x: x[1])  # the second element of the tuple is the value we want to compare
                maxParam = max(selectionList, key=lambda x: x[1])
                specificParameter = minParam[0][:-1]  # remove the scenario number from the key

                if minParam[1] != maxParam[1]:  # is a tuple with key and value
                    specificParameter = minParam[0][:-1]  # remove the scenario number from the key
                    scenario_results["Scenario Analysis"]["{}: {}".format(parameter, specificParameter)] = (
                        "min:{} max:{}".format(round(minParam[1], 3), round(maxParam[1], 3)))

                # the min max are the same but the parameter is uncertain but still constant because
                # other scenarios are infeasible
                elif specificParameter in keysUncertainParams:
                    scenario_results["Scenario Analysis"]["{}: {}".format(parameter, specificParameter)] = (
                        "min:{} max:{}".format(round(minParam[1], 3), round(maxParam[1], 3)))
                else:
                    pass

        return scenario_results

    def upack_tuples(self, tupleKeys):
        """"
        unpacks the tuples in a list, this is the case for theta parameter where the keys are a nested tuples but the
        output is a smooth list of tuples
        """
        if tupleKeys: # make sure the list is not empty
            # now a list of keys from a dict transform to a list of tuples
            tupleList = list(tupleKeys)
            tuple1 = tupleList[0]
            if isinstance(tuple1, tuple):

                nestedTuple = any(isinstance(element, tuple) for element in tuple1)

                if nestedTuple:
                    unpackedList = []
                    for tup in tupleList:
                        unpackedTuple = tuple(element for sub in tup for element in (sub if isinstance(sub, tuple) else (sub,)))
                        unpackedList.append(unpackedTuple)
                    return unpackedList

                else:
                    return tupleKeys
            else:
                return tupleKeys
        else:
            return tupleKeys







