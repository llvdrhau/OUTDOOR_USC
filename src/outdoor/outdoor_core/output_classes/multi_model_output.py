#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 15:26:08 2021

@author: philippkenkel
"""

from pyomo.environ import value
from tabulate import tabulate
import os
import datetime
import cloudpickle as pic
from src.outdoor.outdoor_core.output_classes.model_output import ModelOutput
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression


class MultiModelOutput(ModelOutput):

    """
    Class description
    ----------------

    This class is the main output class for multi-run such as sensitivity, cross senitivity or multi-criteria
    optimization. It includes the case data such as used solver, calculation time, meta data etc.

    It also includes methods to
        - fill data into its own structure from the given pyomo model instance
        - Save data as .txt-file
        - Save the output as pickle file
        - Collect main results and display them in the console


    """

    def __init__(self,
                 model_instance = None,
                optimization_mode = None, # 'wait and see'
                solver_name = None,
                run_time = None,
                gap = None,
                dataFiles = None,):

        # initiate the parent class
        super().__init__(model_instance, optimization_mode, solver_name, run_time, gap)

        self._total_run_time = None
        self._case_time = None
        self._results_data = {}
        self._multi_criteria_data = None
        self._sensitivity_data = None
        self._optimization_mode_set = {
            "sensitivity",
            "multi-objective",
            "cross-parameter sensitivity",
            "wait and see",
        }

        if optimization_mode in self._optimization_mode_set:
            self._optimization_mode = optimization_mode
        else:
            Warning("Optimization mode not supported")

        self._meta_data = dict()

        # fill the data files of the different scenarios
        self._dataFiles = dataFiles


    def add_process(self, index, process_results):
        """
        Parameters
        ----------
        index : String or value
            Identifier for the single-run ModelOutput
        process_results : ModelOutput
            Single-run ModelOutput to be saved

        Description
        -------
        Adds a single-run ModelOutput to the MultiModelOutput data-file

        """
        self._results_data[index] = process_results

    def set_multi_criteria_data(self, data):
        """
        Parameters
        ----------
        data : DICT
            Data dictionary with MCDA data including:
                Objectives, Weighting and Reference values

        """
        self._multi_criteria_data = data

    def set_sensitivity_data(self, data):
        """
        Parameters
        ----------
        data : DICT
            Data dictionary for sensitivity run including:
                Sensitive parameter-names and values
        """
        self._sensitivity_data = data

    def fill_information(self, total_run_time):
        """
        Parameters
        ----------
        total_run_time : FLOAT
            The total run time of the overall Multi-run optimization.
            Is calculated and returned automatically by the Optimizer

        Description
        -----------
        Saves total run times of multi-run, also checks for current date time
        to save date-time as identifier for the run.

        """
        self._total_run_time = total_run_time
        self._case_time = str(datetime.datetime.now())

        self._meta_data["Optimization mode"] = self._optimization_mode

        if self._optimization_mode == "Multi-criteria optimization":
            self._meta_data["Optimization mode data"] = self._multi_criteria_data
        else:
            self._meta_data["Optimization mode data"] = self._sensitivity_data

        self._meta_data["Identifier"] = str(datetime.datetime.now())[0:19]
        self._meta_data["Total run time"] = total_run_time

        # get the objective function
        firstKey = list(self._results_data.keys())[0]
        resultsFirstRun = self._results_data[firstKey]
        Objective = resultsFirstRun._data['Objective Function']
        self._meta_data["Objective Function"] = Objective

    def _collect_results(self):
        results = dict()

        for i, j in self._results_data.items():
            results[i] = j._collect_results()

        return results

    def print_results(self):

        for i, j in self._results_data.items():
            print("")
            print(f"Identifier of Single run:{i}")
            j.print_results()

    def get_results(self, pprint=True, savePath=None, saveName=None):
        results = dict()

        for i, j in self._results_data.items():
            j._collect_results()
            dataHolder = j.results
            results[i] = dataHolder

            if pprint is True:
                j._print_results(dataHolder)

        if savePath is not None:
            if not os.path.exists(savePath):
                os.makedirs(savePath)
            if saveName is not None:
                save = savePath + "/" + saveName + self._case_time[0:13] + ".txt"
            else:
                save = savePath + "/" + "basic_results_file" + self._case_time[0:13] + ".txt"

            self._save_results(results, save)

    def _save_results(self, data, path):
        with open(path, encoding="utf-8", mode="w") as f:

            f.write("\n")
            f.write(f"Run mode: {self._optimization_mode} \n")
            f.write(f"Total run time {self._total_run_time} \n \n \n")

            for i, j in data.items():

                f.write(f"Identifier of Single run: {i} \n")

                for k, t in j.items():
                    table = tabulate(t.items())
                    f.write("\n")
                    f.write(k)
                    f.write("-------- \n")
                    f.write(table)
                    f.write("\n")
                    f.write("\n \n")

                print("")

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

        path = path + "/" + "input_file" + self._case_time + "data.txt"

        with open(path, encoding="utf-8", mode="w") as f:

            for i, j in self._results_data.items():
                f.write(f"Identifier of single run: {i} \n")
                all_data = j._data

                for k, t in all_data.items():
                    f.write(f"{k}: {t} \n \n")

                f.write(" ----------------- \n \n")


  # Calculate the SRC for the sensitivity analysis ------------------------------------------------
    # ----------------------------------------------------------------------------------------------
    def calculate_SRC(self):
        """
        Calculates the standerdized regression coefficients SRC of the wait and see analysis
        :return:
        """


        if self._optimization_mode != "wait and see":
            ValueError("Scenario analysis methode is only available for 'wait and see' analysis.")

        # return the objective function name of the simulations
        objectiveFunctionName = self._results_data['sc1']._data['ObjectiveFunctionName']
        # objectiveFunctionName2 = self._objective_function

        # retrive uncetainty matrix
        uncertaintyMatrix = self.uncertaintyMatrix

        # turn uncertainty matrix into numpy array
        parameterArray = np.array(uncertaintyMatrix)


        # get the results of the wait and see analysis
        objectiveFunctionList = []
        for i, j in self._results_data.items():
            objectiveFunctionList.append(j._data[objectiveFunctionName])

        # turn into numpy array
        results = np.array(objectiveFunctionList)
        results = results.reshape(-1, 1)


        # Standardize data using sklearn (so-called mean-centred sigma-scaling)
        scaler = StandardScaler()
        parametersStandardized = scaler.fit_transform(parameterArray)
        resultsStandardized = scaler.fit_transform(results)

        # Perform regression analysis
        reg = LinearRegression()
        reg.fit(parametersStandardized, resultsStandardized)
        #reg.fit(parameterArray, results)

        # Obtain SRCs
        srcs = reg.coef_

        srcDict = {}
        squareSumSRC = 0
        for i, parameterName in enumerate(uncertaintyMatrix.columns):
            # standerdiseCoef = np.std(parameterArray[:, i]) / np.std(results)
            standerdiseCoef = 1
            src = srcs[0, i] * standerdiseCoef
            srcDict[parameterName] = src
            squareSumSRC += src**2
            print(f"SRC for parameter {parameterName}: {src}")


        # Obtain R-squared value
        RSquared = reg.score(parametersStandardized, resultsStandardized)

        # #plot y_reg vs y
        # get the results from the regression model
        # y_reg = reg.predict(parametersStandardized)
        # y_reg = reg.predict(parameterArray)
        # import matplotlib.pyplot as plt
        # plt.plot(results, y_reg, 'o')
        # plt.xlabel('True values')
        # plt.ylabel('Predicted values')
        # # plot diagonal line
        # plt.plot([np.min(results), np.max(results)], [np.min(results), np.max(results)], 'r-')
        # plt.show()

        #
        # for i, y in enumerate(objectiveFunctionList):
        #     test = (y_reg[i, 0] - yAverage)**2 / (y - yAverage)**2
        #     RSquared += (y_reg[i, 0] - yAverage)**2 / (y - yAverage)**2


        print('Sum of SRC squared: ', squareSumSRC)
        print('R squared: ', RSquared)
        self.SRC = srcDict

        sorted_src = dict(sorted(srcDict.items(), key=lambda item: item[1], reverse=True))
        print(sorted_src)






