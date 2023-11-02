from ..model.optimization_model import SuperstructureModel
from ..model.optimisation_model_2_stage_recourse import SuperstructureModel_2_Stage_recourse

from ..optimizers.main_optimizer import SingleOptimizer

from ..optimizers.customs.custom_optimizer import (
    MCDAOptimizer,
    SensitivityOptimizer,
    TwoWaySensitivityOptimizer,
)

from ..utils.timer import time_printer
from ..optimizers.customs.change_params import prepare_mutable_parameters


import numpy as np

from pyomo.environ import *

import sys


class SuperstructureProblem:
    """
    Class Description
    -----------------

    This Class is the main handler of OUTDOORS modeling and optimization framework.
    It is created, and afterwards the main "solve_optimization_problem" is called
    with given input data, solver name etc.

    This class afterwards calls different classes which
        - Create the model  (SuperstructureModel Class)
        - Populate the model to a model instancen (PYOMO ConcreteModel)
        - Creates the appropriate Optimizer Class obects
        - Hands the model instance to the Optimizer, which solves the model
        using the defined external solver and returns a ModelOutput Class object.
    """

    def __init__(self, parser_type="Superstructure"):
        """

        Parameters
        ----------
        parser_type : String, optional
            DESCRIPTION: Takes the type of which data is parsed. Permitted values
                are "Superstructure" and "External". RIGHT NOW THERE IS NO ALGORITHM
                WHICH WORKS WITH EXTERNAL.

        """

        PARSER_SET = {"Superstructure", "External"}
        if parser_type in PARSER_SET:
            self.parser = parser_type
        else:
            print(
                f"Parser type not recognized, \
                please use one of the following key words:{PARSER_SET}"
            )

        self.CheckNoneVariables = []

    def get_VSS_and_EVPI(self,
                         expected_value,
                         input_data=None,
                         solver="gurobi",
                         interface="local",
                         solver_path=None,
                         options=None):
        """
        This function is used to calculate the VSS and EVPI of a stochastic problem.
        :param input_data of the signal optimisation run::
        :param optimization_mode:
        :param solver:
        :param interface:
        :param solver_path:
        :param options:
        :return:
        """
        def set_parameters_of_scenario(scenario, singleInput, stochasticInput, model):
            # set the parameters of the single run optimisation
            singleDataFile = singleInput.Data_File
            # set the parameters of the stochastic run optimisation
            stochasticDataFile = stochasticInput.Data_File

            # need to go over the following parameters: phi, myu, xi, materialcosts, ProductPrice, gamma and theta

            # first the phi parameter
            phi = singleDataFile[None]['phi']
            phiSto = stochasticDataFile[None]['phi']
            for keys, values in phi.items():
                phi[keys] = phiSto[keys[0],keys[1], scenario]

            # second the myu parameter
            myu = singleDataFile[None]['myu']
            myuSto = stochasticDataFile[None]['myu']
            for keys, values in myu.items():
                myu[keys] = myuSto[keys[0],keys[1], scenario]

            # third the xi parameter
            xi = singleDataFile[None]['xi']
            xiSto = stochasticDataFile[None]['xi']
            for keys, values in xi.items():
                xi[keys] = xiSto[keys[0],keys[1], scenario]

            # fourth the materialcosts parameter
            materialcosts = singleDataFile[None]['materialcosts']
            materialcostsSto = stochasticDataFile[None]['materialcosts']
            for keys, values in materialcosts.items():
                materialcosts[keys] = materialcostsSto[keys, scenario]

            # fifth the productPrice parameter
            productPrice = singleDataFile[None]['ProductPrice']
            productPriceSto = stochasticDataFile[None]['ProductPrice']
            for keys, values in productPrice.items():
                productPrice[keys] = productPriceSto[keys, scenario]

            # sixth the gamma parameter
            gamma = singleDataFile[None]['gamma']
            gammaSto = stochasticDataFile[None]['gamma']
            for keys, values in gamma.items():
                gamma[keys] = gammaSto[keys[0],keys[1], scenario]

            # seventh the theta parameter
            theta = singleDataFile[None]['theta']
            thetaSto = stochasticDataFile[None]['theta']
            for keys, values in theta.items():
                theta[keys] = thetaSto[keys[0],keys[1], scenario]


            # update the model instance
            # phi
            for index, new_value in phi.items():
                model.phi[index] = new_value
            # myu
            for index, new_value in myu.items():
                model.myu[index] = new_value
            # xi
            for index, new_value in xi.items():
                model.xi[index] = new_value
            # materialcosts
            for index, new_value in materialcosts.items():
                model.materialcosts[index] = new_value
            # productPrice
            for index, new_value in productPrice.items():
                model.ProductPrice[index] = new_value
            # gamma
            for index, new_value in gamma.items():
                model.gamma[index] = new_value
            # theta
            for index, new_value in theta.items():
                model.theta[index] = new_value

            return model

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


        # start with the VSS calculation

        # first run the single run optimisation to get the unit operations
        singleInput = input_data.parameters_single_optimization
        # singleInput.optimization_mode = "single" # just to make sure
        optimization_mode = "single"
        # populate the model instance with the input data
        model_instance = self.setup_model_instance(singleInput, optimization_mode)

        # set model options
        mode_options = self.set_mode_options(optimization_mode, singleInput)

        # settings optimisation problem
        optimizer = self.setup_optimizer(solver, interface, solver_path, options, optimization_mode,
                                         mode_options, singleInput)

        # run the optimisation
        model_output = optimizer.run_optimization(model_instance)

        # Extract the boolean variables choosing the units from the model output and save them in a list
        fixBooleanVariables = model_output._data['Y']

        # now make a deep copy of the model and fix the boolean variables as parameters in the model
        model_instance_vss = model_instance.clone()
        model_instance_EVPI = model_instance.clone()

        # change the model instance copy
        model_instance_vss.del_component(model_instance_vss.Y)
        model_instance_vss.Y = Param(model_instance_vss.U, initialize=fixBooleanVariables, mutable=True)

        # delete and redefine the constraints which are affected by the boolean variables
        model_instance_vss.del_component(model_instance_vss.MassBalance_3)
        model_instance_vss.del_component(model_instance_vss.MassBalance_6)
        model_instance_vss.del_component(model_instance_vss.MassBalance_7)
        model_instance_vss.del_component(model_instance_vss.MassBalance_8)
        model_instance_vss.del_component(model_instance_vss.EnvironmentalEquation6) # GWP_6
        model_instance_vss.del_component(model_instance_vss.ProcessGroup_logic_1)
        model_instance_vss.del_component(model_instance_vss.ProcessGroup_logic_2)

        # define the new constraints
        model_instance_vss.MassBalance_33 = Constraint(model_instance_vss.U_SU, rule=MassBalance_3_rule)
        model_instance_vss.MassBalance_66 = Constraint(model_instance_vss.U, model_instance_vss.UU, model_instance_vss.I, rule=MassBalance_6_rule)
        model_instance_vss.MassBalance_77 = Constraint(model_instance_vss.U, model_instance_vss.UU, model_instance_vss.I, rule=MassBalance_7_rule)
        model_instance_vss.MassBalance_88 = Constraint(model_instance_vss.U, model_instance_vss.UU, model_instance_vss.I, rule=MassBalance_8_rule)
        model_instance_vss.EnvironmentalEquation66 = Constraint(model_instance_vss.U_C, rule=GWP_6_rule)
        model_instance_vss.ProcessGroup_logic_11 = Constraint(model_instance_vss.U, model_instance_vss.UU, rule=ProcessGroup_logic_1_rule)
        numbers = [1, 2, 3]
        model_instance_vss.ProcessGroup_logic_22 = Constraint(model_instance_vss.U, numbers, rule=ProcessGroup_logic_2_rule)

        # now we have the model instance with the fixed boolean variables as parameters
        # the next step is to run individual optimisations for each scenario and save the results in a list
        # first we need to get the scenarios from the input data
        scenarios = input_data.Scenarios['SC']

        # now we need to run the single run optimisation for each scenario
        objectiveValueList_VSS = []
        objectiveValueList_EVPI = []
        # Green and bold text
        print("\033[1;32m" + "Calculating the objective values for each scenario to calculate the VSS and EVPI\n"
                             "Please be patient, this might take a while" + "\033[0m")

        total_scenarios = len(scenarios)
        for index, sc in enumerate(scenarios):
            # model for VSS calculation
            modelInstanceScemario_VSS = set_parameters_of_scenario(scenario=sc, singleInput=singleInput,
                                                               stochasticInput=input_data, model=model_instance_vss)
            # solve the single run optimisation
            optimizer = self.setup_optimizer(solver, interface, solver_path, options, optimization_mode,
                                             mode_options, singleInput, printTimer=False)
            # run the optimisation
            modelOutputScenario_VSS = optimizer.run_optimization(model_instance=modelInstanceScemario_VSS, tee=False, printTimer=False)
            objectiveName = modelOutputScenario_VSS._objective_function
            objectiveValueList_VSS.append(modelOutputScenario_VSS._data[objectiveName])

            # model for EVPI calculation, the only difference is that the boolean variables are not fixed
            # i.e. all model variables are optimised according to the scenario parameters
            modelInstanceScemarioEVPI = set_parameters_of_scenario(scenario=sc, singleInput=singleInput,
                                                               stochasticInput=input_data, model=model_instance_EVPI)
            # solve the single run optimisation
            optimizer = self.setup_optimizer(solver, interface, solver_path, options, optimization_mode,
                                             mode_options, singleInput, printTimer=False)
            # run the optimisation
            modelOutputScenario_EVPI = optimizer.run_optimization(model_instance=modelInstanceScemarioEVPI, tee=False,
                                                             printTimer=False)
            objectiveName = modelOutputScenario_EVPI._objective_function
            objectiveValueList_EVPI.append(modelOutputScenario_EVPI._data[objectiveName])


            # Now let's print the progress bar
            progress = (index + 1) / total_scenarios
            bar_length = 40  # Modify this to change the length of the progress bar
            block = int(round(bar_length * progress))
            text = "\rProgress: [{0}] {1:.2f}%".format("#" * block + "-" * (bar_length - block), progress * 100)
            sys.stdout.write(text)
            sys.stdout.flush()

        # now we have the objective values for each scenario in a list
        # the next step is to calculate the VSS
        VSS = expected_value - np.mean(objectiveValueList_VSS)
        EVPI = np.mean(objectiveValueList_EVPI) - expected_value
        # Print a newline character to ensure the next console output is on a new line.
        print()

        return EVPI, VSS

    def solve_optimization_problem(
        self,
        input_data=None,
        optimization_mode=None,
        solver="gurobi",
        interface="local",
        solver_path=None,
        options=None,
    ):
        """

        Parameters
        ----------
        input_data : Superstructure Object, optional
            DESCRIPTION: Input data, if parser type=Superstructure, has to be
                a Superstructure Class object.
        optimization_mode : string, optional
            DESCRIPTION. The default is "single". Other permitted values are:
                'sensitivity', 'cross-parameter', 'multi-objective'
        solver : string, optional
            DESCRIPTION. The default is "gurobi". Solver name to use, solver must
                be installed.
        interface : string optional
            DESCRIPTION. The default is "local". Permitted values ares:
                'local', 'executable'. Local are installed solver packages,
                executables are .exe-files which can be used directly.
        solver_path : string optional
            DESCRIPTION: If 'executable' is choses as solver interface, a path
                has to be defined where the .exe-file is located on the machine.
        options : Dictionarry, optional
            DESCRIPTION. The default is None. Solver options as dictionary.
                Keys are options, values are values. Keys have to be permitted by
                chosen solver.


        Returns
        -------
        model_output : ModelOutput / MultiModelOutput

        Description
        -----------

        The main optimization function. It prepares the model instance,
        Optimizer and optionals. Afterwards solves the model instance by calling
        the Optimizer run_optimization function. Calls the following functions
        in order:
            1) setup_model_instance()
            2) set_mode_options()
            3) setup_optimizer()
            4) optimizer.run_optimization()

        """
        self._optimization_mode = optimization_mode
        if optimization_mode is None:
            optimization_mode = input_data.optimization_mode
            self._optimization_mode = input_data.optimization_mode


        solving_time = time_printer(
            programm_step="Superstructure optimization procedure"
        )
        if self.parser == "Superstructure":

            # populate the model instance with the input data
            model_instance = self.setup_model_instance(input_data, optimization_mode)

            # check for nan Values
            check_nan = self.find_nan_parameters_in_model_instance(model_instance)
            self.CheckNoneVariables = check_nan

            # set model options
            mode_options = self.set_mode_options(optimization_mode, input_data)

            # settings optimisation problem
            optimizer = self.setup_optimizer(solver, interface, solver_path, options, optimization_mode,
                                             mode_options, input_data)

            # run the optimisation
            model_output = optimizer.run_optimization(model_instance)
            time_printer(solving_time, "Superstructure optimization procedure")

            # if the problem is a stochastic problem, a single objective optimisations are solved multiple times to
            # calulate the Expected Value of Perfect Information (EVPI) and the Value of the Stochastic Solution (VSS)
            if optimization_mode == "2-stage-recourse":
                objectiveName = model_output._objective_function
                expected_value = model_output._data[objectiveName]

                EVPI, VSS = self.get_VSS_and_EVPI(expected_value, input_data, solver, interface,
                                                    solver_path, options)

                #print(f"the EVPI is {EVPI} and the VSS is {VSS}")
                model_output.EVPI = EVPI
                model_output.VSS = VSS

            return model_output
        else:
            raise Exception("Currently there is no routine for external data parsing implemented")

    def setup_model_instance(self, input_data, optimization_mode):
        """

        Parameters
        ----------
        input_data : Superstructure Class object

        optimization_mode : String
            DESCRIPTION: If optimization_mode is 'sensitivity' or
                'cross-parameter sensitivity' this function prepares the mutable
                parameters of the model instance. Otherwise all parameters are
                kept as non-mutable.


        Returns
        -------
        model_instance : Pyomo ConcreteModel

        Description
        -----------
        Creates model instance by first creating data file
        from Superstructure, then creating SuperstructureModel objects.
        Afterwards prepares mutable parameters (if required) and populates model

        """
        # create a error warning if the optimisation mode in the excel is not the same as the one given from the script
        # should be redundant with the new parser
        # optimisationModeExcel = input_data.optimization_mode
        # optimisationModeScript = optimization_mode
        # if optimisationModeExcel != optimisationModeScript:
        #     raise ValueError(f"The optimisation mode in the excel file is {optimisationModeExcel} "
        #                      f"and the one given from the script is {optimisationModeScript}. "
        #                      f"Please check the excel file or script.\n "
        #                      f"The possible options are: 'single', 'sensitivity', 'cross-parameter', 'multi-objective' and '2-stage-recourse' ")

        timer = time_printer(programm_step="DataFile, Model- and ModelInstance setup")


        data_file = input_data.create_DataFile()

        if optimization_mode == "2-stage-recourse":
            model = SuperstructureModel_2_Stage_recourse(input_data)
        else:
            model = SuperstructureModel(input_data)

        model.create_ModelEquations()

        if optimization_mode == "sensitivity" or optimization_mode == "cross-parameter sensitivity":
            mode_options = input_data.sensitive_parameters
            prepare_mutable_parameters(model, mode_options)

        # populate the model instance
        model_instance = model.populateModel(data_file)

        timer = time_printer(timer, "DataFile, Model- and ModelInstance setup")

        return model_instance

    def setup_optimizer(
        self,
        solver,
        interface,
        solver_path,
        options,
        optimization_mode,
        mode_options,
        superstructure,
        printTimer=True,
    ):
        """


        Parameters
        ----------
        solver : String
            DESCRIPTION: Solver name
        interface : String
            DESCRIPTION: Interface
        solver_path: String
            DESCRIPTION: Path to .exe-file of executable solver
        options : Dictionary
            DESCRIPTION: Solver options
        optimization_mode : String
            DESCRIPTION: Optimization mode. Permitted values are:
                'single', 'multi-objective', 'sensitivity' and
                'cross-parameter sensitivity'.
        mode_options : Dictionary
            DESCRIPTION: Additional information eg on sensitive parameters
        superstructure : Superstructure Class object
            DESCRIPTION.


        Returns
        -------
        optimizer : SingleOptimizer (other custom Optimizers)


        Description
        -----------
        Creates an Optimizer Class object depending on the optimization mode,
        solver and interface. Returns the Optimizer

        """
        MODE_LIBRARY = {"single",
                        "multi-objective",
                        "sensitivity",
                        "cross-parameter sensitivity",
                        "2-stage-recourse"
                        }

        if optimization_mode not in MODE_LIBRARY:
            print(
                f"Optimization mode is not supported, \n "
                f"please select from: {MODE_LIBRARY}"
            )

        timer = time_printer(programm_step="Optimizer setup", printTimer=printTimer)

        if optimization_mode == "single" or optimization_mode == "2-stage-recourse":
            optimizer = SingleOptimizer(solver_name=solver, solver_interface=interface,
                                        optimization_mode=optimization_mode, solver_path=solver_path,
                                        solver_options=options)

        elif optimization_mode == "multi-objective":
            optimizer = MCDAOptimizer(solver, interface, options, mode_options)

        elif optimization_mode == "sensitivity":
            optimizer = SensitivityOptimizer(
                solver, interface, options, mode_options, superstructure)

        elif optimization_mode == "cross-parameter sensitivity":
            optimizer = TwoWaySensitivityOptimizer(
                solver, interface, options, mode_options, superstructure
            )
        else:
            raise ValueError("Optimization mode not supported")

        time_printer(passed_time=timer, programm_step="Optimizer setup", printTimer=printTimer)

        return optimizer

    def set_mode_options(self, optimization_mode, superstructure):
        """

        Parameters
        ----------
        optimization_mode : String


        Returns
        -------
        mode_options : Dictionary

        Descripion
        ----------
        Collects for Multi-Run Optimizations the required data from the Superstructure
        Object. e.g. sensititive parameters for sensitivity run.

        """
        if optimization_mode == "multi-objective":
            mode_options = superstructure.multi_objectives
        elif (
            optimization_mode == "sensitivity" or optimization_mode == "cross-parameter sensitivity"
        ):
            mode_options = superstructure.sensitive_parameters
        else:
            mode_options = None

        return mode_options

    def find_nan_parameters_in_model_instance(self, model, print_nan_parameters=False):
        """
        Check for NaN values in parameters of a Pyomo model.

        Args:
            model: A Pyomo model instance.

        Returns:
            A list of tuples containing component and key for parameters with NaN values.
            Returns an empty list if no NaN values are found.
        """
        nan_parameters = []

        # parameter_declarations = list(model.component_data_objects(Param, active=True))

        # Iterate through all active parameters in the model
        for component in model.component_objects(Param, active=True):
            for key in component:
                param_value = component[key]
                # check if param_value is a string
                # if isinstance(param_value, str):
                #     continue
                try:
                    if np.isnan(param_value) and not isinstance(param_value, str):
                        nan_parameters.append((component, key, param_value))
                except:
                    nan_parameters.append((component, key, param_value))

        if print_nan_parameters:
            if nan_parameters:
                print("The following parameters have None values, check if they are correct:")
                for param in nan_parameters:
                    if isinstance(param[2], str):
                        # if a string delete the value from the list
                        nan_parameters.remove(param)
                    else:
                        print(f"Parameter {param[0].name}[{param[1]}]: {param[2]}")

                # raise ValueError("NaN values in parameters detected. Please check the model.")

        return nan_parameters




