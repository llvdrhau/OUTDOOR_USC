
from src.outdoor.outdoor_core.output_classes.model_output import ModelOutput
import itertools
import matplotlib.pyplot as plt
import seaborn as sns

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


    def plot_scenario_analysis(self, variable, savePath=None):
        """
        Plots the distribution of a parameter over the scenarios.

        :param variable: A parameter such as 'EBIT', 'NPC', 'NPE', 'NPFWD'...
        :param savePath: Path to save the plot image.
        :return: The plot of the distribution of the parameter over the scenarios.
        """
        probabilities = self._data['odds']
        variableData = self._data[variable]

        # Set Seaborn style for better aesthetics
        sns.set_theme(style="whitegrid", palette="muted")

        # Create the plot
        plt.figure(figsize=(10, 6))
        bars = sns.barplot(x=list(probabilities.values()), y=list(variableData.values()))
        plt.xlabel('Scenarios', fontsize=12)
        plt.ylabel(variable, fontsize=12)
        plt.title(f'Distribution of {variable} Over Scenarios', fontsize=14)

        # Optional: Add annotations or other plot enhancements here

        # Save or display the plot
        if savePath:
            plt.savefig(savePath, format='png', dpi=300)  # High-resolution saving for publication
        plt.show()

    import matplotlib.pyplot as plt
    import seaborn as sns

    def plot_scenario_analysis2(self, variable, savePath=None):
        """
        Plots the distribution of a parameter over the scenarios.

        :param variable: A parameter such as 'EBIT', 'NPC', 'NPE', 'NPFWD'...
        :param savePath: Path to save the plot image.
        :return: The plot of the distribution of the parameter over the scenarios.
        """
        scenarios = self._data['SC']
        variableData = self._data[variable]

        # Set Seaborn style for better aesthetics
        sns.set_theme(style="whitegrid")

        # Create the plot
        plt.figure(figsize=(8, 5))
        bars = sns.barplot(x=list(variableData.keys()), y=list(variableData.values()), hue=list(variableData.keys()),
                           palette="viridis", dodge=False)
        #bars.legend_.remove()  # Remove the legend

        # Add value labels on each bar
        for bar in bars.patches:
            bars.annotate(format(bar.get_height(), '.2f'),
                          (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                          ha='center', va='center', size=10,
                          xytext=(0, 8), textcoords='offset points')

        # Set labels and title with increased font size
        plt.xlabel('Scenario', fontsize=14)
        plt.ylabel(variable, fontsize=14)
        plt.title('Distribution of {} Over the Scenarios'.format(variable), fontsize=16)
        plt.xticks(rotation=45)  # Useful if there are many scenarios or long labels

        # Tight layout for neatness
        plt.tight_layout()

        # Show the plot
        plt.show()

        # Save the plot if a path is provided
        if savePath is not None:
            plt.savefig(savePath + '/{}_distribution.png'.format(variable), bbox_inches='tight')

