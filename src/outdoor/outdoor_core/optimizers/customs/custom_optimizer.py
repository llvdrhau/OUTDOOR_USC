#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 12:19:19 2021

@author: philippkenkel and Lucas Van der Hauwaert
"""


from .change_objective import change_objective_function
from ...output_classes.multi_model_output import MultiModelOutput
from ...model.optimization_model import SuperstructureModel
from ...output_classes.stochastic_model_output import StochasticModelOutput_mpi_sppy


from ..main_optimizer import SingleOptimizer
from ...utils.timer import time_printer
from ...utils.progress_bar import print_progress_bar

from .change_params import (
    prepare_mutable_parameters,
    calculate_sensitive_parameters,
    change_parameter,
)
import numpy as np
from pyomo.environ import *
import sys
import logging
import copy
from concurrent.futures import ProcessPoolExecutor

import mpisppy.utils.sputils as sputils
from mpisppy.opt.ef import ExtensiveForm
from mpisppy.opt.ph import PH

import pyomo.environ as pyo




class MCDAOptimizer(SingleOptimizer):
    def __init__(self, solver_name, solver_interface, solver_options=None, mcda_data=None):
        super().__init__(solver_name, solver_interface, solver_options)
        self.mcda_data = mcda_data
        self.single_optimizer = SingleOptimizer(solver_name, solver_interface, solver_options)

    def run_optimization(self,
                         model_instance,
                         optimization_mode=None,
                         solver="gurobi",
                         interface="local",
                         solver_path=None,
                         options=None,
                         count_variables_constraints=False
                         ):

        timer = time_printer(programm_step="MCDA optimization")

        model_output = MultiModelOutput(optimization_mode="multi-objective")

        for k, v in self.mcda_data.items():
            change_objective_function(model_instance, k)
            single_solved = self.single_optimizer.run_optimization(model_instance)
            single_solved._tidy_data()
            model_output.add_process(k, single_solved)

        print("MCDA reformulation")
        change_objective_function(model_instance, "MCDA", model_output, self.mcda_data)
        single_solved = self.single_optimizer.run_optimization(model_instance)
        single_solved._tidy_data()
        model_output.add_process("MCDA", single_solved)
        model_output.set_multi_criteria_data(self.mcda_data)

        timer = time_printer(timer, "MCDA optimization")
        model_output.fill_information(timer)
        return model_output


class SensitivityOptimizer(SingleOptimizer):
    def __init__(
        self,
        solver_name,
        solver_interface,
        solver_options=None,
        sensi_data=None,
        superstructure=None,
    ):
        super().__init__(solver_name, solver_interface, solver_options)

        self.sensi_data = sensi_data
        self.superstructure = superstructure

        self.single_optimizer = SingleOptimizer(solver_name, solver_interface, solver_options)

    def run_optimization(self, model_instance,
                         optimization_mode = None,
                         solver = "gurobi",
                         interface = "local",
                         solver_path = None,
                         options = None,
                         count_variables_constraints = False):

        timer1 = time_printer(programm_step="Sensitivity optimization")
        sensi_data_Dict_lists = calculate_sensitive_parameters(self.sensi_data)

        initial_model_instance = model_instance.clone()
        time_printer(passed_time=timer1, programm_step="Create initial ModelInstance copy")
        model_output = MultiModelOutput(optimization_mode="sensitivity")

        superstructureData = self.superstructure


        for parameterName, (value_list, metadata) in sensi_data_Dict_lists.items():
            for val in value_list:
                model_instance = change_parameter(Instance=model_instance,
                                                  parameter=parameterName,
                                                  value=val, metadata=metadata,
                                                  superstructure= superstructureData)

                single_solved = self.single_optimizer.run_optimization(model_instance)

                single_solved._tidy_data()
                model_output.add_process((parameterName, val), single_solved)

            model_instance = initial_model_instance

        model_output.set_sensitivity_data(self.sensi_data)
        timer = time_printer(timer1, "Sensitivity optimization")
        model_output.fill_information(timer)
        return model_output

    def _solve_single_optimisation(self, model_instance, senitivityData):
        """
        This function is used to solve the single optimisation problem for each parameter in the sensitivity analysis
        :param model_instance:
        :param senitivityData:
        :return:

        the idea is to use this function to run parralell computing using follwong code:
         # Using ProcessPoolExecutor to solve models in parallel
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.solve_single_optimisation, model_instance) for data in data_list]
            results = [future.result() for future in futures]

        """
        # parameterName = senitivityData
        # for parameterName, (value_list, metadata) in sensi_data_Dict_lists.items():
        #     for val in value_list:
        #         model_instance = change_parameter(Instance=model_instance,
        #                                           parameter=parameterName,
        #                                           value=val, metadata=metadata,
        #                                           superstructure= superstructureData)
        #
        #         single_solved = self.single_optimizer.run_optimization(model_instance)
        #
        #         single_solved._tidy_data()
        #         model_output.add_process((parameterName, val), single_solved)
        #
        #     model_instance = initial_model_instance
        pass

class TwoWaySensitivityOptimizer(SingleOptimizer):
    def __init__(
        self,
        solver_name,
        solver_interface,
        solver_options=None,
        two_way_data=None,
        superstructure=None,
    ):

        super().__init__(solver_name, solver_interface, solver_options)

        self.cross_parameters = two_way_data
        self.superstructure = superstructure

        self.single_optimizer = SingleOptimizer(
            solver_name, solver_interface, solver_options
        )

    def run_optimization(self,
                         model_instance,
                         optimization_mode=None,
                         solver="gurobi",
                         interface="local",
                         solver_path=None,
                         options=None,
                         count_variables_constraints=False,
                         parralellComputing = False
                         ):

        timer1 = time_printer(programm_step="Two-way sensitivity optimimization")
        self.cross_parameters = calculate_sensitive_parameters(self.cross_parameters)

        model_output = MultiModelOutput(optimization_mode="cross-parameter sensitivity")

        index_names = list()
        dic_1 = dict()
        dic_2 = dict()

        for i in self.cross_parameters.keys():
            index_names.append(i)

        for i, j in self.cross_parameters.items():
            if i == index_names[0]:
                dic_1[i] = j
            elif i == index_names[1]:
                dic_2[i] = j

        paramName1 = list(dic_1.keys())[0]
        paramName2 = list(dic_2.keys())[0]

        parmaValues1 = list(dic_1.values())[0][0]
        paramValues2 = list(dic_2.values())[0][0]

        metadata1 = list(dic_1.values())[0][1]
        metadata2 = list(dic_2.values())[0][1]

        if parralellComputing:
            # todo make parallel computing work
            # Using ProcessPoolExecutor to solve models in parallel
            with ProcessPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self._solve_model_instance,
                                           paramName1, paramName2,
                                           paramVal1, paramVal2,
                                           metadata1, metadata2,
                                           model_instance, model_output)
                           for paramVal1 in parmaValues1 for paramVal2 in paramValues2]

                results = [future.result() for future in futures]
            print(results)
        # model_output.add_process((paramName1, paramVal1, paramName2, paramVal2), single_solved)

        else:
            for i in parmaValues1:
                for j in paramValues2:
                    self._solve_model_instance(paramName1, paramName2,
                                                 i, j,
                                                 metadata1, metadata2,
                                                 model_instance, model_output)



        timer = time_printer(timer1, "Ending Two-way sensitivity Analysis")
        model_output.fill_information(timer)
        return model_output

    def _solve_model_instance(self, paramName1, paramName2,
                              paramVal1, paramVal2,
                              metadata1, metadata2,
                              model_instance, model_output):
        """
        This function is used to solve the model instance for a given parameter set
        :param param1:
        :param param2:
        :param model_instance:
        :param superstructure:
        :return:

        """
        superstructure = self.superstructure

        model_instance = change_parameter(Instance=model_instance,
                                          parameter=paramName1,
                                          value=paramVal1, metadata=metadata1,
                                          superstructure=superstructure,
                                          printTimer=False)

        model_instance = change_parameter(Instance=model_instance,
                                          parameter=paramName2,
                                          value=paramVal2, metadata=metadata2,
                                          superstructure=superstructure,
                                          printTimer=False)

        single_solved = self.single_optimizer.run_optimization(model_instance,
                                                               tee=False,
                                                               keepfiles=True,
                                                               printTimer=False)
        single_solved._tidy_data()
        model_output.add_process((paramName1, paramVal1, paramName2, paramVal2), single_solved)
        return (paramName1, paramVal1, paramName2, paramVal2), single_solved


class StochasticRecourseOptimizer(SingleOptimizer):
    def __init__(
        self,
        solver_name,
        solver_interface,
        input_data,
        solver_options=None,
        single_model_instance=None,
        stochastic_options=None,
        remakeMetadata = None
    ):

        super().__init__(solver_name, solver_interface, solver_options)
        self.single_optimizer = SingleOptimizer(solver_name, solver_interface, solver_options)
        self.input_data = input_data
        self.single_model_instance_4_EVPI = single_model_instance.clone()
        self.single_model_instance_4_VSS = single_model_instance.clone()
        self. remakeMetadata = remakeMetadata
        if stochastic_options is None:
            self.stochastic_options = {
                "calculation_EVPI": False,
                "calculation_VSS": False,
            }
        else:
            self.stochastic_options = stochastic_options

    def run_optimization(self,
                         model_instance,
                         optimization_mode=None,
                         solver="gurobi",
                         interface="local",
                         solver_path=None,
                         options=None,
                         count_variables_constraints=False,

                         ):


        # preallocate the variables
        infeasibleScenarios = None
        waitAndSeeSolution = 0
        average_VSS = 0

        # get the input data and stochastic options
        input_data = self.input_data
        calculation_EVPI = self.stochastic_options["calculation_EVPI"]
        calculation_VSS = self.stochastic_options["calculation_VSS"]

        waitAndSeeSolutionDict = {}
        EEVDict = {}

        # calculate the EVPI and VSS, if not on a rerun (i.e. if the remakeMetadata is not None)
        # ---------------------------------------------------------------------------------------
        if self.remakeMetadata:
            EEVList = self.remakeMetadata["EEVList"]
            waitAndSeeSolutionList = self.remakeMetadata["waitAndSeeSolutionList"]
            infeasibleScenarios = self.remakeMetadata["infeasibleScenarios"]
        else:
            # make a deep copy of the input data so the stochastic parameters can be transformed to final dataformat
            Stochastic_input_EVPI = copy.deepcopy(input_data)
            Stochastic_input_EVPI.create_DataFile()
            Stochastic_input_vss = copy.deepcopy(Stochastic_input_EVPI)

            if calculation_EVPI:
                # timer for the EVPI calculation
                startEVPI = time_printer(programm_step="EPVI calculation")
                # create the Data_File Dictionary in the object input_data

                waitAndSeeSolutionDict, infeasibleScenarios = self.get_WaitAndSee(Stochastic_input_EVPI)
                time_printer(passed_time=startEVPI, programm_step="EPVI calculation")

            if calculation_VSS:
                startVSS = time_printer(programm_step="VSS calculation")
                # calculate the VSS
                EEVDict = self.get_EEV(Stochastic_input_vss)
                time_printer(passed_time=startVSS, programm_step="VSS calculation")

            # ---------------------------------------------------------------------------------------

            # continue with the stochastic optimization
            # if there are infeasible scenarios, we need to remove them from the input data
            if infeasibleScenarios: # if the list is not empty
                print("\033[1;32m" + "unfeasible scenarios detected, removing them from the input data and "
                                     "reconstructing the model" + "\033[0m")

                #model_instance = self.curate_stochastic_model_intance(model_instance, infeasibleScenarios)
                #model_output = ("remake_stochastic_model_instance", infeasibleScenarios)
                # make a dictionary of all the values we need to pass on to the model output, needed for the rerun:
                # infeasibleScenarios, EEVList, waitAndSeeSolutionList
                model_output = {"infeasibleScenarios": infeasibleScenarios,
                                "EEVList": EEVDict,
                                "waitAndSeeSolutionList": waitAndSeeSolutionDict,
                                "Status": "remake_stochastic_model_instance" }
                return model_output


        # run the optimization
        model_output = self.single_optimizer.run_optimization(model_instance=model_instance,
                                                              stochastic_optimisation=True)

        # pass on the uncertainty data to the model output
        model_output.uncertaintyDict = input_data.uncertaintyDict
        #time_printer(solving_time, "Superstructure optimization procedure")

        objectiveName = model_output._objective_function
        expected_value = model_output._data[objectiveName]

        # pass on the EVPI and VSS to the model output

        if calculation_EVPI:
            waitAndSeeSolution = self.calculate_final_EEV_or_WS(model_output._data['odds'], waitAndSeeSolutionDict)
            # Use ANSI escape codes to make the text purple and bold
            print("\033[95m\033[1mThe EVwPI is:", waitAndSeeSolution, "\033[0m")

            # pass on the EVPI
            if model_output._data['objective_sense'] == 1: # 1 if optimisation is maximised 0 if minimized 1
                model_output.EVPI = waitAndSeeSolution - expected_value
            else:
                model_output.EVPI = expected_value - waitAndSeeSolution
            model_output.infeasibleScenarios = infeasibleScenarios

        if calculation_VSS:
            # EEV = self.curate_EEV(EEVList, expected_value)
            EEV = self.calculate_final_EEV_or_WS(model_output._data['odds'], EEVDict)
            # print the EEV
            print("\033[95m\033[1mThe EEV is:", EEV, "\033[0m")
            if model_output._data['objective_sense'] == 1: # 1 if optimisation is maximised 0 if minimized
                model_output.VSS = expected_value - EEV
            else:
                model_output.VSS = EEV - expected_value

        # pass on the default scenario if it changed
        # (extra parameter is data to the input data object in this case)
        if hasattr(input_data, 'DefaultScenario'):
            model_output.DefaultScenario = input_data.DefaultScenario
        else:
            model_output.DefaultScenario = 'sc1'

        # self.debug_EVPI(model_output, Stochastic_input_EVPI, solver, interface, solver_path, options)
        # self.debug_VSS(model_output, Stochastic_input_EVPI, solver, interface, solver_path, options)

        return model_output

    def calculate_final_EEV_or_WS(self, probabilities, metricDict):
        """
        This function calculates the EVPI based on the probabilities of the scenarios
        :param probabilities: Dict of probabilities of each scenario
        :param metricDict: Dict of wait and see solutions or Expected results of Expected values
        :return: metric: the weighted sum of the EVPI or EEV
        """
        metric = 0
        for key, value in probabilities.items():
            prob = value
            i = metricDict[key]
            metric += prob * i
        return metric

    def get_WaitAndSee(self, input_data=None):
        """
        This function is used to calculates the EVPI of a stochastic problem.
        :param input_data: of the signal optimization run
        :param solver:
        :param interface:
        :param solver_path:
        :param options:
        :return: EVPI

        """

        # get data from the object
        #model_instance_EVPI = copy.deepcopy(self.single_model_instance)
        model_instance_EVPI = self.single_model_instance_4_EVPI
        singleInput = self.input_data.parameters_single_optimization
        optimizer = self.single_optimizer

        # the next step is to run individual optimizations for each scenario and save the results in a list
        # first we need to get the scenarios from the input data
        scenarios = input_data.Scenarios['SC']

        # now we need to run the single run optimization for each scenario
        # we need to save the objective values in a list
        WaitAndSeeDict = {}
        objectiveValueList_EVPI = []
        infeasibleScenarios = []
        selectedTechnologies = []

        # Green and bold text
        print("\033[1;32m" + "Calculating the objective values for each scenario to calculate the EVPI\n"
                             "Please be patient, this might take a while" + "\033[0m")

        # Suppress the specific warning if model is infeasible
        logging.getLogger('pyomo.core').setLevel(logging.ERROR)
        total_scenarios = len(scenarios)

        for index, sc in enumerate(scenarios):

            # model for EVPI calculation, the only difference is that the boolean variables are not fixed
            # i.e. all model variables are optimised according to the scenario parameters
            modelInstanceScemarioEVPI = self.set_parameters_of_scenario(scenario=sc, singleInput=singleInput,
                                                               stochasticInput=input_data, model=model_instance_EVPI)

            # run the optimization
            modelOutputScenario_EVPI = optimizer.run_optimization(model_instance=modelInstanceScemarioEVPI, tee=False,
                                                                  keepfiles=False, printTimer=False, VSS_EVPI_mode=True)

            if modelOutputScenario_EVPI == 'infeasible':
                infeasibleScenarios.append(sc)
            else: # save the results
                objectiveName = modelOutputScenario_EVPI._objective_function
                objectiveValueList_EVPI.append(modelOutputScenario_EVPI._data[objectiveName])

                WaitAndSeeDict.update({sc: modelOutputScenario_EVPI._data[objectiveName]})
                chosenTechnology = modelOutputScenario_EVPI.return_chosen()
                selectedTechnologies.append(chosenTechnology)

            # print the progress bar
            print_progress_bar(iteration=index, total=total_scenarios, prefix='EVPI', suffix='')


        # now we have the objective values for each scenario in a list
        # the next step is to calculate the EVPI
        #EVPI = np.mean(objectiveValueList_EVPI)

        # Print a newline character to ensure the next console output is on a new line.
        print()
        # reactivate the warning if model is infeasible
        logging.getLogger('pyomo.core').setLevel(logging.WARNING)
        # count the unique sets of selected technologies
        self.count_unique_sets(selectedTechnologies)

        # make a set of infeasible scenarios to get rid of duplicates
        infeasibleScenarios = set(infeasibleScenarios)

        return WaitAndSeeDict, infeasibleScenarios

    def get_EEV(self, stochastic_input_data=None):
        """
        This function is used to calculate the VSS of a stochastic problem.
        :param stochastic_model_output: is the model output of the stochastic optimisation
        :param input_data of the signal optimisation run::
        :param optimization_mode:
        :param solver:
        :param interface:
        :param solver_path:
        :param options:
        :return:
        """

        def MassBalance_3_rule(self, u_s, u):
            return self.FLOW_ADD[u_s, u] <= self.alpha[u] * self.Y[u]  # Big M constraint

        def MassBalance_6_rule(self, u, uu, i):
            if (u, uu) not in self.U_DIST_SUB:
                    if (u, uu) in self.U_CONNECTORS:
                        return self.FLOW[u, uu, i] <= self.myu[u, uu, i] * self.FLOW_OUT[
                            u, i
                            ] + self.alpha[u] * (1 - self.Y[uu])
                    else:
                        return Constraint.Skip

            else:
                return self.FLOW[u, uu, i] <= sum(
                    self.FLOW_DIST[u, uu, uk, k, i]
                    for (uk, k) in self.DC_SET
                    if (u, uu, uk, k) in self.U_DIST_SUB2
                ) + self.alpha[u] * (1 - self.Y[uu])

        def MassBalance_7_rule(self, u, uu, i):
            if (u,uu) in self.U_CONNECTORS:
                return self.FLOW[u, uu, i] <= self.alpha[u] * self.Y[uu]
            else:
                return Constraint.Skip

        def MassBalance_8_rule(self, u, uu, i):
            if (u, uu) not in self.U_DIST_SUB:
                if (u, uu) in self.U_CONNECTORS:
                    return self.FLOW[u, uu, i] >= self.myu[u, uu, i] * self.FLOW_OUT[
                        u, i
                        ] - self.alpha[u] * (1 - self.Y[uu])
                else:
                    return Constraint.Skip
            else:
                return self.FLOW[u, uu, i] >= sum(
                    self.FLOW_DIST[u, uu, uk, k, i]
                    for (uk, k) in self.DC_SET
                    if (u, uu, uk, k) in self.U_DIST_SUB2
                ) - self.alpha[u] * (1 - self.Y[uu])

        def GWP_6_rule(self, u):
            return self.GWP_UNITS[u] == self.em_fac_unit[u] / self.LT[u] * self.Y[u]

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

        # start with the VSS calculation by setting up a model instance with the single optimization data parameters
        # first run the single run optimization to get the unit operations
        singleInput = self.input_data.parameters_single_optimization
        # singleInput.optimization_mode = "single" # just to make sure
        optimization_mode = "single"
        # populate the model instance with the input data
        model_instance_deterministic_average = self.single_model_instance_4_VSS
        model_instance_variable_params = model_instance_deterministic_average.clone()

        # STEP 1: solve the deterministic model with the average values (i.e. the expected value)
        # -----------------------------------------------------------------------------------------------
        # solve the deterministic model with the average values of the stochastic parameters (i.e. the expected value)

        # settings optimization problem, the optimizer is the single run optimiser
        optimizer = self.single_optimizer

        # run the optimisation
        # EVV expected value problem or mean value problem

        model_output_VSS_average = optimizer.run_optimization(model_instance=model_instance_deterministic_average,
                                                              tee=False, printTimer=False, VSS_EVPI_mode=True)

        if model_output_VSS_average == 'infeasible':
            raise Exception("The model to calculate the VSS is infeasible, please check the input data for the single optimisation problem is correct ")

        # extract the first stage decisions from the model output, i.e. the boolean variables
        BooleanVariables = model_output_VSS_average._data['Y']

        # STEP 2: make the model instance for the VSS calculation with 1st stage decisions fixed
        # -------------------------------------------------------------------------------------------------
        # now make the model where the boolean variables are fixed as parameters
        # loop of ther BooleanVariables and transform the item in the dict to the absolute value
        for key, value in BooleanVariables.items():
            if value is not None:
                BooleanVariables[key] = abs(value)

        # change the model instance copy and fix the boolean variables as parameters
        model_instance_variable_params.del_component(model_instance_variable_params.Y)
        model_instance_variable_params.Y = Param(model_instance_variable_params.U, initialize=BooleanVariables,
                                                 mutable=True, within=Any)

        # delete and redefine the constraints which are affected by the boolean variables
        model_instance_variable_params.del_component(model_instance_variable_params.MassBalance_3)
        model_instance_variable_params.del_component(model_instance_variable_params.MassBalance_6)
        model_instance_variable_params.del_component(model_instance_variable_params.MassBalance_7)
        model_instance_variable_params.del_component(model_instance_variable_params.MassBalance_8)
        model_instance_variable_params.del_component(model_instance_variable_params.EnvironmentalEquation6)  # GWP_6
        model_instance_variable_params.del_component(model_instance_variable_params.ProcessGroup_logic_1)
        model_instance_variable_params.del_component(model_instance_variable_params.ProcessGroup_logic_2)

        # define the constraints again
        model_instance_variable_params.MassBalance_33 = Constraint(model_instance_variable_params.U_SU, rule=MassBalance_3_rule)
        model_instance_variable_params.MassBalance_66 = Constraint(model_instance_variable_params.U, model_instance_variable_params.UU, model_instance_variable_params.I, rule=MassBalance_6_rule)
        model_instance_variable_params.MassBalance_77 = Constraint(model_instance_variable_params.U, model_instance_variable_params.UU, model_instance_variable_params.I, rule=MassBalance_7_rule)
        model_instance_variable_params.MassBalance_88 = Constraint(model_instance_variable_params.U, model_instance_variable_params.UU, model_instance_variable_params.I, rule=MassBalance_8_rule)
        model_instance_variable_params.EnvironmentalEquation66 = Constraint(model_instance_variable_params.U_C, rule=GWP_6_rule)
        model_instance_variable_params.ProcessGroup_logic_11 = Constraint(model_instance_variable_params.U, model_instance_variable_params.UU, rule=ProcessGroup_logic_1_rule)
        numbers = [1, 2, 3]
        model_instance_variable_params.ProcessGroup_logic_22 = Constraint(model_instance_variable_params.U, numbers, rule=ProcessGroup_logic_2_rule)


        # STEP 3: loop over all scenarios and solve the model for each scenario save the results in a list
        # -------------------------------------------------------------------------------------------------
        # now we need to run the single run optimisation for each scenario and save the results in a list
        # now we have the model instance with the fixed boolean variables as parameters
        # the next step is to run individual optimisations for each scenario and save the results in a list
        # first we need to get the scenarios from the input data
        scenarios = stochastic_input_data.Scenarios['SC']
        total_scenarios = len(scenarios)

        # now we need to run the single run optimisation for each scenario
        # preallocate the variables
        EEVDict = {} # dictionary of the EEV for each scenario EEV = Expected results of the Expected Value problem
        objectiveValueList_VSS = []
        infeasibleScenarios = []

        # Green and bold text, warning this might take a while
        print("\033[1;32m" + "Calculating the objective values for each scenario to calculate the VSS\n"
                             "Please be patient, this might take a while" + "\033[0m")

        # Suppress the specific warning if model is infeasible
        logging.getLogger('pyomo.core').setLevel(logging.ERROR)

        # set the options for the single run optimisation
        # set model options

        for index, sc in enumerate(scenarios):
            # model for VSS calculation
            modelInstanceScemario_VSS = self.set_parameters_of_scenario(scenario=sc, singleInput=singleInput,
                                                               stochasticInput=stochastic_input_data, model=model_instance_variable_params)

            # run the optimization
            modelOutputScenario_VSS = optimizer.run_optimization(model_instance=modelInstanceScemario_VSS, tee=False,
                                                                 keepfiles=False, printTimer=False, VSS_EVPI_mode=True)

            if modelOutputScenario_VSS == 'infeasible':
                infeasibleScenarios.append(sc)
            else:
                objectiveName = modelOutputScenario_VSS._objective_function
                objectiveValueList_VSS.append(modelOutputScenario_VSS._data[objectiveName])
                EEVDict.update({sc: modelOutputScenario_VSS._data[objectiveName]})

            # print the progress bar
            print_progress_bar(iteration=index, total=total_scenarios, prefix='EVPI', suffix='')

        # now we have the objective values for each scenario in a Dictionary

        # Print a newline character to ensure the next console output is on a new line.
        print()
        # reactivate the warning if model is infeasible
        logging.getLogger('pyomo.core').setLevel(logging.WARNING)

        # make a set of infeasible scenarios to get rid of duplicates
        if infeasibleScenarios:
            infeasibleScenarios = set(infeasibleScenarios)
            # print a warning in red and bold text
            print("\033[1;31m" + "The following scenarios during VSS calculations are infeasible:", infeasibleScenarios, "\n"
             " please check the optimization problem or report the problem to github \033[0m")

        return EEVDict

    def curate_EEV(self, EEV, expectedValueStochastic):
        """"
        The curation of the list of EEV is need because scenarios can exist where |Determinist value| > |Stochastic value|
        which should not be possible. This is due to the fact that the stochastic optimization takes into account the MAXIMUM
        reference flow rate to calculate the CAPEX. if this happens we'll assume that the deterministic value is equal to the stochastic value
        :param EEV: list of EEV
        :param expectedValueStochastic: expected value of the stochastic optimisation
        :return: EEV: mean of the EEV list
        """
        EEV_New = []
        for evv in EEV:
            if abs(evv) > abs(expectedValueStochastic):
                EEV_New.append(expectedValueStochastic)
            else:
                EEV_New.append(evv)
        EEVmean = np.mean(EEV_New)
        return EEVmean

    def set_parameters_of_scenario(self, scenario, singleInput, stochasticInput, model):
        """
        This function is used to set the parameters of the stochastic model instance according to the scenario
        for a single deterministic run.

        :param scenario:
        :param singleInput:
        :param stochasticInput:
        :param model:
        :return: model instance with the parameters of the scenario
        """

        # set the parameters of the single run optimisation
        singleDataFile = singleInput.Data_File
        # set the parameters of the stochastic run optimisation
        stochasticDataFile = stochasticInput.Data_File

        # need to go over the following parameters: phi, myu, xi, materialcosts, ProductPrice, gamma and theta
        # make a list of the parameters
        parameterList = ['phi', 'myu', 'xi', 'materialcosts', 'ProductPrice', 'gamma', 'theta']

        for parameter in parameterList:
            # first check if the parameter is in the single run optimization data
            if parameter in singleDataFile[None]:
                # get the parameter from the single run optimization
                parameterSingle = singleDataFile[None][parameter]
                # get the parameter from the stochastic run optimization
                parameterStochastic = stochasticDataFile[None][parameter]

                # update the model instance
                for index in parameterSingle:
                    if isinstance(index, tuple):
                        newIndex = tuple(list(index) + [scenario])
                    else:
                        newIndex = tuple([index] + [scenario])

                    new_value = parameterStochastic[newIndex]
                    model.__dict__[parameter][index] = new_value

        return model

    def count_unique_sets(self, list_of_dicts):
        """
        This function is used to count the number of unique sets in a list of dictionaries
        :param list_of_dicts: list of dictionaries with the unique sets of technologies
        :return: count: number of unique sets
        """
        # Create an ordered dictionary to store the count of each unique dictionary
        unique_dict_count = {}

        # Iterate through the list of dictionaries
        for dictionary in list_of_dicts:
            # Convert the dictionary to a tuple of key-value pairs for hashing
            dict_as_tuple = tuple(dictionary.items())

            # Check if the tuple representation is already in the unique_dict_count dictionary
            if dict_as_tuple in unique_dict_count:
                # If it's already in the dictionary, increment the count
                unique_dict_count[dict_as_tuple] += 1
            else:
                # If it's not in the dictionary, add it with a count of 1
                unique_dict_count[dict_as_tuple] = 1

        total_sets = len(list_of_dicts)
        for unique_dict, count in unique_dict_count.items():
            percent = round((count / total_sets) * 100, 1)
            print("\033[95m\033[1mDictionary:", dict(unique_dict), "percent (%):", percent, "\033[0m")

class WaitAndSeeOptimizer(StochasticRecourseOptimizer):
    def __init__(
        self,
        solver_name,
        solver_interface,
        input_data,
        solver_options=None,
        single_model_instance=None,
        stochastic_options=None,
        remakeMetadata = None
    ):

        super().__init__(solver_name, solver_interface, solver_options)
        self.single_optimizer = SingleOptimizer(solver_name, solver_interface, solver_options)
        self.input_data = input_data
        self.single_model_instance_4_EVPI = single_model_instance.clone()
        self.single_model_instance_4_VSS = single_model_instance.clone()
        self. remakeMetadata = remakeMetadata
        if stochastic_options is None:
            self.stochastic_options = {
                "calculation_EVPI": True,
                "calculation_VSS": True,
            }
        else:
            self.stochastic_options = stochastic_options

    def run_optimization(self,
                         model_instance,
                         optimization_mode=None,
                         solver="gurobi",
                         interface="local",
                         solver_path=None,
                         options=None,
                         count_variables_constraints=False):

        # preallocate the variables
        infeasibleScenarios = None
        waitAndSeeSolution = 0
        average_VSS = 0

        # get the input data and stochastic options
        input_data = self.input_data
        calculation_EVPI = self.stochastic_options["calculation_EVPI"]
        calculation_VSS = self.stochastic_options["calculation_VSS"]

        waitAndSeeSolutionDict = {}
        EEVDict = {}



        # make a deep copy of the input data so the stochastic parameters can be transformed to final dataformat
        Stochastic_input_EVPI = copy.deepcopy(input_data)
        Stochastic_input_EVPI.create_DataFile()
        Stochastic_input_vss = copy.deepcopy(Stochastic_input_EVPI)


        # timer for the EVPI calculation
        startEVPI = time_printer(programm_step="Wait and see calculation")
        # create the Data_File Dictionary in the object input_data

        waitAndSeeSolutionDict, infeasibleScenarios = self.get_WaitAndSee(Stochastic_input_EVPI)
        time_printer(passed_time=startEVPI, programm_step="Wait and see calculation")

class StochasticRecourseOptimizer_mpi_sppy(SingleOptimizer):

    def __init__(
        self,
        solver_name,
        solver_interface,
        inputObject,
        mpiOptions,
        solver_options=None,
    ):
        # initialize the single optimizer
        super().__init__(solver_name, solver_interface, solver_options)

        # set the optimization mode
        # todo find where the optimisation mode is passed on, this is not the right place to define it but ok for now
        self.optimization_mode = "2-stage-recourse"

        # initialize the input object
        if inputObject is None:
            raise Exception("No input object is provided")
        else:
            self.inputObject = inputObject

        if mpiOptions is None:
            raise Exception("No mpi-sppy options are provided")
        else:
            self.options = mpiOptions

    def run_optimization(self,*args, **kwargs):

        StartTimer = time_printer(printTimer=False)

        # run the stochastic optimization
        phResults = self.run_progressive_hedging(inputObject=self.inputObject,options=self.options)
        # phResults is a tuple with the following elements: (variablesR0, allVariables, VariableWarningDict)

        timeMpiSppy = time_printer(passed_time=StartTimer,
                                   printTimer=False)



        modelOutput = StochasticModelOutput_mpi_sppy(optimization_mode = '2-stage-recourse', #todo again shady, find where this variable is set and pass it on
                                                     mpi_sppy_results=phResults,
                                                     run_time = timeMpiSppy)

        return modelOutput

    def scenario_creator(self, scenarioName):
        """
        This function is used to create instances of a scenario, used to run optimization problems under uncertainty
        using mpi-sppy. The function is called by mpi-sppy and should return a Pyomo model instance for the scenario

        :param scenario_name:
        :param inputObject:
        :return: model_instance
        """

        # retrive the data file for all scenarios
        inputObject = self.inputObject
        scenarioDataFile = inputObject.scenarioDataFiles

        # initialize the model
        model = SuperstructureModel(inputObject)

        # create the model equations
        model.create_ModelEquations()

        # get the correct data file for the scenarioDataFile
        dataFile = scenarioDataFile[scenarioName]

        # populate the model instance
        modelInstance = model.populateModel(dataFile)

        # introduce the model instance to mpi-sppy
        sputils.attach_root_node(modelInstance,
                                 modelInstance.Objective,  # the objective function
                                 # the first stage variables, which are non-anticipative constraints.
                                 # i.e., do not change across scenarios. In this case, the binary variables responsible
                                 # for the selection of the technology
                                 [modelInstance.Y])  # todo add?  ,modelInstance.Y_DIST

        modelInstance._mpisppy_probability = 1.0 / len(scenarioDataFile)

        return modelInstance

    def run_extensive_form(self, options, allScenarioNames):
        """
        This function runs the extensive form of the optimization problem. The extensive form is a deterministic
        optimization problem where all scenarios are considered. The function returns the objective value and the
        solution of the extensive form.

        :param options: a dictionary with options for the extensive form
        :param allScenarioNames: a list with the names of all scenarios
        :param scenario_creator: a function which creates the model instance for a scenario
        :return: objective value, solution
        """

        ef = ExtensiveForm(options, allScenarioNames, self.scenario_creator)
        results = ef.solve_extensive_form()

        objval = ef.get_objective_value()
        soln = ef.get_root_solution()

        return objval, soln

    def run_progressive_hedging(self, inputObject, options):
        """
        This function runs the progressive hedging algorithm for solving the stochastic optimization problem. The
        function returns the objective value and the solution of the progressive hedging algorithm.

        :param options: a dictionary with options for the progressive hedging algorithm
        :param all_scenario_names: a list with the names of all scenarios
        :param scenario_creator: a function which creates the model instance for a scenario
        :return: objective value, solution
        """
        allScenarioNames = list(inputObject.scenarioDataFiles.keys())
        self.inputObject = inputObject

        ph = PH(options,
                allScenarioNames,
                self.scenario_creator)

        ph.ph_main()

        variablesR0 = ph.gather_var_values_to_rank0()

        # Gather and print all variable values for the first scenario
        allVariables = {}
        VariableWarningDict = {}
        for sc in allScenarioNames:
            scenario = ph.local_scenarios[sc]
            allVariables.update({sc: {}})
            VariableWarningDict.update({sc: {}})
            # print(f"\nResults for scenario {allScenarioNames[0]}:")
            for var in scenario.component_objects(pyo.Var, active=None):
                try:
                    var_object = getattr(scenario, str(var))
                    for index in var_object:
                        allVariables[sc].update({f"{var}[{index}]": pyo.value(var_object[index])})

                        # if sc == allScenarioNames[0]: # only print the variables for the first scenario
                        #     print(f"{var}[{index}] = {pyo.value(var_object[index])}")

                except:
                    VariableWarningDict[sc].update({str(var): "Variable not calculated"})
                    # print(f"Variable {var_object} is not calculated!!")
                    continue

        return variablesR0, allVariables, VariableWarningDict






