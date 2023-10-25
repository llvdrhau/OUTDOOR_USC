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

from pyomo.environ import Param

import numpy as np

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

    def solve_optimization_problem(
        self,
        input_data=None,
        optimization_mode= None,
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

        if optimization_mode is None:
            optimization_mode = input_data.optimization_mode


        solving_time = time_printer(
            programm_step="Superstructure optimization procedure"
        )
        if self.parser == "Superstructure":

            # populate the model instance with the input data
            model_instance = self.setup_model_instance(input_data, optimization_mode)

            # check for nan Values
            check_nan = self.find_nan_parameters_in_model_instance(model_instance)

            if check_nan:
                print('')
                print("There are NaN values in the model instance. Please check the model.")
                print(check_nan)
                print('')

            # set model options
            mode_options = self.set_mode_options(optimization_mode, input_data)

            # settings optimisation problem
            optimizer = self.setup_optimizer(solver, interface, solver_path, options, optimization_mode,
                                             mode_options, input_data)

            # run the optimisation
            model_output = optimizer.run_optimization(model_instance)
            solving_time = time_printer(solving_time, "Superstructure optimization procedure")
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
        optimisationModeExcel = input_data.optimization_mode
        optimisationModeScript = optimization_mode

        if optimisationModeExcel != optimisationModeScript:
            raise ValueError(f"The optimisation mode in the excel file is {optimisationModeExcel} "
                             f"and the one given from the script is {optimisationModeScript}. "
                             f"Please check the excel file or script.")


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

        timer = time_printer(programm_step="Optimizer setup")

        if optimization_mode == "single" or optimization_mode == "2-stage-recourse":
            optimizer = SingleOptimizer(solver, interface, solver_path, options)

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

        timer = time_printer(passed_time=timer, programm_step="Optimizer setup")

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

    def find_nan_parameters_in_model_instance(self,model):
        """
        Check for NaN values in parameters of a Pyomo model.

        Args:
            model: A Pyomo model instance.

        Returns:
            A list of tuples containing component and key for parameters with NaN values.
            Returns an empty list if no NaN values are found.
        """
        nan_parameters = []

        #parameter_declarations = list(model.component_data_objects(Param, active=True))


        #Iterate through all active parameters in the model
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



        if nan_parameters:
            print("The following parameters have None values, check if they are correct:")
            for param in nan_parameters:
                if isinstance(param[2],str):
                    # if a string delete the value from the list
                    nan_parameters.remove(param)
                else:
                    print(f"Parameter {param[0].name}[{param[1]}]: {param[2]}")

            #raise ValueError("NaN values in parameters detected. Please check the model.")

        return nan_parameters
