#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 15:12:24 2022

@author: philippkenkel
"""
import copy
import datetime
# import os
# import sys
# import pickle5 as pic5
import time

import cloudpickle as pic
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from scipy.spatial import cKDTree
from tabulate import tabulate
#from basic_analyzer import BasicModelAnalyzer
from outdoor.outdoor_core.output_classes.analyzers.basic_analyzer import BasicModelAnalyzer



class AdvancedMultiModelAnalyzer(BasicModelAnalyzer):
    """
    Class description
    -----------------
    The MultiModelOutput classes are the results from multiple optimization runs
    such as sensitivity analysis and multi-criteria optimization. In order to
    analyse the case specific data structure this class icnludes several methods.

    These methods include:
        - create_mcda_table()           --> Usable for MCDAOptimizer runs
        - create_sensitivity_graph()    --> Usable for SensitivityOptimizer
        - create_crossparameter_graph() --> Usable for TwoWaySensitivityOptimizer runs
        - plot_parero_front()            --> Usable for MultiObjectiveOptimizer runs

    """

    def __init__(self, model_output=None):
        super().__init__(model_output)
        #self.model_output = copy.deepcopy(model_output)
        self._case_time = datetime.datetime.now()

    # INPUT METHODS
    # -------------

    def set_model_output(self, model_output):
        """
        Parameters
        ----------
        model_output : MultiModelOutput Class
            Store MultiModelOutput Object in ModelAnalyzer

        """
        self.model_output = copy.deepcopy(model_output)

    def load_model_output(self, path):
        """
        Parameters
        ----------
        path : String
            Path string from where to load pickle file

        """

        timer = time.time()

        with open(path, "rb") as file:
            self.model_output = pic.load(file)

        timer = time.time() - timer
        print(f"File loading time was {timer} seconds")

    # ANALYSIS METHODS FOR MCDA MODES
    # -------------------------------

    def _collect_mcda_data(self, table_type="values"):
        """
        Parameters
        ----------
        table_type : STRING, optional
            Defines which data should be collected for table
            Default: 'values'
            Options: 'scores', 'relative closeness'

        Returns
        -------
        data : DICT
            Dictionary of collected data for tabulate

        """

        data = dict()
        r_npc = round(self.model_output._multi_criteria_data["NPC"][1], 2)
        r_npe = round(self.model_output._multi_criteria_data["NPE"][1], 2)
        r_fwd = round(self.model_output._multi_criteria_data["FWD"][1], 2)

        if table_type == "values":

            data["Ref"] = [r_npc, r_npe, r_fwd]

            for i, j in self.model_output._results_data.items():
                npc = round(j._data["NPC"], 2)
                npe = round(j._data["NPE"], 2)
                fwd = round(j._data["NPFWD"], 2)
                data[i] = [npc, npe, fwd]

        else:

            npc_list = [r_npc]
            npe_list = [r_npe]
            fwd_list = [r_fwd]

            for i in self.model_output._results_data.values():
                npc_list.append(i._data["NPC"])
                npe_list.append(i._data["NPE"])
                fwd_list.append(i._data["NPFWD"])

            # Check best and worst values for NPC, NPE and FWD
            best_npc = min(npc_list)
            worst_npc = max(npc_list)
            best_npe = min(npe_list)
            worst_npe = max(npe_list)
            best_fwd = min(fwd_list)
            worst_fwd = max(fwd_list)
            r_npc = round((worst_npc - r_npc) / (worst_npc - best_npc), 3)
            r_npe = round((worst_npe - r_npe) / (worst_npe - best_npe), 3)
            r_fwd = round((worst_fwd - r_fwd) / (worst_fwd - best_fwd), 3)
            npc_weight = self.model_output._multi_criteria_data["NPC"][0]
            npe_weight = self.model_output._multi_criteria_data["NPE"][0]
            fwd_weight = self.model_output._multi_criteria_data["FWD"][0]

            # Prepare Reference values
            if table_type == "scores":
                data["Ref"] = [r_npc, r_npe, r_fwd]
            else:
                data["Ref"] = [
                    r_npc * npc_weight,
                    r_npe * npe_weight,
                    r_fwd * fwd_weight,
                ]

            # Prepare calculated values
            for i, j in self.model_output._results_data.items():
                npc = round((worst_npc - j._data["NPC"]) / (worst_npc - best_npc), 3)
                npe = round((worst_npe - j._data["NPE"]) / (worst_npe - best_npe), 3)
                fwd = round((worst_fwd - j._data["NPFWD"]) / (worst_fwd - best_fwd), 3)

                if table_type == "scores":

                    data[i] = [npc, npe, fwd]

                else:

                    data[i] = [npc * npc_weight, npe * npe_weight, fwd * fwd_weight]

            if table_type == "relative closeness":

                C = {}

                for i, j in data.items():
                    d_p = (
                        abs(npc_weight - j[0])
                        + abs(npe_weight - j[1])
                        + abs(fwd_weight - j[2])
                    )
                    d_n = abs(0 - j[0]) + abs(0 - j[1]) + abs(0 - j[2])
                    C[i] = [round(d_n / (d_p + d_n), 5)]

                data = C

        return data

    def create_mcda_table(self, table_type="values"):
        """
        Parameters
        ----------
        table_type : String, optional default is 'values', permitted values are:
                'scores' and 'relative closeness'
            DESCRIPTION: Defines which values of the MCDA run should be printed
                in a table

        Description
        -------
        Collects the MCDA data and tabulates them in the console

        """

        if self.model_output._optimization_mode == "Multi-criteria optimization":

            data = self._collect_mcda_data(table_type)
            index = ["NPC", "NPE", "FWD"]

            if table_type != "relative closeness":
                table = tabulate(data, headers="keys", showindex=index)
            else:
                table = tabulate(data, headers="keys")

            print("")
            print(table_type)
            print("--------")
            print(table)
            print("")
        else:
            print(
                "MCDA table representation is only supported for optimization \
                  mode Multi-criteria optimization"
            )

    # ANALYSIS METHODS FOR SENSITIVTY MODE
    # ------------------------------------

    def _collect_sensi_data(self, objectiveParameter):
        """

        Returns
        -------
        data : DICTIONARY
            Returns data dictionary for sensitivity graphs

        """

        data = {}

        for i, j in self.model_output._results_data.items():

            if len(i) > 2:
                titel = i[0:2]
            else:
                titel = i[0]

            if titel not in data.keys():
                data[titel] = [[], []]
                x = i[-1]
                y = round(j._data[objectiveParameter], 2)
                data[titel][0].append(x)
                data[titel][1].append(y)
            else:
                x = i[-1]
                y = round(j._data[objectiveParameter], 2)
                data[titel][0].append(x)
                data[titel][1].append(y)

        return data

    def create_sensitivity_graph(self, savePath=None, saveName=None, figureMode='subplot', xlable=None):
        """
        Returns
        -------
        fig : MATPLOTLIB FIGURE

        Description
        -----------
        Collects data for sensitivity graph by calling _collect_sensi_data
        and creates matplotlib graph to display.

        Parameters
        ----------
        savePath : str, optional
            The path where to save the figure.
        figureMode : str, optional
            The mode of the figure. Can be 'subplot' for individual subplots for each dataset,
            or 'single' for all datasets plotted on a single graph.
        """

        if self.model_output._optimization_mode != "sensitivity":
            print("Sensitivity graph presentation only available for Sensitivity analysis mode")
            return

        ylabDict = {"NPC": "Net production costs in (€/t)",
                    "NPE": "Net production emmisions in (t-CO2/t)",
                    "NPFWD": "Fresh Water usage in (t-H2O/t)",
                    "EBIT": " Earnings Before Income Tax (M€/y)"}

        objectiveName = self.model_output._meta_data["Objective Function"]

        ylab = ylabDict[objectiveName]

        data = self._collect_sensi_data(objectiveParameter=objectiveName)

        if figureMode == 'subplot':
            fig = plt.figure()
            for count, (title, (x_vals, y_vals)) in enumerate(data.items(), start=1):
                if max(y_vals) == min(y_vals):
                    # skip the graph if all values are the same
                    continue
                else:
                    ax = fig.add_subplot(len(data), 1, count)
                    ax.plot(x_vals, y_vals, linestyle="--", marker="o")
                    ax.set_xlabel(title)
                    ax.set_ylabel(ylab)

        elif figureMode == 'single':
            fig, ax = plt.subplots()  # Create a single figure and axes for plotting
            for title, (x_vals, y_vals) in data.items():
                if max(y_vals) == min(y_vals):
                    # skip the graph if all values are the same
                    continue
                else:
                    if len(data) > 1:
                        x_discreet = list(range(len(x_vals)))
                        ax.plot(x_discreet, y_vals, linestyle="--", marker="o", label=title)
                        # plt.figure(figsize=(8, 6))
                        # plt.plot(product_price, ebit, marker='o', linestyle='-', color='b')
                        ax.axhline(0, color='gray', linestyle='--')
                    else:
                        ax.plot(x_vals, y_vals, linestyle="--", marker="o", label=title)
                    if xlable:
                        ax.set_xlabel(xlable)
                    else:
                        ax.set_xlabel("Discritised Parameter Values")

                    ax.set_ylabel(ylab)

            # Place the legend outside the plot on the right side
            # ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

            plt.tight_layout()  # Adjust the layout to make room for the legend
        else:
            raise ValueError("Invalid figureMode. Choose either 'subplot' or 'single'.")

        fig.tight_layout()

        if savePath is not None:
            if saveName is not None:
                saveString = savePath + "/" + saveName + ".png"
            else:
                saveString = savePath + "/" + "sensitivity_graph_" + self._case_time[0:13] + ".png"

            fig.savefig(saveString)

        return fig


    # DESIGN SCREENING ALGORITHM METHODS
    # ---------------------------------

    def _get_contour_numbers(self, process_design, plist):
        """
        Parameters
        ----------
        process_design : ProcessResults File
            DESCRIPTION.
        plist : List
           List with number of processes to be checked if chosen

        Returns
        -------
        number : Int
            Number associated with the chosen technology combination
        string : String
            Name of the technology combination

        Description
        -----------
        Takes a ProcessResults object and checks for all chosen technologies if
        the required technologies (in plist) are chosen in this design.
        Afterwards hands back the identifier for the technology choices and the name.

        """

        # Set-up required variables:
        number = 0
        string_list = list()

        # Retrieve chosen technologies for the current ProcessDesign
        dic = process_design.return_chosen()

        #keysSelectedProcesses = list(dic.keys())

        #sourceFlow = process_design._data['FLOW_SOURCE']
        #processFlows = process_design.results['Mass flows'] #is a dictionary with the mass flows of the processes
        #processesWithFlows = []

        #for key, val in processFlows.items():
        #    if val > 1e-3:
        #        processesWithFlows.append(key[1]) # the second key is the technolgy where flow enters

        #for key, val in sourceFlow.items():
        #    if val > 1e-3:
        #        processesWithFlows.append(key)

        # Check if the chosen processes actually have a mass flow going through them
        #for process in keysSelectedProcesses:
        #    if process not in processesWithFlows:
        #        dic.pop(process, None)



        # Set up the numbers for the colorcontours , depending on number
        # of checkable processes.

        if len(plist) == 2:
            numbers = {plist[0]: 1, plist[1]: 2}

        if len(plist) == 3:
            numbers = {plist[0]: 1, plist[1]: 2, plist[2]: 4}

        if len(plist) == 4:
            numbers = {plist[0]: 1, plist[1]: 2, plist[2]: 4, plist[3]: 8}

        if len(plist) > 4:
            raise ValueError("The number of processes to be checked must be between 2 and 4.")

        # Check which processes are chosen in the current processdesign
        pset = set(plist)
        dset = set(dic.keys())
        cset = pset.intersection(dset)

        # Iterate through the set of chosen and searched processes and safe the
        # according number and process name string

        for i in cset:
            number += numbers[i]
            string_list.append(dic[i])

        string = ' + '.join(string_list)

        return number, string

    def _get_2d_array(self, input_, iterator):
        """


        Parameters
        ----------
        input_ : 1 Dimensional list
        iterator : Int
            Lenth of the x / y axis

        Returns
        -------
        output_ : 2-dimensional numpy array

        Description
        -----------

        Takes a one dimensional list with two dimensional data and converts
        it into a two dimensional numpy array, which is readable for matplotlibs
        imshow graph.
        """

        # Set-up required variables

        list1 = list()
        temp = list()
        count = 0

        # Iterate through the input and produce a 2-dimensional list from it

        for j in input_:
            count += 1
            if count <= iterator:
                temp.append(j)
            else:
                list1.append(temp)
                temp = []
                temp.append(j)
                count = 1

        list1.append(temp)

        # Convert list into numpy array
        output_ = np.array(list1)

        return output_

    def _get_graph_data(self, process_list, cdata):
        """

        Parameters
        ----------
        process_list : List
            Process numbers to be checked.
        cdata : String
            Data to be depicted on the z-axis i.e. the objective function

        Returns
        -------
        X : Numpy array
            x-axis values
        Y : Numpy array
            y-axis values
        Z : Two-dimensional Numpy array
            Net production costs of x and y
        C : Two-dimensional Numpy array
            Map of indentifiers for technology choice of x and y
        label_dict : Dictionary
            Dictionary with labels and identifier numbers

        Description
        -----------

        Iterates through all ProcessDesigns in the MultipleDesign and calls:
            - self._get_contour_numbers
            - self._get_2d_array

        It gets all x and y-axis data from the ProcessResults as well as
        net production costs(NPC), from there it creates the axis and
        two-dimensional Z and C arrays which hold costs and technology choice
        information.

        """

        # Set-up required variables

        label_dict = dict()
        n_list = list()
        x = list()
        y = list()
        z = list()

        # Iterate through all ProcessResults and get x,y,z and c values
        # i is the index of the results
        # j is the results file of that run
        for i, j in self.model_output._results_data.items():

            npc = j._data[cdata]

            if cdata == 'NPE':
                rounder = 4
            else:
                rounder = 0

            rounder = 4
            x.append(i[1])
            y.append(i[3])
            z.append(round(npc, rounder))


            n, s = self._get_contour_numbers(j, process_list)

            if n not in label_dict.keys():
                label_dict[n] = s

            n_list.append(n)

        #print(z)
        iterator = len(set(x))

        # Turn x- and y-axis lists into numpy arrays

        y1 = np.array(list(dict.fromkeys(y)))
        x1 = np.array(list(dict.fromkeys(x)))

        # Produce meshgrid and Z and C for imshow / contour plots

        X, Y = np.meshgrid(x1, y1)

        Z = self._get_2d_array(z, iterator)
        C = self._get_2d_array(n_list, iterator)

        Z = np.transpose(Z)
        C = np.transpose(C)

        return X, Y, Z, C, label_dict

    def create_crossparameter_graph(self, process_list, cdata, xlabel, ylabel, clabel):
        """

        Parameters
        ----------
        process_list : LIST
            List with Process numbers to be checked in algorithm
        xlabel : String
            Label of the x-axis
        ylabel : String
            Label of the y-axis
        clabel : String
            Label of the colorbar

        Description
        -----------
        Creates the screening algorithm figure for two-way sensitivity analysis.
        First collects all data and preprocesses them in the right format.
        Afterwards converts technology choices to numerical grid and
        produces an overlaying contour (for costs) and imshow / heatmap
        (for technology choices)
        """

        cdata_list = ['EBIT', 'NPC', 'NPE', 'NPFWD']

        countour_line_labels = {'NPC':"%1.0f €/MWh",
                                'NPE':"%1.0f t-CO2/MWh",
                                'NPFWD':"%1.0f t-H2O/MWh",
                                'EBIT':"%1.0f M€",}

        if cdata not in cdata_list:
            print('No method or data to depict the demanded value, please chose from')
            print(cdata_list)


        # Define color-palette for usage

        color_palette = [
            "orangered",
            "royalblue",
            "mediumpurple",
            "yellow",
            "orange",
            "indianred",
            "gainsboro",
            "gray",
            "limegreen",
            "tan",
            "mediumseagreen",
            "mediumpurple",
            "mediumturquoise",
            "thistle",
            "indianred",
        ]

        # Define set_axes method for convenience

        def set_axes(x, y):
            x_max = float(np.max(x))
            x_min = float(np.min(x))
            y_max = float(np.max(y))
            y_min = float(np.min(y))

            x_ticks = x[0]
            y_ticks = np.transpose(y)[0]

            for i in range(len(x_ticks)):
                x_ticks[i] = round(x_ticks[i], 0)

            for i in range(len(y_ticks)):
                y_ticks[i] = round(y_ticks[i], 0)

            return x_max, x_min, y_max, y_min, x_ticks, y_ticks

        # Get x,y,z,c, and labels from get_graph_data
        # Get axis data from set_axes method

        x, y, z, c, label_dict = self._get_graph_data(process_list, cdata)
        x_max, x_min, y_max, y_min, x_ticks, y_ticks = set_axes(x, y)

        # Set-up figure
        plt.rcParams["figure.dpi"] = 1200
        plt.rcParams["font.family"] = "Times New Roman"

        fig = plt.figure()

        # Prepare labels for the colorbar

        labels = list()
        col_dict = dict()
        label_items = sorted(label_dict.keys())

        for i in label_items:
            col_dict[i] = color_palette[i - 1]
            labels.append(label_dict[i])

        # Create custom colormap for imshow figure
        cm = matplotlib.colors.ListedColormap([col_dict[t] for t in col_dict.keys()])

        labels = np.array(labels)
        len_lab = len(labels)
        norm_bins = np.sort([*col_dict.keys()]) + 0.5
        norm_bins = np.insert(norm_bins, 0, np.min(norm_bins) - 1.0)

        # Prepare format of the colorbar
        norm = matplotlib.colors.BoundaryNorm(norm_bins, len_lab, clip=True)
        fmt = matplotlib.ticker.FuncFormatter(lambda k, pos: labels[norm(k)])
        diff = norm_bins[1:] - norm_bins[:-1]
        tickz = norm_bins[:-1] + diff / 2

        # Create graph 1: Heatmap of technology choice (c)

        ax = fig.add_subplot(111)

        graph_1 = ax.imshow(
            c,
            cmap=cm,
            norm=norm,
            extent=[x_min, x_max, y_min, y_max],
            interpolation="none",
            origin="lower",
            aspect="auto",
            alpha=1,
        )

        cbar = plt.colorbar(graph_1, format=fmt, ticks=tickz, label=clabel, shrink=1)

        # Create graph 2: Contour levels of NPC (z)

        contour_levels = list(np.linspace(np.min(z) + 5, np.max(z) - 5, 10))

        ax = fig.add_subplot(111)
        # graph_2 = ax.contour(x, y, z, colors="black", levels=contour_levels)
        graph_2 = ax.contour(x, y, z, colors="black")
        ax.clabel(graph_2, fmt=countour_line_labels[cdata], fontsize=8)

        # Set lables of axes

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.show()

    def create_cross_parameter_plot(self, processList, objective, savePath=None, saveName=None,
                                    simpleContour=False, levels=10, xlabel=None, ylabel=None, ecludianDistancePoint=None ):
        """
        This method creates a contour plot with contour lines and background colors corresponding to labels using a custom colormap.
        :param processList: List of process numbers to be checked in the algorithm (e.g., [6000, 410])
        :param objective: The objective function to be plotted on the contour lines (e.g., 'EBIT')
        :param savePath: where to save the plot
        :param saveName: specify the name of the plot
        :param simpleContour: If True, only the contour lines are plotted. If False, the contour lines are plotted on
        top of a filled contour plot representing which products where produced (from process list).
        :param levels: Number of levels for the contour plot
        :param xlabel: Label for the x-axis
        :param ylabel: Label for the y-axis
        :param ecludianDistancePoint: A tuple (x, y, Z) where x and y the coordinates of the point for which the
        distance to the contour line Z should be calculated

        :return: Contour plot with labels and contour lines saved to the specified file path

        """
        x, y, z, c, label_dict = self._get_graph_data(processList, objective)
        c, label_dict = self._reorder_labels(c, label_dict)

        if simpleContour:
            # Create a filled contour plot
            contour_filled = plt.contourf(x, y, z, levels=levels, cmap='viridis')
            # Add contour lines on top of the filled contours
            contour_lines = plt.contour(x, y, z, levels=levels, colors='black')


            # Highlight the zero contour line with extra boldness
            levelHighLightedContor = ecludianDistancePoint[2]
            zero_contour = plt.contour(x, y, z, levels=[levelHighLightedContor], colors='cyan',
                                       linewidths=3)  # Change color and width as needed

            # Label the contour lines with larger fonts
            # Increase font size here
            labels = plt.clabel(contour_lines, inline=False, fontsize=12, fmt='%1.2f M€/y')
            # Adjust label positions
            for label in labels:
                label.set_y(label.get_position()[1] + 0.01)  # Adjust the distance as needed

            # Label for the zero contour, if needed
            zeroLable = plt.clabel(zero_contour, inline=False, fontsize=12, fmt='%1.2f M€/y')
            for lable in zeroLable:
                lable.set_y(lable.get_position()[1] + 0.01)  # Adjust the distance as needed

            # add labels to the axes
            if xlabel:
                plt.xlabel(xlabel)
            if ylabel:
                plt.ylabel(ylabel)

            # find the minimum distance from a point to the 0-level contour
            if ecludianDistancePoint:
                point = (ecludianDistancePoint[0], ecludianDistancePoint[1])
                contour_level = ecludianDistancePoint[2]
                distance, closest_point = self.calculate_min_distance_to_contour(x, y, z, contour_level, point)
                # print in purple color
                print("\033[95m")
                print(f"Distance from point {ecludianDistancePoint} to the 0-level contour: {distance}")
                print(f"Closest point on the contour line: {closest_point}")
                print("\033[0m")

                # add the point and the closest point on the contour line to the plot as a red dot
                plt.plot(point[0], point[1], 'wo', label='Current state of the technology', markersize=10)
                plt.plot(closest_point[0], closest_point[1], 'yo', label='Break Even Point', markersize=10)

            # save the plot to the specified file path
            if savePath:
                if saveName:
                    save_path = f"{savePath}/{saveName}.png"
                else:
                    save_path = f"{savePath}/contour_plot.png"
                plt.savefig(save_path)
                plt.clf()
        else:
            self.plot_contour_with_labels(x, y, z, c, label_dict, savePath, saveName)

    def calculate_min_distance_to_contour(self, x, y, z, contour_level, point):
        """
        Calculate the minimum distance from a point to a specific contour level.

        Parameters:
        - x: 2D array of x-coordinates (meshgrid).
        - y: 2D array of y-coordinates (meshgrid).
        - z: 2D array of z-values (function values over the grid).
        - contour_level: The contour level you are interested in (e.g., 0 for the 0-level contour).
        - point: A tuple representing the (x, y) coordinates of the point.

        Returns:
        - min_distance: The minimum Euclidean distance from the point to the contour line.
        - closest_point: The closest point on the contour line.
        """

        # Create a contour plot but don't display it
        fig, ax = plt.subplots()
        CS = ax.contour(x, y, z, levels=[contour_level])

        # Extract the contour line coordinates from the plot
        contour_paths = CS.collections[0].get_paths()

        contour_points = []

        # Iterate over all paths of the contour line
        for path in contour_paths:
            contour_points.extend(path.vertices)

        # Convert contour points to a numpy array
        contour_points = np.array(contour_points)

        # Create a KDTree for fast nearest-neighbor search
        tree = cKDTree(contour_points)

        # Find the nearest point on the contour line to the given point
        distance, idx = tree.query(point)
        closest_point = contour_points[idx]

        # Close the figure as we don't need to show the plot
        plt.close(fig)

        return distance, closest_point

    def _reorder_labels(self, labels, labelDict):
        """
        I now want the labels to go from 0 to n, where n is the number of unique labels. I have to remap the labels and
        correct/update the label_dict accordingly.
        :param labels: nd.array
        :param label_dict: dict
        :return: New labels and updated label_dict
        """
        uniqueLabels = np.unique(labels)
        newLabels = np.zeros_like(labels)
        for i, label in enumerate(uniqueLabels):
            newLabels[labels == label] = i
            labelDict[i] = labelDict.pop(label)

        # if the value of the label is an empty string, replace it with 'other'
        for key, value in labelDict.items():
            if value == '':
                labelDict[key] = 'other'

        return newLabels, labelDict

    def plot_contour_with_labels(self, x, y, z, labels, label_dict, savePath, saveName):
        """
        Plots a contour plot with contour lines and background colors corresponding to labels using a custom colormap.

        Parameters:
        x (array-like): X-axis values
        y (array-like): Y-axis values
        z (2D array-like): Z-axis values
        labels (2D array-like): Label values corresponding to each (x, y) point
        label_dict (dict): Dictionary mapping labels to their corresponding descriptions
        savePath (str, optional): Path to save the plot
        saveName (str, optional): Name to save the plot file

        Returns:
        None
        """
        plt.figure(figsize=(10, 6))

        # Number of discrete colors needed
        num_colors = len(label_dict.keys())
        # Sample the viridis colormap
        viridis = cm.get_cmap('viridis', num_colors)
        # Extract the colors as a list
        colors = [viridis(i) for i in range(num_colors)]
        # Create a custom colormap from these colors
        custom_cmap = ListedColormap(colors)

        # Create a filled contour plot with colors corresponding to labels
        contourf = plt.contourf(x, y, labels, alpha=0.6, cmap=custom_cmap)

        # Generate a contour plot with only lines
        contour = plt.contour(x, y, z, colors='black')

        # Add labels to the contour lines
        #plt.clabel(contour, inline=True, fontsize=8)
        plt.clabel(contour, inline=True, fontsize=10, fmt='%1.1f', colors='black')

        # Get the axis labels
        xLabel = list(self.model_output._results_data.keys())[0][0]
        yLabel = list(self.model_output._results_data.keys())[0][2]
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)

        # Create a legend
        legend_elements = [Patch(facecolor=colors[i], edgecolor='black', label=label) for i, label in
                           enumerate(label_dict.values())]
        plt.legend(handles=legend_elements, title='Products', bbox_to_anchor=(1.05, 1), loc='upper left')

        # Adjust layout to fit everything
        plt.tight_layout()

        # Save the plot to the specified file path
        if savePath:
            if saveName:
                save_path = f"{savePath}/{saveName}.png"
            else:
                save_path = f"{savePath}/contour_plot.png"
            plt.savefig(save_path)

        # Show the plot
        # plt.show()


    # METHODES FOR WAIT AND SEE ANALYSIS
    # ---------------------------------
    def plot_scenario_analysis(self, variableName=None, path=None, saveName=None, showPlot=False, flowThreshold=1e-5, savePlot=True):
        """
        This method creates a figure of the different possible design spaces for the wait and see analysis.
        the graph are box plots where each box represents the distribution of the objective function for a given flow
        sheet design.

        :return:
        """
        permittedModes = ["wait and see",
                          "here and now"]

        if self.model_output._optimization_mode not in permittedModes:
            ValueError("Scenario analysis methode is only available for 'wait and see' analysis.")

        flowsheetDict, flowsheetDictExtra = self._get_flow_sheet_designs(threshold=flowThreshold)

        if variableName is None:
            if isinstance(self.model_output._results_data['sc1'], classmethod):
                variableName = self.model_output._results_data['sc1']._data['ObjectiveFunctionName']
            else:
                variableName = self.model_output._results_data['sc1']['ObjectiveFunctionName']

            # print in orange
            print('')
            self._print_warning()
            print(f"No variable name was provided for the method plot_scenario_analysis.\n "
                  f"Using the objective function {variableName}.\n")

        boxPlotData = self._get_distribution_variable(variableName, flowsheetDict)
        #percentageOccurence = {key: len(value) / len(self.model_output._results_data) for key, value in boxPlotData.items()}

        xTickLabels = self._identify_products(flowsheetDict)

        # Create the box plot
        fig, ax = plt.subplots(figsize=(16, 12))  # Width, Height in inches
        ax.boxplot(boxPlotData.values())
        ax.set_xticklabels(xTickLabels)
        ax.set_ylabel(variableName)
        ax.set_title(f"Distribution of {variableName} per flow sheet design")

        # show the plot
        if showPlot:
            plt.show()

        # save the plot
        if path:
            if saveName:
                save_path = f"{path}/{saveName}.png"
            else:
                save_path = f"{path}/scenario_analysis.png"

            if savePlot:
                fig.savefig(save_path)

        return plt, flowsheetDictExtra, boxPlotData

    def _get_distribution_variable(self, variable, flowsheetDict):
        """
        Returns the distribution of a specifed variable for the different scenarios with the same
        flow sheet design.

        :param variable: str
            The variable for which the distribution should be calculated.
        :param flowsheetDict: dict
            A dictionary with the flow sheet design as key and the data of the different scenarios as value.
        :return: dict
            The distribution of the specified variable per flow sheet design.
        """

        variableDistribution = {} # Dictionary to store the distribution of the variable per flow sheet design
        for key, listData in flowsheetDict.items():
            collectVariable = []
            for data in listData:
                try:
                    collectVariable.append(data[variable])
                except:
                    ValueError(f"Variable {variable} not found in the data.")
            variableDistribution[key] = collectVariable

        return variableDistribution

    def _get_flow_sheet_designs(self, threshold=1e-5):
        """
        Returns a dictionary with the flow sheet design as key and the data of the different scenarios as value with
        that flow sheet as a design.

        :return: flowsheetDict: dict
            A dictionary with the flow sheet design as key and the data of the different scenarios as value.
        flowSheetDictExtra: dict
            A dictionary with the flow sheet design as key and the {scenario:data} as value.
        """
        # Get the data from the model output
        dataAllScenarios = self.model_output._results_data

        flowsheetDict = {}
        flowsheetDictExtra = {}
        for scenario in dataAllScenarios:
            # depending on the structure of the data, get the data (depends on how it was loaded from the pickle file)
            if hasattr(dataAllScenarios[scenario], '_data'):
                dataScenario = dataAllScenarios[scenario]._data
            else:
                dataScenario = dataAllScenarios[scenario]

            flowsheet = self.model_output.return_chosen(dataScenario, threshold=threshold)  # Get the chosen technologies for each scenario
            keyFlowSheet = tuple(flowsheet.items())

            # Check if the flowsheet is already in the dictionary
            if keyFlowSheet not in flowsheetDict:
                flowsheetDict[keyFlowSheet] = []
                flowsheetDictExtra[keyFlowSheet] = {}

            # Append the data to the dictionary with the flow sheet as key
            flowsheetDict[keyFlowSheet].append(dataScenario)
            flowsheetDictExtra[keyFlowSheet].update({scenario: dataScenario})

        return flowsheetDict, flowsheetDictExtra

    def _identify_products(self, flowsheetDict):
        """
        Returns a list with the products for each flow sheet design.
        :param flowsheetDict: dict
        :return: productsPerFlowsheet: list
        """
        if hasattr(self.model_output._results_data['sc1'], '_data'):
            productIDs = self.model_output._results_data['sc1']._data['U_PP']
            generatorIDs = tuple(set(self.model_output._results_data['sc1']._data['U_TUR'] +
                                    self.model_output._results_data['sc1']._data['U_FUR']))
        else:
            productIDs = self.model_output._results_data['sc1']['U_PP']
            generatorIDs = tuple(set(self.model_output._results_data['sc1']['U_TUR'] +
                                    self.model_output._results_data['sc1']['U_FUR']))

        # productIDs = self.model_output._results_data['sc1']._data['U_PP']
        # generatorIDs = tuple(set(self.model_output._results_data['sc1']._data['U_TUR'] +
        #                          self.model_output._results_data['sc1']._data['U_FUR']))

        productIDs = productIDs + generatorIDs

        productsPerFlowsheet = []
        for flowsheet in flowsheetDict.keys():
            tupleProducts = ()
            for (key1,key2) in flowsheet:
                if key1 in productIDs:
                    tupleProducts = tupleProducts + (key2,)

            productsPerFlowsheet.append(tupleProducts)

        return productsPerFlowsheet

    def _print_warning(self):
        orange_color = "\033[33m"
        reset_color = "\033[0m"
        print(f"{orange_color}-------WARNING-------{reset_color}")


    def plot_pareto_front(self, path, saveName, flowTreshold=1e-5):
        """
        Plot the pareto front of the multi-objective optimization, the dots have different colors depending on the
        flow sheet design. The x-axis is the first objective function and the y-axis is the second objective function.
        :return:
        """

        data = self.model_output._results_data
        objectiveFunctionName1 = self.model_output.multi_data['objective1']
        objectiveFunctionName2 = self.model_output.multi_data['objective2']

        x = []
        y = []
        colors = []
        color_map = {}
        color_index = 0

        for sc in data:
            scData = data[sc]._data
            flowSheet = self.model_output.return_chosen(scData, flowTreshold)
            flowSheetTuple = tuple(flowSheet.items())

            if flowSheetTuple not in color_map:
                color_map[flowSheetTuple] = color_index
                color_index += 1

            x.append(scData[objectiveFunctionName1])
            y.append(scData[objectiveFunctionName2])
            colors.append(color_map[flowSheetTuple])

        # Normalize colors to the range [0, 1]
        norm_colors = np.array(colors) / max(colors)

        plt.scatter(x, y, c=norm_colors, cmap='viridis')
        plt.xlabel(objectiveFunctionName1)
        plt.ylabel(objectiveFunctionName2)

        # save the plot
        if saveName:
            if 'png' not in saveName:
                savePath = f"{path}/{saveName}.png"
            else:
                savePath = f"{path}/{saveName}"
        else:
            savePath = f"{path}/pareto_front.png"
        plt.savefig(savePath)

    def create_all_flowsheets(self, path=None, saveName=None):
        """
        This methode finds the different flow sheet designs of the multi objective optimisation and returns
        a png of each flow sheet design,

        :param flowThreshold: float cut off the mass flow of the flow sheet design
        :return:
        """
        flowTreshold = 1e-5
        data = self.model_output._results_data
        designDict = {}
        for scenario in data:
            scData = data[scenario]._data
            flowSheet = self.model_output.return_chosen(scData, flowTreshold)
            flowSheetTuple = tuple(flowSheet.items())

            if flowSheetTuple not in designDict:
                designDict[flowSheetTuple] = scenario

        # make and save the flow sheet designs
        if not saveName:
            saveName = 'Flowsheet Design '

        for i, scenario in enumerate(designDict.values()):
            dataScenario = data[scenario]._data
            saveName = saveName + str(i)
            self.create_flowsheet(path=path, saveName=saveName, dataScenario=dataScenario)
