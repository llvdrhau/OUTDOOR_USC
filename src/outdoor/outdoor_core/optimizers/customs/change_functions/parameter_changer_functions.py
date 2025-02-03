'''
contains all funcitions to change the parameters in the model instance called in change_parameter
(see change_params.py)

Each parameter is indexed in a slightly different way so the data refering to the parameter also
needs to be formated in the same way as in the model.For adding new uncertain parameters, check the
model to see how it needs to be indexed. (see also stochastic.py line 186 and onwards for reference)
For example

if parameterName == 'stoich_reaction_coefficient':
    component = row.Component
    reactionNr = row.Reaction_Number
    nrComponentTuple = (unitNr, (component, reactionNr))

elif parameterName == 'stoich_conversion_factor':
    component = row.Component
    reactionNr = row.Reaction_Number
    nrComponentTuple = (unitNr, (reactionNr, component))

elif parameterName == 'split_factor':
    component = row.Component
    targetUnit = row.Target_Unit
    nrComponentTuple = (unitNr, (targetUnit, component))

elif parameterName == 'component_concentration' or parameterName == 'yield_factor_unit_operation':
    component = row.Component
    nrComponentTuple = (unitNr, component)

elif parameterName == 'ProductPrice' or parameterName == 'material_costs' or parameterName == 'decimal_numbers':
    nrComponentTuple = (unitNr)

'''
def change_myu_parameter(Instance, Value, metadata, *args):
    """
    changes the split factors in the model instance to the given value of a specific component in a specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """
    # nrComponentTuple = (unitNr, (targetUnit, component))
    index = (metadata['Unit_Number'], int(metadata['Target_Unit']), metadata['Component'])
    try :
        Instance.split_factor[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter split_factor (Split Factor)'.format(index))


    return Instance

def change_phi_parameter(Instance, Value, metadata, *args):
    """
    Changes the feed composition in the model instance to the given value of a specific component in a specific unit
    CAREFULL this function changes the feed composition of all components so that the sum of the feed composition is 1
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """
    # nrComponentTuple = (unitNr, component)
    # get the set of components from the model instance
    components = Instance.COMPONENTS.value
    componentsList = []
    for i in components:
        index = (metadata['Unit_Number'], i)
        if Instance.component_concentration[index].value > 0:
            componentsList.append(i)

    # index of the component parameter to change
    index = (metadata['Unit_Number'], metadata['Component'])
    originalValue = Instance.component_concentration[index]
    delta = Value - originalValue

    # percent to change equally over the other components is:
    toSubtract = delta / (len(componentsList)-1)

    # change the value of the component parameters
    try:
        index = (metadata['Unit_Number'], metadata['Component'])
        Instance.component_concentration[index] = Value
    except:
        raise ValueError('Index {} is not a valid set of the Parameter component_concentration (Feed Composition)'.format(index))

    # pop metadata['Component'] from the list
    componentsList.remove(metadata['Component'])

    # change the value of the component parameters which have to be changed equally so the sum of the feed composition
    # remains 1


    for i in componentsList:
        indexB = (metadata['Unit_Number'], i)
        Instance.component_concentration[indexB] = Instance.component_concentration[indexB].value - toSubtract

    # test if the sum of the feed composition is 1 after the change
    # # add the original value of the component to the list again
    # componentsList.append(metadata['Component'])
    # a = 0
    # for i in componentsList:
    #     indexB = (metadata['Unit_Number'], i)
    #     a = a + Instance.component_concentration[indexB].value
    # print(a)

    return Instance

def change_theta_parameter(Instance, Value, metadata, *args):
    """
    Changes the conversion factors in the model instance to the given value of a specific component in a
    specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """

    # nrComponentTuple = (unitNr, (reactionNr, component))
    index = (metadata['Unit_Number'], metadata['Reaction_Number'], metadata['Component'])
    try:
        Instance.stoich_conversion_factor[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter stoich_conversion_factor (Conversion factor)'.format(index))
    return Instance


def change_stoich_parameter(Instance, Value, metadata, *args):
    """
    Changes the stoichiometric factors in the model instance to the given value of a specific component in a
    specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """
    # nrComponentTuple = (unitNr, (component, reactionNr))
    index = (metadata['Unit_Number'], (metadata['Component'], metadata['Reaction_Number']))
    try:
        Instance.stoich_reaction_coefficient[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter stoich_reaction_coefficient (Stoichiometric factor)'.format(index))
    return Instance

def change_xi_parameter(Instance, Value, metadata, *args):
    """
    Changes the yield factors in the model instance to the given value of a specific component in a
    specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """
    # nrComponentTuple = (unitNr, component)
    index = (metadata['Unit_Number'], metadata['Component'])
    try:
        Instance.yield_factor_unit_operation[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter yield_factor_unit_operation (Yield factor)'.format(index))
    return Instance

def change_material_costs(Instance, Value, metadata, *args):
    """
    Changes the material costs in the model instance to the given value of a specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """
    # nrComponentTuple = (unitNr)
    index = (metadata['Unit_Number'])
    try:
        Instance.material_costs[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter material_costs (Material Costs)'.format(index))
    return Instance

def change_product_price(Instance, Value, metadata, *args):
    """
    Changes the product price in the model instance to the given value of a specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """
    # nrComponentTuple = (unitNr)
    index = (metadata['Unit_Number'])
    Instance.ProductPrice[index] = Value
    # don't need to check if the index is valid because the their is a general error function in the change_params.py
    # which is called if the parameter is not in the variation parameter set
    return Instance

def change_utility_costs(Instance, Value, metadata, *args):

    Parameter = args[1]

    if Parameter =='Electricity price (delta_ut)':
        Instance.delta_ut['Electricity'] = Value
    elif Parameter =='Chilling price (delta_ut)':
        Instance.delta_ut['Chilling'] = Value
    else:
        raise ValueError('Parameter Name not correct for utility costs change')

    return Instance

def change_heat_costs(Instance, Value, metadata, *args):
    """
    Changes the heat costs in the model instance to the given value of a specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """

    param = args[1]

    superstructureData = args[0] # superstructure data
    priceDict = superstructureData.temperaturePricesDict


    heatIntervalSet = Instance.HEAT_INTERVALS.value
    #priceSet = Instance.delta_q.value

    if param == 'Heating price super (delta_q)': # super
        for i in heatIntervalSet:
            if Instance.delta_q[i].value == priceDict['super']:
                Instance.delta_q[i] = Value # change the value of the parameter to the new value
    elif param == 'Heating price high (delta_q)': # high
        for i in heatIntervalSet:
            if Instance.delta_q[i].value == priceDict['high']:
                Instance.delta_q[i] = Value

    elif param == 'Heating price medium (delta_q)': # medium
        for i in heatIntervalSet:
            if Instance.delta_q[i].value == priceDict['medium']:
                Instance.delta_q[i] = Value

    elif param == 'Heating price low (delta_q)': # low
        for i in heatIntervalSet:
            if Instance.delta_q[i].value == priceDict['low']:
                Instance.delta_q[i] = Value
    else:
        raise ValueError('Parameter Name {} not correct for heat costs change'.format(param))

    return Instance

def change_heating_demand(Instance, Value, metadata, *args):
    """
    Changes the heat demand in the model instance to the given value of a specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """

    # nrComponentTuple = (unitNr)
    param = args[1]
    if param == 'Heating demand 1 (specific_heat_demand)':
        index = ('Heat',metadata['Unit_Number'])
        index2 = (metadata['Unit_Number'],'Heat')
    else:
        index = ('Heat2',metadata['Unit_Number'])
        index2 = (metadata['Unit_Number'], 'Heat2')

    if Value > 0:
        try:
            Instance.specific_heat_demand[index] = Value
            Instance.specific_utility_demand[index2] = Value
        except:
            raise ValueError('Index {} is not a valid set of the Parameter heat_demand (Heat Demand)'.format(index))
    else:
        try:
            Instance.specific_cooling_demand[index] = Value
            Instance.specific_utility_demand[index2] = Value
        except:
            raise ValueError('Index {} is not a valid set of the Parameter heat_demand (Heat Demand)'.format(index))

    return Instance

def change_utility_demand(Instance, Value, metadata, *args):
    """
    Changes the electricity demand or chilling demand in the model instance to the given value of a specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """
    param = args[1]
    if param == 'Electricity demand (specific_utility_demand)':
        index = (metadata['Unit_Number'], 'Electricity')
        #index2 = (metadata['Unit_Number'],'Electricity')
    else:
        index = (metadata['Unit_Number'], 'Chilling')
        #index2 = (metadata['Unit_Number'],'Chilling')

    try:
        Instance.specific_utility_demand[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter electricity_demand (Electricity Demand)'.format(index))
    return Instance

def change_concentration_demand(Instance, Value, metadata, *args):
    """
    Changes the component concentration in the model instance to the given value of a specific unit
    :param Instance: model instance
    :param Value: float
    :param metadata: pd.Series
    :param args: list
    :return: model instance
    """
    # nrComponentTuple = (unitNr, component)
    index = (metadata['Unit_Number'])
    try:
        Instance.concentration[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter concentration (Component concentration)'.format(index))
    return Instance


from ....utils.linearizer import capex_calculator


def change_capital_costs(Instance, Value, metadata, *args):

    Superstructure = args[0]
    Index = metadata['Unit_Number']

    for i in Superstructure.UnitsList:
        if i.Number == Index:
            unit_operation = i
            unit_operation.CAPEX_factors['C_Ref'][Index] = Value
            (x_vals,y_vals) = capex_calculator(unit_operation, Superstructure.CECPI,Superstructure.linearizationDetail)
            temp_x = x_vals['lin_CAPEX_x']
            temp_y = y_vals['lin_CAPEX_y']


            for i in range(len(temp_x)):
                Instance.lin_CAPEX_x[Index,i+1] = temp_x[Index,i+1]
                Instance.lin_CAPEX_y[Index,i+1] = temp_y[Index,i+1]

            break

    return Instance


def change_opex_factor(Instance, Value, metadata, *args):

        Index = metadata['Unit_Number']

        Instance.K_OM[Index] = Value

        return Instance
