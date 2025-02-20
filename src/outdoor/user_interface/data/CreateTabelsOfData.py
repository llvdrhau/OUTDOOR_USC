import pandas as pd


class LatTexTableCreator:
    def __init__(self, superstructureObject, round_to=3):
        self.superstructureObject = superstructureObject
        self.round_to = round_to
        self.dictionary_unit_processes = {}
        self.splitting_data_frames = {}
        self.unit_id_dict = self.superstructureObject.UnitNames2['Names']

        self.reaction_data_frames = {}
        self.reaction_uuid_dict = {}

        for i, uuid in enumerate(self.superstructureObject.ReactionsList['R']):
            self.reaction_uuid_dict[uuid] = i + 1

        self.format = None

    def create_table(self, format='LaTex'):
        self.format = format

        unitList = self.superstructureObject.UnitsList
        for unit in unitList:
            if unit.Type in 'Source':
                pass
                #self._create_source_table(unit)
            elif unit.Type == 'Distributor':
                pass
                # self._create_distributor_table(unit)
            elif unit.Type == 'ProductPool':
                pass
                # self._create_pool_table(unit)
            else:
                self._process_unit_operations(unit)

        self._generate_tables()

    def _process_unit_operations(self, unit):

        name, uuid = unit.Name, unit.Number
        self.dictionary_unit_processes[name] = {
            'Type': unit.Type,
            'Lifetime (y)': unit.LT['LT'][uuid],
            'Temperature In (°C)': unit.T_IN['Heat'],
            'Temperature Out (°C)': unit.T_OUT['Heat'],
        }

        self._add_equipment_cost(unit, name, uuid)
        self._add_energy_data(unit, name, uuid)
        self._add_energy_generators_data(unit, name, uuid)
        self._add_separation_data(unit, name)
        self._add_reaction_data(unit, name )
        self._add_yield_data(unit, name)

    def _add_equipment_cost(self, unit, name, uuid):
        CAPEX_dict = unit.CAPEX_factors
        self.dictionary_unit_processes[name].update({
            'Reference Equipment Cost (M€)': round(CAPEX_dict['CECPI_ref'][uuid], self.round_to),
            'Reference Capacity (t/h)': round(CAPEX_dict['m_Ref'][uuid], self.round_to),
            'Scale Parameter (-)': round(CAPEX_dict['f'][uuid], self.round_to),
            'Chemical Plant Index': CAPEX_dict['CECPI_ref'][uuid],
        })

    def _add_energy_data(self, unit, name, uuid):
        if not unit.tau['tau']:
            electricity = 0
            heat = 0
        else:
            electricity = unit.tau['tau'][uuid, 'Electricity'] if unit.tau['tau'][uuid, 'Electricity'] is not None else 0
            heat = unit.tau['tau'][uuid, 'Heat'] if unit.tau['tau'][uuid, 'Heat'] is not None else 0

        self.dictionary_unit_processes[name].update({
            'Electricity Consumption (kWh/kg)': round(electricity, self.round_to),
            'Heating Consumption (kWh/kg)': round(heat, self.round_to),
        })

    def _add_energy_generators_data(self,unit, name, uuid):
        type = unit.Type
        if type in ["ElectricityGenerator", 'CombinedHeatAndPower', 'HeatGenerator']:

            if type == 'HeatGenerator':
                efficiencyHeat = unit.Efficiency_FUR['Efficiency_FUR'][uuid]

                self.dictionary_unit_processes[name]['Efficiency Electricity Production'] = '(-)'
                self.dictionary_unit_processes[name]['Efficiency Heat Production (-)'] = efficiencyHeat

            elif type == 'ElectricityGenerator':
                efficiencyElec = unit.Efficiency_TUR['Efficiency_TUR'][uuid]
                self.dictionary_unit_processes[name]['Efficiency Electricity Production (-)'] = efficiencyElec
                self.dictionary_unit_processes[name]['Efficiency Heat Production (-)'] = '(-)'

            elif type == 'CombinedHeatAndPower':
                efficiencyElec = unit.Efficiency_TUR['Efficiency_TUR'][uuid]
                efficiencyHeat = unit.Efficiency_FUR['Efficiency_FUR'][uuid]
                self.dictionary_unit_processes[name]['Efficiency Electricity Production (-)'] = efficiencyElec
                self.dictionary_unit_processes[name]['Efficiency Heat Production (-)'] = efficiencyHeat

    def _add_separation_data(self, unit, name):
        separation_Dict = unit.myu['myu']
        split_dict = {}

        for key, val in separation_Dict.items():
            targetUnitUID = key[1][0]
            targetUnit = self.unit_id_dict[targetUnitUID]
            component = key[1][1]
            # split_dict[targetUnit].update({component: round(val, self.round_to)})
            split_dict.setdefault(targetUnit, {})[component] = val

        split_df = pd.DataFrame(split_dict)
        split_df['Waste'] = 1 - split_df.sum(axis=1)
        self.splitting_data_frames[name] = split_df

    def _add_reaction_data(self, unit, name):
        if unit.Type in ["ElectricityGenerator", 'CombinedHeatAndPower', 'HeatGenerator', 'Stoich-Reactor']:
            self._process_stoich_reactor(unit, name)

    def _process_stoich_reactor(self, unit, name):
        reactionDict = {}
        for key, stoich in unit.gamma['gamma'].items():
                reactionNumber = key[1][1]
                component = key[1][0]
                reactionDict.setdefault(reactionNumber, {})[component] = round(stoich, self.round_to)
        reactionDict = self._reactions_as_string(reactionDict)

        # now get the conversion efficiency of each described reaction
        # and make the final reaction dictionary
        reactionDictionaryNew = {}
        conversionEfficiencyDict = unit.theta['theta']
        for key, val in conversionEfficiencyDict.items():

                reactionUUID = key[1][0] # reaction number
                conversionEfficiency = val
                reactionString = reactionDict[reactionUUID]
                reactionNumber = self.reaction_uuid_dict[reactionUUID]

                reactionDictionaryNew['Reaction {}'.format(reactionNumber)] = {}
                reactionDictionaryNew['Reaction {}'.format(reactionNumber)].update({'Reaction': reactionString})
                reactionDictionaryNew['Reaction {}'.format(reactionNumber)].update({'Conversion Efficiency': val})
        df = pd.DataFrame(reactionDictionaryNew)
        self.reaction_data_frames[name] = df

    def _add_yield_data(self, unit, name):
        if 'Yield-Reactor' in unit.Type:
            yieldDict = unit.xi['xi']
            key = list(yieldDict.keys())[0]
            component = key[1]
            yieldFactor = yieldDict[key]

            self.dictionary_unit_processes[name]['Yield Component (-)'] = component
            self.dictionary_unit_processes[name]['Yield Factor ($g_{product}/g_{feed}$)'] = round(yieldFactor, self.round_to)
        else:
            self.dictionary_unit_processes[name]['Yield Component (-)'] = '(-)'
            self.dictionary_unit_processes[name]['Yield Factor ($g_{product}/g_{feed}$)'] = '(-)'


    def _reactions_as_string(self, reaction_dict):
        reaction_list = {}
        for number, components in reaction_dict.items():
            reactants = ' + '.join([f'{-v} {k}' for k, v in components.items() if v < 0])
            products = ' + '.join([f'{v} {k}' for k, v in components.items() if v > 0])
            reaction_list[number] = f'{reactants} -> {products}'
        return reaction_list

    def _generate_tables(self):
        df_data = pd.DataFrame(self.dictionary_unit_processes).fillna('(-)')

        if self.format == 'print':
            print(df_data)

        elif self.format == 'LaTex':
            self._dataframe_to_latex(df=df_data,
                                     caption_base='Unit Process Data',
                                     label_base='unitProcessData',
                                     columns_per_table=3)
            self._print_separation_latex_code()
            self._print_reaction_latex_code()

            #self._export_latex(df_data, 'Unit Process Data', 'unitProcessData')

        elif self.format == 'excel':
            df_data.to_excel(f'{self.path}/unitProcessData.xlsx')

    def _print_separation_latex_code(self):
        for name, df in self.splitting_data_frames.items():
            df = df.fillna(0)
            # df = df.rename(columns= unitNumberDict)
            latexCode = self._dataframe_to_latex_separation_tables(df, caption=f'Splitting of Unit {name}', label=name + '_splitting')
            print(latexCode)
            print("")
            print("% -------------------")
            print("")

    def _print_reaction_latex_code(self):
        for name, df in self.reaction_data_frames.items():
            df = df.transpose()
            # Change the order of the columns
            df = df[['Reaction', 'Conversion Efficiency']]

            # Print 1 reaction table in LaTeX format
            caption = f'Reactions of Unit {name}'
            latexText = self._dataframe_to_latex_reactions_tables(df, caption=caption, label=name)
            print('')
            print("% -----------------------------------------")
            print('')
            print(latexText)
            print('')
            print("% -----------------------------------------")

    def _dataframe_to_latex(self,df, caption_base, label_base, columns_per_table):
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

            latex_code = latex_table.replace("_",
                                             "\_")  # Replace '_' with '\_' so it doesn't mess up the LaTeX formatting
            latex_table = latex_table.replace("llll", "lccc")  # Remove trailing zeros
            print('% -------------------')
            print('')
            print(latex_table)
            latex_tables.append(latex_table)

        return latex_tables

    def _dataframe_to_latex_separation_tables(self,df, caption="Caption input", label="label_input"):
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
        latex_table = latex_table.replace("0000", "")  # Remove trailing zeros
        latex_table = latex_table.replace("000", "")  # Remove trailing zeros
        latex_table = latex_table.replace("_", "\_")  # Replace '_' with '\_' so it doesn't mess up the LaTeX formatting

        # Remove the header line with column names (after \\midrule)
        headerLine = ""
        for colName in df.columns:
            headerLine += f" & {colName}"
        headerLine += " \\\\"
        latex_table = latex_table.replace(headerLine, "")

        # latex_table = latex_table.replace("0.", "0") # Remove trailing zeros
        # latex_table = latex_table.replace("1.", "1") # Remove trailing zeros
        # latex_table = latex_table.replace(".0", "0") # Remove trailing zeros

        # Add the table environment, caption, and label
        latex_code = "\\begin{table}[h]\n\\centering\n"
        latex_code += "\\caption{" + caption + "}\n"
        latex_code += "\\label{" + label + "}\n"
        latex_code += "\\small\n"  # Set font size to small
        latex_code += latex_table
        latex_code += "\\end{table}"

        return latex_code

    def _dataframe_to_latex_reactions_tables(self, df, caption="A caption I want", label="unit_name"):
        # Convert the DataFrame to LaTeX format
        latex_table = df.to_latex(index=False, escape=False)

        # Customize the LaTeX string

        latex_table = latex_table.replace("\\begin{tabular}", "\\small % Set font size to small\n\\begin{tabular}")
        latex_table = latex_table.replace("\\begin{tabular}{ll}", "\\begin{tabular}{@{}lc@{}}")
        # latex_table = latex_table.replace("\\end{tabular}", "\\end{tabular}%\n}")

        latex_table = latex_table.replace("->", " $\\rightarrow$ ")  # Replace '->' with LaTeX arrow
        latex_table = latex_table.replace("_", "\_")  # Replace '_' with '\_' so it doesn't mess up the LaTeX formatting
        latex_table = latex_table.replace("000", "")  # Remove trailing zeros
        # latex_table = latex_table.replace("\\toprule",
        #                                   "\\toprule\nReaction & \\multicolumn{1}{l}{Conversion Efficiency} & Reference \\\\ ") # \\midrule
        latex_table = latex_table.replace("Reaction & Conversion Efficiency \\",
                                          "Reaction & \multicolumn{1}{l}{Conversion Efficiency}  \\")
        latex_table = latex_table.replace("\\bottomrule", "\\bottomrule\n")

        # Add resizebox and centering
        # latex_table = "\\resizebox{\\columnwidth}{!}{%\n" + latex_table

        # Add the table environment, caption, and label
        latex_code = "\\begin{table}[h]\n\\centering\n"
        latex_code += "\\caption{" + caption + "}\n"
        latex_code += "\\label{" + label + "}\n"
        latex_code += latex_table
        latex_code += "\\end{table}"

        return latex_code
