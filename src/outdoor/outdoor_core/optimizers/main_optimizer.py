#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 12:19:19 2021

@author: philippkenkel
"""

import pyomo.environ as pyo

from ..output_classes.model_output import ModelOutput
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
    def __init__(self, solver_name, solver_interface, solver_path=None,
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

        SOLVER_LIBRARY = {"gurobi", "cbc", "scip", "glpk"}
        INTERFACE_LIBRARY = {"local", "executable"}

        # setup name
        if solver_name in SOLVER_LIBRARY:
            self.solver_name = solver_name
        else:
            self.solver_name = solver_name
            print("Solver not in library, correct optimization not garanteed")

        # setup interface
        if solver_interface in INTERFACE_LIBRARY:
            self.solver_interface = solver_interface
        else:
            print("Solver interface not in library, correct optimization not garanteed")

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

    def run_optimization(self, model_instance):
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
        timer = time_printer(programm_step='Single optimization run')

        results = self.solver.solve(model_instance, tee=True)
        gap = (
            (
                results["Problem"][0]["Upper bound"]
                - results["Problem"][0]["Lower bound"]
            )
            / results["Problem"][0]["Upper bound"]
        ) * 100
        timer = time_printer(timer, 'Single optimization run')
        model_output = ModelOutput(model_instance, self.solver_name, timer, gap)
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

        if options is not None:
            for i, j in options.items():
                solver.options[i] = j
        else:
            pass
        return solver
