import pandas as pd
import warnings

def makeTabels(excel, roundTo: int =3, format: str = 'print', path: str = 'examples/Excel_files/excel_4_latex'):
    """
    Reads the input excel file and creates tables for literature review or papers

    :param path: str, path to the excel file

    """

    print('PATH NAME IS:::')
    print(excel)


    # Disable the specific warning about Data Validation extension to make code run faster
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    dataframe = pd.read_excel(excel, sheet_name=None)

    PU_ObjectList = []

    ## Hidden tables with specific names will be skipped:
    Hidden_Tables = []
    Hidden_Tables.append('Template_PhysicalProcess')
    Hidden_Tables.append('Template_StoichReactor')
    Hidden_Tables.append('Template_YieldReactor')
    Hidden_Tables.append('Template_SteamGenerator')
    Hidden_Tables.append('Template_ElGenerator')
    Hidden_Tables.append('Template_ProductPool')
    Hidden_Tables.append('DataBank')
    Hidden_Tables.append('Component Databases')
    Hidden_Tables.append('Uncertainty_test_idea')
    Hidden_Tables.append('Uncertainty_old')

    dictionaryUnitProcesses = {}
    splittingDataFrames = {}
    reactionDataFrames = {}

    maxCount = 3
    count = 0
    unitNumberDict = {}
    for i in dataframe.keys():
        count += 1
        if i == 'Systemblatt':
            # DFGeneralData = dataframe[i]
            continue
            # directCostFactor = DF.iloc[13, 4]
            # dictionaryUnitProcesses[name]['directCostFactor'] = directCostFactor

            # indirectCostFactor = DF.iloc[14, 4]
            # dictionaryUnitProcesses[name]['indirectCostFactor'] = indirectCostFactor

        elif i == 'Uncertainty':
            continue

        elif i == 'Sensitivity':
            continue

        elif i == "Pools":
            DFPools = dataframe[i]
            DFselect = DFPools.iloc[4:6, 3:14]

            for col in DFselect:
                if not pd.isnull(DFselect[col].iloc[0]):
                    name = DFselect[col].iloc[0]
                    number = DFselect[col].iloc[1]
                    unitNumberDict.update({number: name})

            continue

        elif i == "Sources":
            DFSources = dataframe[i]
            DFselect = DFSources.iloc[4:6, 3:14]

            for col in DFselect:
                if not pd.isnull(DFselect[col].iloc[0]):
                    name = DFselect[col].iloc[0]
                    number = DFselect[col].iloc[1]
                    unitNumberDict.update({number: name})

        elif i == 'Distributor':
            DFDistro = dataframe[i]
            DFselect = DFDistro.iloc[4:6, 3:14]

            for col in DFselect:
                if not pd.isnull(DFselect[col].iloc[0]):
                    name = DFselect[col].iloc[0]
                    number = DFselect[col].iloc[1]
                    unitNumberDict.update({number: name})

        elif i in Hidden_Tables:
            continue  # skip the hidden tables

        else:  # for the unit operations

            DF = dataframe[i]
            # get the data from the excel file and create the tables
            # get the name

            name = DF.iloc[8,4]
            number = DF.iloc[9,4]
            unitNumberDict.update({number:name})

            dictionaryUnitProcesses[name] = {}
            type = DF.iloc[10,4]
            lifeTime = DF.iloc[12,4]
            TemperatureIn = DF.iloc[15,4]
            TemperatureOut = DF.iloc[16,4]
            efficientcy = DF.iloc[19,4]

            # create a dictionary with the data
            dictionaryUnitProcesses[name]['Type'] = type
            dictionaryUnitProcesses[name]['Lifetime (y)'] = lifeTime
            dictionaryUnitProcesses[name]['Temperature In (°C)'] = TemperatureIn
            dictionaryUnitProcesses[name]['Temperature Out (°C)'] = TemperatureOut

            if type == 'Heat.Generator':
                dictionaryUnitProcesses[name]['Efficiency Electricity Production'] = '(-)'
                dictionaryUnitProcesses[name]['Efficiency Heat Production (-)'] = efficientcy

            elif type == 'Elect.Generator':
                dictionaryUnitProcesses[name]['Efficiency Electricity Production (-)'] = efficientcy
                dictionaryUnitProcesses[name]['Efficiency Heat Production (-)'] = '(-)'

            elif type == 'CHP.Generator':
                dictionaryUnitProcesses[name]['Efficiency Electricity Production (-)'] = 0.35
                dictionaryUnitProcesses[name]['Efficiency Heat Production (-)'] = 0.50



            # equipment cost
            equipmentCost = DF.iloc[9,8]
            dictionaryUnitProcesses[name]['Reference Equipment Cost (M€)'] = round(equipmentCost, roundTo)

            referenceCapacity = DF.iloc[10, 8]  # Reference capacity
            dictionaryUnitProcesses[name]['Reference Capacity (t/h)'] = round(referenceCapacity, roundTo)

            scaleparameter = DF.iloc[11, 8]  # Exponent of the scaling law
            dictionaryUnitProcesses[name]['Scale Parameter (-)'] = round(scaleparameter, roundTo)

            referenceYear = DF.iloc[12, 8] # The reference year for the equipment cost for CPIEX
            dictionaryUnitProcesses[name]['Reference Year '] = referenceYear


            # energy related data
            electricityConsumption = DF.iloc[8, 13]
            dictionaryUnitProcesses[name]['Electricity Consumption (kWh/kg)'] = round(electricityConsumption,roundTo)
            # units: kWh/kg
            heatingConsumption = DF.iloc[8, 14]
            dictionaryUnitProcesses[name]['Heating Consumption (kWh/kg)'] = round(heatingConsumption,roundTo)

            # Seperation efficiency
            # seperate a block of the dataFrame for the seperation efficiency
            seperationEfficiencyDataFrame = DF.iloc[8:22, 18:21]
            splitDictionary = {}
            componentKeys = []
            for index, row in seperationEfficiencyDataFrame.iterrows():
                # check if row.iloc[0] is nan
                if not pd.isnull(row.iloc[0]):
                    componentKeys.append(row.iloc[1])
                    if row.iloc[0] in splitDictionary.keys():
                        splitDictionary[row.iloc[0]].update({row.iloc[1]: round(row.iloc[2],roundTo)})
                    else:
                        splitDictionary[row.iloc[0]] = {}
                        splitDictionary[row.iloc[0]].update({row.iloc[1]: round(row.iloc[2],roundTo)})

                else:
                    continue


            splitDataFrame = pd.DataFrame(splitDictionary)
            # add the waste stream column to the splitting table
            splitDataFrame['Waste'] = 1 - splitDataFrame.sum(axis=1)

            splittingDataFrames[name] = splitDataFrame


            # add stoiometric data if it is stoichometric unit
            if type == 'Stoich.Reactor':
                stoichiometricDataFrame = DF.iloc[8:44, 33:36]
                stoichiometricDictionary = {}
                for index, row in stoichiometricDataFrame.iterrows():
                    if not pd.isnull(row.iloc[0]):
                        reactionNumber = row.iloc[1] # reaction number
                        chemical =  row.iloc[0]
                        stoich = round(row.iloc[-1], roundTo)

                        if reactionNumber in stoichiometricDictionary.keys():
                            stoichiometricDictionary[reactionNumber].update({chemical: stoich})
                        else:
                            stoichiometricDictionary[reactionNumber] = {}
                            stoichiometricDictionary[reactionNumber].update({chemical: stoich})

                    else:
                        continue
                reactionDictionary = reactions_as_string(stoichiometricDictionary)

                # now get the conversion efficiency of each described reaction
                # and make the final reaction duictionary
                reactionDictionaryNew = {}
                conversionEfficiencyDF = DF.iloc[8:32, 37:40]
                for index, row in conversionEfficiencyDF.iterrows():
                    if not pd.isnull(row.iloc[0]):
                        reactionNumber = row.iloc[0]  # reaction number
                        conversionEfficiency = row.iloc[-1]
                        reactionString = reactionDictionary[reactionNumber]
                        reactionDictionaryNew['Reaction {}'.format(reactionNumber)] = {}
                        reactionDictionaryNew['Reaction {}'.format(reactionNumber)].update({'Reaction':reactionString})
                        reactionDictionaryNew['Reaction {}'.format(reactionNumber)].update({'Conversion Efficiency': conversionEfficiency})



                reactionDataFrames[name] = pd.DataFrame(reactionDictionaryNew)
                #dictionaryUnitProcesses[name]['Reactions'] = reactionList

            if type == 'Yield.Reactor':
                component = DF.iloc[8, 33]
                yieldFactor = DF.iloc[8, 34]
                dictionaryUnitProcesses[name]['Yield Component (-)'] = component
                dictionaryUnitProcesses[name]['Yield Factor ($g_{product}/g_{feed}$)'] = round(yieldFactor, roundTo)
            else:
                dictionaryUnitProcesses[name]['Yield Component (-)'] = '(-)'
                dictionaryUnitProcesses[name]['Yield Factor ($g_{product}/g_{feed}$)'] = '(-)'

    # create the tables
    # 1) Unit Process Data
    dataFrameData = pd.DataFrame(dictionaryUnitProcesses)
    table = dataFrameData.fillna('(-)')
    match format:
        case 'print':
            print(table)
        case 'latex':
            #print(table.to_latex()) # Include header row
            # print('\n % ----------------------------- \n % -------------- \n')
            # latexCode = dataframe_to_longtable(table, caption='Unit Process Data', label='unitProcessData')
            # print(latexCode)

            split_dataframe_to_latex(table,
                                     caption_base='Unit Process Data',
                                     label_base='unitProcessData',
                                     columns_per_table=3)
        case 'excel':
            if path:
                table.to_excel(f'{path}/unitProcessData.xlsx')
            else: # save in the current directory
                table.to_excel('unitProcessData.xlsx')

    # 2) Splitting Data
    # each dataframe I want to export to a different sheet in the excel file
    output_file: str = 'splittingData.xlsx'
    if path:
        output_file = f'{path}/splittingData.xlsx'

    # print 1 splitting table
    print()
    print('$ Spliting Table')
    print('\n $ ----------------------------- \n $ --------------')

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for name, df in splittingDataFrames.items():
            df = df.fillna(0)
            df = df.rename(columns= unitNumberDict)
            if format == 'print':
                print(df)
            elif format == 'latex':
                latexCode = dataframe_to_latex_table_splitting(df, caption=f'Splitting of Unit {name}', label=name + '_splitting')
                print('')
                print("% -----------------------------------------")
                print('')
                print(latexCode)
                print('')
                print("% -----------------------------------------")

            elif format == 'excel':
                # Write each DataFrame to a new sheet in the same Excel file
                df.to_excel(writer, sheet_name=name)


    # Initialize ExcelWriter outside the loop
    output_file: str = 'ReactionData.xlsx'
    if path:
        output_file = f'{path}/ReactionData.xlsx'
    print()
    print('% Reaction Table')
    print('\n % ----------------------------- \n % --------------')

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for name, df in reactionDataFrames.items():
            df = df.transpose()
            # Change the order of the columns
            df = df[['Reaction', 'Conversion Efficiency']]

            if format == 'print':
                # Print 1 reaction table

                print(df)
            elif format == 'latex':
                # Print 1 reaction table in LaTeX format
                caption = f'Reactions of Unit {name}'
                latexText = dataframe_to_latex_table_reacations(df, caption=caption, label=name)
                print('')
                print("% -----------------------------------------")
                print('')
                print(latexText)
                print('')
                print("% -----------------------------------------")



            elif format == 'excel':
                # Write each DataFrame to a new sheet in the same Excel file
                df.to_excel(writer, sheet_name=name)


def reactions_as_string(reactionDict):

    reactionList = {}
    for reactionNumber, reactionComponents in reactionDict.items():
        reactantsDict = {}
        productsDict = {}
        for component, stoich in reactionComponents.items():
            if stoich < 0:
                reactantsDict[component] = - stoich # make the stoich positive for the reactants
            else:
                productsDict[component] = stoich

        stringReactionReactants = ''
        for component, stoich in reactantsDict.items():
            stringReactionReactants += f'{stoich} {component} + '

        stringReactionProducts = ''
        for component, stoich in productsDict.items():
            stringReactionProducts += f'{stoich} {component} + '

        reactionsString = f'{stringReactionReactants[:-3]} -> {stringReactionProducts[:-3]}'

        reactionList.update({reactionNumber:reactionsString})
    return reactionList

def dataframe_to_longtable(df, caption="", label="tab:my-table", nCol = 3):
    """
    Converts a DataFrame to a LaTeX longtable format with a specified caption and label.

    Args:
    - df (pd.DataFrame): The DataFrame to convert.
    - caption (str): The caption for the LaTeX table.
    - label (str): The label for the LaTeX table.

    Returns:
    - str: A string containing the LaTeX longtable.
    """

    # Start the longtable environment
    latex_code += "\\begin{longtable}[c]{@{}" + "l" * (df.shape[1] + 1) + "@{}}\n"
    #eg:  \begin{longtable}[c]{@{}lll@{}}

    # Add caption and label
    latex_code += f"\\caption{{{caption}}} \\\\\n"
    latex_code += f"\\label{{{label}}} \\\\\n"


    # Begin first head
    latex_code += "\\endfirsthead\n"
    latex_code += "%\n"
    latex_code += "\\endhead\n"
    latex_code += "%\n"

    # Generate table content
    for index, row in df.iterrows():
        row_str = ' & '.join([str(index)] + [str(value) for value in row]) + " \\\\\n"
        latex_code += row_str

    # End the longtable environment
    latex_code += "\\end{longtable}\n"
    latex_code = "\\end{landscape}\n"

    return latex_code


def split_dataframe_to_latex(df, caption_base, label_base, columns_per_table):
    # Split the DataFrame into chunks of specified number of columns
    chunks = [df.iloc[:, i:i + columns_per_table] for i in range(0, df.shape[1], columns_per_table)]

    latex_tables = []

    for idx, chunk in enumerate(chunks):
        # Creating LaTeX table for each chunk
        caption = f"{caption_base} - Part {idx + 1}"
        label = f"{label_base}_part{idx + 1}"

        # Convert DataFrame chunk to LaTeX
        # latex_code = chunk.to_latex(index=True, header=True)
        latex_code = chunk.to_latex(index=True, header=True, float_format=lambda x: f"{x:g}")

        # Wrap in table environment with resizebox without indenting
        latex_table = (
            "\\begin{table}[h]\n"
            "\\centering\n"
            f"\\caption{{{caption}}}\n"
            f"\\label{{{label}}}\n"
            "\\resizebox{\\columnwidth}{!}{%\n"
            f"{latex_code}"
            "}\n"
            "\\end{table}\n"
        )

        latex_code = latex_table.replace("_", "\_")  # Replace '_' with '\_' so it doesn't mess up the LaTeX formatting
        latex_table = latex_table.replace("llll", "lccc")  # Remove trailing zeros
        print('% -------------------')
        print('')
        print(latex_table)
        latex_tables.append(latex_table)

    return latex_tables

def dataframe_to_latex_table_reacations(df, caption="A caption I want", label="unit_name"):
    # Convert the DataFrame to LaTeX format
    latex_table = df.to_latex(index=False, escape=False)

    # Customize the LaTeX string

    latex_table = latex_table.replace("\\begin{tabular}", "\\small % Set font size to small\n\\begin{tabular}")
    latex_table = latex_table.replace("\\begin{tabular}{ll}", "\\begin{tabular}{@{}lc@{}}")
    #latex_table = latex_table.replace("\\end{tabular}", "\\end{tabular}%\n}")

    latex_table = latex_table.replace("->", " $\\rightarrow$ ")  # Replace '->' with LaTeX arrow
    latex_table = latex_table.replace("_", "\_")  # Replace '_' with '\_' so it doesn't mess up the LaTeX formatting
    latex_table = latex_table.replace("000", "") # Remove trailing zeros
    # latex_table = latex_table.replace("\\toprule",
    #                                   "\\toprule\nReaction & \\multicolumn{1}{l}{Conversion Efficiency} & Reference \\\\ ") # \\midrule
    latex_table = latex_table.replace("Reaction & Conversion Efficiency \\", "Reaction & \multicolumn{1}{l}{Conversion Efficiency}  \\")
    latex_table = latex_table.replace("\\bottomrule", "\\bottomrule\n")

    # Add resizebox and centering
    #latex_table = "\\resizebox{\\columnwidth}{!}{%\n" + latex_table

    # Add the table environment, caption, and label
    latex_code = "\\begin{table}[h]\n\\centering\n"
    latex_code += "\\caption{" + caption + "}\n"
    latex_code += "\\label{" + label + "}\n"
    latex_code += latex_table
    latex_code += "\\end{table}"

    return latex_code

def dataframe_to_latex_table_splitting(df, caption="Caption input", label="label_input"):
    """
    Converts a DataFrame to a LaTeX table format with a specified caption and label.

    Args:
    - df (pd.DataFrame): The DataFrame to convert.
    - caption (str): The caption for the LaTeX table.
    - label (str): The label for the LaTeX table.

    Returns:
    - str: A string containing the LaTeX table.
    """

    # Convert the DataFrame to LaTeX format without special character escaping
    latex_table = df.to_latex(index=True, header=True, escape=False)

    # Modify the LaTeX table string to fit the desired format
    latex_table = latex_table.replace("\\begin{tabular}{lrrr}", "\\begin{tabular}{@{}lccc@{}}")
    latex_table = latex_table.replace("\\toprule",
                                      "\\toprule\n\\textbf{Chemical \\textbackslash Target units} & " + " & ".join(
                                          [f"\\multicolumn{{1}}{{l}}{{{col}}}" for col in df.columns]) + " \\\\ ")
    latex_table = latex_table.replace("0000", "") # Remove trailing zeros
    latex_table = latex_table.replace("000", "") # Remove trailing zeros
    latex_table = latex_table.replace("_", "\_") # Replace '_' with '\_' so it doesn't mess up the LaTeX formatting

    # Remove the header line with column names (after \\midrule)
    headerLine = ""
    for colName in df.columns:
        headerLine += f" & {colName}"
    headerLine += " \\\\"
    latex_table = latex_table.replace(headerLine, "")

    #latex_table = latex_table.replace("0.", "0") # Remove trailing zeros
    #latex_table = latex_table.replace("1.", "1") # Remove trailing zeros
    #latex_table = latex_table.replace(".0", "0") # Remove trailing zeros




    # Add the table environment, caption, and label
    latex_code = "\\begin{table}[h]\n\\centering\n"
    latex_code += "\\caption{" + caption + "}\n"
    latex_code += "\\label{" + label + "}\n"
    latex_code += "\\small\n"  # Set font size to small
    latex_code += latex_table
    latex_code += "\\end{table}"

    return latex_code


if __name__ == '__main__':

    makeTabels('potato_peel_case_study.xlsm',
               format='latex',
               path= r'C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\Excel_files\excel_4_latex')
