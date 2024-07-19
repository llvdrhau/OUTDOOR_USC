
from src.outdoor.outdoor_core.output_classes.model_output import ModelOutput
import itertools
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import gaussian_kde
import json
import random as rnd
import datetime
import pickle as pic
import os

class StochasticModelOutput(ModelOutput):
    """
    collect results of the stochastic model
    """
    def __init__(self, model_instance=None, optimization_mode=None, solver_name=None, run_time=None, gap=None):
        super().__init__(model_instance, optimization_mode, solver_name, run_time, gap)
        self.uncertaintyDict = {}
        self.VSS = 0 # Value of the Stochastic Solution
        self.EVPI = 0 # Expected Value of Perfect Information
        self.infeasibleScenarios = []
        self.DefaultScenario = 'sc1' # if no scenario is specified then this is the default scenario
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

        # save the _data in the ModelOutput to a JSON file
        if savePath:
            savePathData = savePath + '/data_file.json'
            rawData = self._data
            with open(savePathData, 'w') as json_file:
                json.dump(rawData, json_file, indent=4)

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


    def plot_scenario_analysis_PDF(self, variable, xlabel= None, savePath=None, saveName=None):
        """
        Plots the probality distribution function of a variable over the scenarios.

        :param variable: A parameter such as 'EBIT', 'NPC', 'NPE', 'NPFWD'...
        :param xlabel: The label of the x-axis.
        :param savePath: Path to save the plot image.
        :return: The plot of the distribution of the parameter over the scenarios.
        """

        VariablePermission = ["ENERGY_DEMAND_TOT", "OPEX", "EBIT", "NPC", "NPE", "NPFWD"]
        EnergyDemandPermission = ["Electricity", "Cooling"]

        # Handling variable input
        if isinstance(variable, dict):
            variableName = variable['Variable']
        else:
            variableName = variable

        # Validate variable
        if variableName not in VariablePermission:
            raise ValueError(f"The variable {variableName} cannot be plotted at the moment. "
                             f"Possible parameters to plot are: {VariablePermission}")

        # Handle ENERGY_DEMAND_TOT
        elif variableName == "ENERGY_DEMAND_TOT":
            UT = variable['UT']
            if UT not in EnergyDemandPermission:
                raise ValueError("Please specify the Utility parameter UT as either 'Electricity' or 'Cooling'")
            variableData = [value for key, value in self._data[variableName].items() if key[0] == UT]
        else:
            variableData = list(self._data[variableName].values())

        if xlabel is None:
            xlabel = variableName

        # get the probabilty data
        probabilities = list(self._data['odds'].values())

        # Set Seaborn style for better aesthetics
        sns.set_theme(style="whitegrid", palette="muted")

        # Estimate the PDF
        kde = gaussian_kde(variableData, weights=probabilities)

        # Create the plot
        plt.figure(figsize=(10, 6))
        sns.kdeplot(x=variableData, weights=probabilities, fill=True, color="skyblue", linewidth=2)

        plt.xlabel(xlabel, fontsize=12)
        plt.title(f'Distribution of {variable} Over Scenarios', fontsize=14)

        # Optional: Add annotations or other plot enhancements here

        # Save or display the plot

        # Save or display the plot
        if savePath:
            if saveName:
                saveLocation = savePath + '/' + saveName + '_PDF_distribution.png'
            else:
                saveLocation = savePath + '/PDF_distribution.png'
            plt.savefig(saveLocation, format='png', dpi=300)  # High-resolution saving for publication
        plt.show()

        return kde # return the estimated PDF


    def calculate_odds_in_range(self, kde, range_start, range_end):
        """
        Calculates the odds of a value falling within the specified range.

        :param kde: The estimated PDF from plot_scenario_analysis_PDF function.
        :param range_start: The start of the range.
        :param range_end: The end of the range.
        :return: The probability of the value falling within the range.
        """
        return kde.integrate_box_1d(range_start, range_end)


    def plot_scenario_analysis_histogram(self, variable, bins=None, xlabel=None, savePath=None, saveName= None):
        """
        Plots the distribution of a parameter over the scenarios as a histogram

        :param variable: A parameter such as 'EBIT', 'NPC', 'NPE', 'NPFWD'...
        :param bins: The number of bins to use in the histogram. If not specified, the square root of the number of scenarios is used.
        :param xlabel: The label of the x-axis.
        :param savePath: Path to save the plot image.
        :return: The plot of the distribution of the parameter over the scenarios.
        """

        if xlabel is None:
            xlabel = variable

        probabilities = self._data['odds']
        variableData = self._data[variable]

        # Determine the number of bins if not specified
        if bins is None:
            bins = int(np.sqrt(len(variableData)))

        # Create bins
        bin_ranges = np.linspace(min(variableData.values()), max(variableData.values()), bins + 1)

        lowerBin = 0
        binLabels = []
        for bn in bin_ranges:
            bn = round(bn, 3)
            binLabels.append("[{},{}]".format(lowerBin, bn))
            lowerBin = bn

        binned_data = np.digitize(list(variableData.values()), bins=bin_ranges)

        # Count occurrences in each bin
        bin_counts = dict((bin_number, 0) for bin_number in range(1, bins + 2))
        for b in binned_data:
            bin_counts[b] += 1

        # Set Seaborn style for better aesthetics
        sns.set_theme(style="whitegrid", palette="muted")

        # Create the plot
        plt.figure(figsize=(10, 6))
        bars = sns.barplot(x=list(bin_counts.keys()), y=list(bin_counts.values()))
        # Set tick labels for x-axis
        bars.set_xticklabels(binLabels, rotation=45, ha="right")
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel("Count", fontsize=12)
        plt.title(f'Distribution of {variable} Over Scenarios (Binned)', fontsize=14)



        # Optional: Add annotations or other plot enhancements here

        # Save or display the plot
        if savePath:
            if saveName:
                saveLocation = savePath + '/' + saveName + '_binned_distribution.png'
            else:
                saveLocation = savePath + '/binned_distribution.png'

            plt.savefig(saveLocation, format='png', dpi=300)  # High-resolution saving for publication
        plt.show()


class StochasticModelOutput_mpi_sppy(ModelOutput):

    def __init__(self, model_instance=None, optimization_mode="2-stage-recourse", solver_name=None, run_time=None, gap=None,
                 mpi_sppy_results=None):
        super().__init__(model_instance, optimization_mode, solver_name, run_time, gap)


        # get the results from the mpi_sppy
        self.solver_name = solver_name
        self.optimization_mode = optimization_mode
        self._run_time = run_time
        self.stochastic_mode = "mpi-sppy"
        self.dataFile = {}
        self._dataStochastic = {}

        # create a case number
        self._case_time = str(datetime.datetime.now())
        self._case_number = self._case_time[0:10] + '--Nr ' + str(rnd.randint(1, 10000))


        if mpi_sppy_results:
            self.fistStageVars = mpi_sppy_results[0]
            self.dataFileVariables = mpi_sppy_results[1]
            self.warningVariables = mpi_sppy_results[2]
            self.ph = mpi_sppy_results[3] # raw results from the ph object in mpi_sppy
            # make the data dictionary from the ph object
            self.get_data()
            # consistency checks
            self.check_warning_variables()
            consistent, value, variable, scenario = self.check_first_stage_variable_consistency()
            if not consistent:
                warningMessage = (f"First stage decision Variable {variable} : {value} is not consistent across scenarios"
                                  f" {scenario} Please check the data and rerun the optimization")
                self.warningMessage = warningMessage
                raise Warning(warningMessage)


    def check_first_stage_variable_consistency(self):
        data_dict = self.fistStageVars
        # Create a dictionary to store the variable values for each variable
        variable_values = {}

        # Iterate over the items in the input dictionary
        for (scenario, variable), value in data_dict.items():
            # If the variable is not already in the variable_values dictionary, add it
            if variable not in variable_values:
                variable_values[variable] = value
            # If the variable is already in the variable_values dictionary, check if the value is the same
            elif variable_values[variable] != value:
                return False, value, variable, scenario

        # If all values are consistent, return True
        return True, None, None, None

    def check_warning_variables(self):
        wanringVariables = self.warningVariables
        for sc, dictSc in wanringVariables.items():
            if dictSc:
                print("----------------------\n"
                      "-----------------------")
                print(f"\033[93mWarning: Some variables were not calculated for scenario {sc}\033[0m")
                print(f"Scenario: {sc} will be deleeted from the data set \n")

    def get_data(self):
        """
        gets the data from the ph object, uses the local_scenarios attribute to get the instance of the scenarios
        use _fill_data to fill the data of that scenario
        """

        for scenario_name, scenario_instance in self.ph.local_scenarios.items():
            if not self.warningVariables[scenario_name]: # if the de warning scenario is epmty then fill the data
                dataScenario = self._fill_data(scenario_instance)
                # todo should I tidy the data or not??????
                # dataScenario = self._tidy_data(dataScenario)
                self._dataStochastic.update({scenario_name: dataScenario})

        self._data = self._dataStochastic # duplicate for the parent class
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
        data = {}
        for i in instance.component_objects():
            if "pyomo.core.base.var.SimpleVar" in str(type(i)):
                data[i.local_name] = i.value
            elif "pyomo.core.base.var.ScalarVar" in str(type(i)):
                data[i.local_name] = i.value
            elif "pyomo.core.base.param.SimpleParam" in str(type(i)):
                data[i.local_name] = i.value
            elif "pyomo.core.base.param.ScalarParam" in str(type(i)):
                data[i.local_name] = i.value
            elif "pyomo.core.base.param.IndexedParam" in str(type(i)):
                data[i.local_name] = i.extract_values()
            elif "pyomo.core.base.var.IndexedVar" in str(type(i)):
                data[i.local_name] = i.extract_values()
            elif "pyomo.core.base.set.SetProduct_OrderedSet" in str(type(i)):
                data[i.local_name] = i.ordered_data()
            elif "pyomo.core.base.sets.SimpleSet" in str(type(i)):
                data[i.local_name] = i.value_list
            elif "pyomo.core.base.sets.ScalarSet" in str(type(i)):
                data[i.local_name] = i.value_list
            elif "pyomo.core.base.set.OrderedScalarSet" in str(type(i)):
                data[i.local_name] = i.ordered_data()
            elif "pyomo.core.base.objective.SimpleObjective" in str(type(i)):
                data["Objective Function"] = i.expr.to_string()
            elif "pyomo.core.base.objective.ScalarObjective" in str(type(i)):
                data["Objective Function"] = i.expr.to_string()
            else:
                continue

        return data

    def calulate_EVPI(self, resultsWaitAndSee):
        """
        Calculate the Expected Value of Perfect Information (EVPI) of the given objective function.

        :param resultsWaitAndSee: a dict with the results of the wait-and-see scenarios.
        :return: The EVPI value.
        """
        # todo get this function up and runnning

        # Get the objective function value for each scenario
        ExpectedValueList = [value for key, value in self._dataStochastic["Objective Function"].items()]
        recourseSolution = sum(ExpectedValueList)/len(ExpectedValueList)

        # Expected value of the objective function under perfect information
        waitAndSeeSolution = resultsWaitAndSee["Objective Function"]

        # Calculate the Expected Value of Perfect Information (EVPI)
        # get the sens of the objective function
        sensOptimisation = self._dataStochastic["Sense"]  # this will be wrong

        if sensOptimisation:
            EVPI = recourseSolution - waitAndSeeSolution
        else:
            EVPI = waitAndSeeSolution - recourseSolution


        return EVPI

    # Save and load ModelOutput --------------------------------------------------------------------
    # in JSON format, not recommended for use-------------------------------------------------------
    # ----------------------------------------------------------------------------------------------

    def save_2_json(self, savePath=None, saveName=None):
        """
        Save the results to a JSON file
        :param savePath: The path to save the JSON file
        """

        # save the _data in the ModelOutput to a JSON file
        if savePath:
            if not saveName:
                savePathData = savePath + '/output_data_file.json'
            else:
                if '.json' not in saveName:
                    saveName = saveName + '.json'
                savePathData = savePath + '/' + saveName

            rawData = self._dataStochastic
            rawData.update({'Solver': self.solver_name,
                            'Optimisation Mode': self.optimization_mode,
                            'Timer': self._run_time,
                            'Stochastic Mode': self.stochastic_mode,
                            'Case Number': self._case_number
                            })

            rawDataCompatible = self.dict_to_json_compatible(rawData)


            with open(savePathData, 'w') as json_file:
                json.dump(rawDataCompatible, json_file, indent=4)

    def load_from_json(self, savedLocation):
        """
        Load the results from a JSON file
        :param savedLocation: The path to the JSON file
        """

        with open(savedLocation, 'r') as json_file:
            data = json.load(json_file)

        # model output data is stored in the object
        self.dataFile = data
        self.solver_name = data['Solver']
        self.optimization_mode = data['Optimisation Mode']
        self._run_time = data['Timer']
        self.stochastic_mode = data['Stochastic Mode']
        self._case_number = data['Case Number']

        # remove the keys, solver, optimisation mode and timer from the data
        data.pop('Solver')
        data.pop('Optimisation Mode')
        data.pop('Timer')
        data.pop('Stochastic Mode')
        data.pop('Case Number')

        # # Deserialize from JSON
        # deserialized_dict = json.loads(json_str)
        # Convert back to original format
        # restored_dict = self.json_compatible_to_dict(data)
        # self._data = restored_dict
        self._data = data

        # initialise the object with the data
        # self.__init__(model_instance=None,
        #               optimization_mode= self.optimization_mode,
        #               solver_name= self.solver_name,
        #               run_time= self._run_time,
        #               gap=None,
        #              mpi_sppy_results=None)

    def dict_to_json_compatible(self, d):
        def convert_keys(obj):
            if isinstance(obj, dict):
                new_dict = {}
                for k, v in obj.items():
                    new_key = str(k) if isinstance(k, tuple) else k
                    new_dict[new_key] = convert_keys(v)
                return new_dict
            elif isinstance(obj, list):
                return [convert_keys(item) for item in obj]
            else:
                return obj

        return convert_keys(d)

    def json_compatible_to_dict(self, d):
        def convert_keys(obj):
            if isinstance(obj, dict):
                new_dict = {}
                for k, v in obj.items():
                    new_key = self.parse_tuple(k) if isinstance(k, str) and k.startswith('(') and k.endswith(')') else k
                    new_dict[new_key] = convert_keys(v)
                return new_dict
            elif isinstance(obj, list):
                return [convert_keys(item) for item in obj]
            else:
                return obj

        return convert_keys(d)

    def parse_tuple(self, s):
        try:
            return tuple(map(int, s.strip("()").split(",")))
        except:
            return s






