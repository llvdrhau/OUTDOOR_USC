""""
This class collects all parameters and sets for the 2 stage stochastic problem with recourse.
author: Lucas Van der Hauwaert
date: october 2023

Class description
        -----------------

        This Class prepares the data for the stochastic problem.

        This class adds parameters which define
            - The number of scenarios
            - The parameters for each scenario
            - The probability of each scenario
            - The dataFrame of the uncertain parameters and their values for each scenario
"""

import pandas as pd
import itertools
import ast
from numpy import isnan
#from itertools import product

class StochasticObject():
    def __init__(self):
        self.NumberOfScenarios = None
        self.LevelList = []
        self.ScenarioProbabilities = []
        self.AffectedUnitNumbers = []
        self.ScenarioNames = []

        self.GammaDict = {}
        self.XiDict = {}
        self.PhiDict = {}
        self.ThetaDict = {}
        self.GeneralDict = {}
        self.GroupDict = {}
        self.level = 0
        self.PhiComponentsList = []
        self.LableDict = {'phi': {},
                          'theta': {},
                          'myu': {},
                          'gamma': {},
                          'xi': {},
                          'ProductPrice': {},
                          'materialcosts': {},
                          'Decimal_numbers': {}
                          }


    def _set_general_data(self, GeneralDataFrame, customLevelDataFrame):

        self.level = GeneralDataFrame.iloc[0,1]

        if isinstance(self.level, str):
            if self.level == 'custom':
                level_list = self._set_custom_levels(customLevelDataFrame)
            else:
                raise ValueError("The level {} is not supported".format(self.level))
        else:
            if self.level == 2:
                level_list = [1, -1]
            elif self.level == 3:
                level_list = [1, 0, -1]
            else:
                raise ValueError("The level of the stochastic problem is not supported please select 2 or 3")

        self.LevelList = level_list

        self.ProbabilitySettings = GeneralDataFrame.iloc[1, 1]


    def _set_phi_exclusion_list(self, phiExclusionDataFrame):
        """
        This function makes a list of tuples which contain the unit number and the components of the excluded elements
        when composition changes
        :param phiExclusionDataFrame:
        :return:
        """

        # make a dictionary from the dataframe, the keys are the unit numbers in the first column. the items should be a list of all the strings in the row
        phiExclusionDict = {}
        # loop for the first colunm of the dataframe
        availableSources = phiExclusionDataFrame.iloc[:,0].dropna()
        exclusionList = []
        for i, source in enumerate(availableSources):
            sourceRow = phiExclusionDataFrame.iloc[i,1:].dropna()
            for component in sourceRow:
                exclusionList.append((source, component))

            if source is not None:
                # if the value in the dataframe is not nan add it to the list
                row = phiExclusionDataFrame.loc[source]
                row = row[1:]
                # drop Nan
                row = row.dropna()
                # make a list from the row
                row = row.tolist()
                phiExclusionDict[source] = row

        self.PhiExclusionDict = phiExclusionDict
        self.PhiExclusionList = exclusionList

    def add_probability_dict(self, paramerterName, parameterData):
        """
        This function adds the probability dictionary to the GeneralDict
        :param paramerterName: (str)
        :param parameterData: (series)
        :return:
        """
        # make a list from the row
        #parameterData = parameterData.tolist()
        parameterDataProbaility = parameterData[('Probabilities')]

        if isinstance(parameterDataProbaility, str):
            try:
                probabilityList = ast.literal_eval(parameterDataProbaility)
            except ValueError:
                raise ValueError("The probabilities are not a list in parameter {} \n"
                                 "make sure you write in the following format: '[x, y, z]' ".format(paramerterName))

        elif isnan(parameterDataProbaility):
            probabilityList = [1 / len(self.LevelList) for i in self.LevelList]

        else:
            raise ValueError("The probabilities are not a list in parameter {} \n"
                             "make sure you write in the following format: '[x, y, z]' ".format(paramerterName))


        if len(probabilityList) != len(self.LevelList):
            raise ValueError("The number of probabilities is not equal to the number of levels in "
                             "parameter {}".format(paramerterName))

        if round(sum(probabilityList)) != 1:
            raise ValueError("The sum of the probabilities is not equal to 1 in parameter {}".format(paramerterName))

        # make a dictionary from the row
        probabilityDict = {self.LevelList[i]: odd for i, odd in enumerate(probabilityList)}
        # add the probability dictionary to the GeneralDict
        self.GeneralDict[paramerterName]["ProbabilityDict"] = probabilityDict


    def _set_general_dict(self, dataFrame, parameterName):
        """"
        This function creates dictionaries so the characteristics of each uncertain parameter can be accessed easily
        """
        # preprocess the dataframe
        dataFrame = make_first_row_column_names(dataFrame)
        nr = 0
        # Iterate over rows using iterrows()
        for index, row in dataFrame.iterrows():
            # if the first element in the row is an integer add the row to the dictionary
            if isinstance(row.iloc[0], int):
                unitNr = row.iloc[0]
                self.AffectedUnitNumbers.append(unitNr)
                nr += 1
                keyName = '{}_{}'.format(parameterName, nr)
                self.GeneralDict[keyName] = row[0:].to_dict()

                # add the probability dictionary to the GeneralDict if the probability setting is custom
                if self.ProbabilitySettings == 'custom':
                    self.add_probability_dict(paramerterName=keyName, parameterData=row)

                if parameterName =='gamma':
                    component = row['Component']
                    reactionNr = row['Reaction-number']
                    nrComponentTuple = (unitNr, component, reactionNr)

                elif parameterName == 'theta': # unfortuant gimmik, because the index is reversed for the theta data
                    component = row['Component']
                    reactionNr = row['Reaction-number']
                    nrComponentTuple = (unitNr, (reactionNr, component))

                elif parameterName == 'myu':
                    component = row['Component']
                    targetUnit = row['Target unit']
                    nrComponentTuple = (unitNr, (targetUnit, component))

                elif parameterName == 'phi' or parameterName == 'xi':
                    component = row['Component']
                    nrComponentTuple = (unitNr, component)

                elif parameterName == 'ProductPrice' or parameterName == 'materialcosts' or parameterName == 'Decimal_numbers':
                    nrComponentTuple = (unitNr)

                else:
                    raise ValueError("The parameter {} is not supported".format(parameterName))

                self.LableDict[parameterName][nrComponentTuple] = keyName


    def _set_group_dict(self):
        """
        This function makes a dataframe from GereralDict where the first column are the keys of GeneralDict and the
        second column is the value for 'Group-nr' in the value of GeneralDict (which is a dictionary)
        """
        # make a dataframe from GeneralDict
        df = pd.DataFrame.from_dict(self.GeneralDict)
        # transpose the dataframe
        df = df.transpose()
        try:
            counter = max(df['Group-nr.'])
        except:
            counter = 0

        # iterate over the rows of the dataframe and add the group number to the column 'Group-nr.'
        # if the value of Group-nr. is nan
        for index, row in df.iterrows():
            if pd.isnull(row['Group-nr.']):
                counter += 1
                df.loc[index, 'Group-nr.'] = counter


        grouped = df.groupby('Group-nr.')
        self.GroupDict = grouped.groups
        self.NumberOfScenarios = len(self.LevelList) ** len(self.GroupDict)




    def _set_custom_levels(self, customLevelDataFrame):
        """
        makes a list from the custom levels (which is a Series)
        :param customLevelDataFrame:
        :return: list of custom levels (list)
        """

        # need to delete the nan values in the dataframe
        customLevelDataFrame = customLevelDataFrame.dropna()
        customLevelDataFrame = customLevelDataFrame.reset_index(drop=True)

        # make a list from the custom levels
        customLevelList = customLevelDataFrame.iloc[1:,0].tolist()

        return customLevelList


    def make_scenario_dataframe(self):
        """
        This function makes a dataframe with all the scenarios and their values for each uncertain parameter
        :return: self.UncertaintyMatrix (dataframe)
        """
        # Define your list and values for n and r
        my_list = self.LevelList
        # Number of variables
        m = len(self.GroupDict)
        # Number of states each variable can take
        r = self.level
        # Generating all states each variable can take
        states = [my_list for _ in range(m)]
        # Getting the cartesian product of states
        combinations = list(itertools.product(*states))
        # Converting combinations to a DataFrame
        df = pd.DataFrame(combinations, columns=[f'Variable_{i + 1}' for i in range(m)])

        nr = 1
        for key, value in self.GroupDict.items():
            referenceNameGroup = None
            column_index = None
            if len(value) > 1:

                # find the reference name in the group
                for i in value:
                    correlation = self.GeneralDict[i]['Correlation']
                    # find the reference name in the group
                    if correlation == 'reference': # the column name on position pos-1 becomes i
                        df.rename(columns={'Variable_{}'.format(nr): i}, inplace=True)
                        nr += 1
                        referenceNameGroup = i
                        column_index = df.columns.get_loc(referenceNameGroup)

                # error if no reference name is found for group i
                if referenceNameGroup is None or column_index is None:
                    raise ValueError("There is no reference variable in Group {}".format(key))

                # add the additional columns to the df which are correlated to the reference variable
                for varName in value:
                    correlation = self.GeneralDict[varName]['Correlation']
                    if correlation == 'equal':
                        df.insert(column_index, varName, df[referenceNameGroup])
                        column_index += 1
                    elif correlation == 'opposite':
                        df.insert(column_index, varName, df[referenceNameGroup]*-1)
                        column_index += 1
                    elif correlation == 'reference':
                        continue
                    else:
                        raise ValueError("The correlation {} is not supported".format(correlation))
            else:
                colName = value[0]
                df.rename(columns={'Variable_{}'.format(nr): colName}, inplace=True)
                nr += 1

        dfScenarioCopy = df.copy()

        for varName in df.columns:
            variation = self.GeneralDict[varName]['(%)']
            df[varName] = df[varName] * variation

        self.UncertaintyMatrix = df

        # make the list of scenario names
        scenarioNames = []
        for n in range(len(combinations)):
            scenarioNames.append("sc{}".format(n+1))
        self.ScenarioNames = scenarioNames

        # make the list of scenario probabilities
        if self.ProbabilitySettings == 'uniform':
            self.ScenarioProbabilities = [1/len(scenarioNames) for i in scenarioNames]

        elif self.ProbabilitySettings == 'custom':
            for _, row in dfScenarioCopy.iterrows():
                probabilityListParam = []
                probabilityListSC = 1
                for param in row.index:
                    # check if the parameter is a reference parameter if not skip it
                    correlation = self.GeneralDict[param]['Correlation']
                    if correlation == 'reference':
                        lv = row[param]
                        probability = self.GeneralDict[param]['ProbabilityDict'][lv]
                        probabilityListParam.append(probability)
                        probabilityListSC *= probability
                self.ScenarioProbabilities.append(probabilityListSC)


            # a = sum(self.ScenarioProbabilities)
            # print(a)
            # print('heerererere')

        else:
            raise ValueError("ERROR ON EXCEL SHEET 'Uncertainty' \n"
                             "The probability setting {} is not supported yet".format(self.ProbabilitySettings))

    def _set_uncertain_composition_list(self):
        #for key in GeneralDict:
         #   if 'phi' in key:
          #
           # unit.Composition['phi'][(unit.Number, i, sc)] = composition_dic[i]
        pass



def make_first_row_column_names(df):
    if len(df) == 0:
        raise ValueError("DataFrame is empty")

    # Extract the first row as column names
    new_column_names = df.iloc[0]

    # Set the column names to the extracted row
    df.columns = new_column_names

    # Drop the first row (if needed)
    df = df.drop(df.index[0])
    return df
