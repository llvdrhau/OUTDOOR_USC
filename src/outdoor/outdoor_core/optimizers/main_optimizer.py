#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 12:19:19 2021

@author: philippkenkel
"""

import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

from ..output_classes.model_output import ModelOutput
from ..output_classes.stochastic_model_output import StochasticModelOutput

from ..utils.timer import time_printer


class SingleOptimizer:
    """
    Class Description
    -----------------
    This Class is the model instance handler. It takes holds the run_optimization
    method which takes any PYOMO concrete model, solves it and return and ModelOuput
    Class object.

    It is also the parent class of the custom Opimizer Classes which are written
    especially for special runs in Superstructure Opimitzation (e.g. Sensitivity etc.)
    """
    def __init__(self, solver_name, solver_interface, optimization_mode= None, solver_path=None,
                 solver_options=None):
        """
        Parameters
        ----------
        solver_name : String
        solver_interface : String
        solver_options : Dict, optional

        Description
        -------
        Constructor of the SingleOptimzer. It checks if the handed solver is in the
        solver library as well as the interface in the interface library. However,
        it does NOT check if the solvers are installed on the maschine.

        """

        SOLVER_LIBRARY = {"gurobi", "cbc", "scip", "glpk", 'gams'}
        INTERFACE_LIBRARY = {"local", "executable"}

        # setup name
        if solver_name in SOLVER_LIBRARY:
            self.solver_name = solver_name
        else:
            self.solver_name = solver_name
            raise Exception("Solver not in library, correct optimization not garanteed")

        # setup interface
        if solver_interface in INTERFACE_LIBRARY:
            self.solver_interface = solver_interface
        else:
            raise Exception("Solver interface not in library, correct optimization not garanteed")

        # check for gurobi
        if self.solver_name == "gurobi":
            self.solver_io = "python"

        # create solver
        if solver_interface == "local":
            if solver_name == "gurobi":
                self.solver = pyo.SolverFactory(
                    self.solver_name, solver_io=self.solver_io
                    )
            else:
                self.solver = pyo.SolverFactory(self.solver_name)
        else:
            self.solver = pyo.SolverFactory(self.solver_name,
                                            executable=solver_path)


        self.solver = self.set_solver_options(self.solver, solver_options)

        # save optimisation mode
        self.optimization_mode = optimization_mode

    def run_optimization(self,
                         model_instance,
                         tee=True,
                         keepfiles = True,
                         printTimer=True,
                         VSS_EVPI_mode=False,
                         stochastic_optimisation=False):


        """
        Parameters
        ----------
        model_instance : PYOMO Concrete Model

        Returns
        -------
        model_output : ModelOutput

        Description
        -----------
        This is the main optimization method of the optimizer. It calls the
        solver.solve function from pyomo, and stores all results
        (Sets, Params, Var, Objective, Optimimality gap) in the ModelOuput object.

        """

        timer = time_printer(programm_step='Superstructure optimization run', printTimer=printTimer)


        results = self.solver.solve(model_instance, keepfiles=keepfiles, tee=tee)


        # Check if the model is infeasible
        if (results.solver.termination_condition == TerminationCondition.infeasibleOrUnbounded or
            results.solver.termination_condition == TerminationCondition.infeasible):

            if not VSS_EVPI_mode:
                raise Exception("The model is infeasible, please check the input data is correct. \n"
                                " TIP check the min max sourse fluxes and pool fluxes .")
            else:
                return 'infeasible' # so we can save the conditions where the solution is infeasible in the VSS_EVPI mode
        else:
            # The model may be feasible or have some other issue
            if results.solver.termination_condition == TerminationCondition.optimal:
                pass
                #print("The model is optimal.")
            elif results.solver.termination_condition == TerminationCondition.licensingProblems:
                raise Exception('There seems to be a problem with the licencing of your solver\n'
                                ' please check that the solver is correctly installed on choose another')
            else:
                print("The solver terminated with a different condition.: ", results.solver.termination_condition)

        gap = (
            (results["Problem"][0]["Upper bound"] - results["Problem"][0]["Lower bound"])
            / results["Problem"][0]["Upper bound"]) * 100

        timer = time_printer(timer, 'Single optimization run', printTimer=printTimer)

        if stochastic_optimisation: # if the run is a stochastic run we need to use the stochastic model output class
            model_output = StochasticModelOutput(model_instance=model_instance, # the model instance now contains the optimised values
                                                 optimization_mode='Single 2-stage recourse optimization',
                                                 solver_name=self.solver_name, run_time=timer, gap=gap)
        else:
            model_output = ModelOutput(model_instance=model_instance,
                                       optimization_mode='Single run optimization',
                                       solver_name=self.solver_name, run_time=timer, gap=gap)

        return model_output


    def set_solver_options(self, solver, options):
        """
        Parameters
        ----------
        solver : Pyomo solver object

        options : Dict


        Returns
        -------
        solver : Pyomo solver object

        Description
        -----------
        Sets solver options based on the options in the dictionary.

        """

        # lowering the integer feasibility tolerance
        if options is None:
            options = {}
            options['IntFeasTol'] = 1e-8
        else:
            options.update({'IntFeasTol': 1e-8})

        if options is not None:
            for i, j in options.items():
                solver.options[i] = j
        else:
            pass
        return solver
