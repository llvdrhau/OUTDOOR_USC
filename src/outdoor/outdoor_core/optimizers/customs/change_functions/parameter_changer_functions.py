'''
contains all funcitions to change the parameters in the model instance called in change_parameter
(see change_params.py)

Each parameter is indexed in a slightly different way so the data refering to the parameter also
needs to be formated in the same way as in the model.For adding new uncertain parameters, check the
model to see how it needs to be indexed. (see also stochastic.py line 186 and onwards for reference)
For example

if parameterName == 'gamma':
    component = row.Component
    reactionNr = row.Reaction_Number
    nrComponentTuple = (unitNr, (component, reactionNr))

elif parameterName == 'theta':
    component = row.Component
    reactionNr = row.Reaction_Number
    nrComponentTuple = (unitNr, (reactionNr, component))

elif parameterName == 'myu':
    component = row.Component
    targetUnit = row.Target_Unit
    nrComponentTuple = (unitNr, (targetUnit, component))

elif parameterName == 'phi' or parameterName == 'xi':
    component = row.Component
    nrComponentTuple = (unitNr, component)

elif parameterName == 'ProductPrice' or parameterName == 'materialcosts' or parameterName == 'Decimal_numbers':
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
    index = (metadata['Unit_Number'], (metadata['Target_Unit'], metadata['Component']))
    try :
        Instance.myu[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter myu (Split Factor)'.format(index))


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
    components = Instance.I.value
    componentsList = []
    for i in components:
        index = (metadata['Unit_Number'], i)
        if Instance.phi[index].value > 0:
            componentsList.append(i)

    # index of the component parameter to change
    index = (metadata['Unit_Number'], metadata['Component'])
    originalValue = Instance.phi[index]
    delta = Value - originalValue

    # percent to change equally over the other components is:
    toSubtract = delta / (len(componentsList)-1)

    # change the value of the component parameters
    try:
        index = (metadata['Unit_Number'], metadata['Component'])
        Instance.phi[index] = Value
    except:
        raise ValueError('Index {} is not a valid set of the Parameter phi (Feed Composition)'.format(index))

    # pop metadata['Component'] from the list
    componentsList.remove(metadata['Component'])

    # change the value of the component parameters which have to be changed equally so the sum of the feed composition
    # remains 1


    for i in componentsList:
        indexB = (metadata['Unit_Number'], i)
        Instance.phi[indexB] = Instance.phi[indexB].value - toSubtract

    # test if the sum of the feed composition is 1 after the change
    # # add the original value of the component to the list again
    # componentsList.append(metadata['Component'])
    # a = 0
    # for i in componentsList:
    #     indexB = (metadata['Unit_Number'], i)
    #     a = a + Instance.phi[indexB].value
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
    index = (metadata['Unit_Number'], (metadata['Reaction_Number'], metadata['Component']))
    try:
        Instance.theta[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter theta (Conversion factor)'.format(index))
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
        Instance.gamma[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter gamma (Stoichiometric factor)'.format(index))
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
        Instance.xi[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter xi (Yield factor)'.format(index))
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
        Instance.materialcosts[index] = Value
    except KeyError:
        raise ValueError('Index {} is not a valid set of the Parameter materialcosts (Material Costs)'.format(index))
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

    Parameter = metadata['Parameter_Type']

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

    heatIntervalSet = Instance.HI.value
    priceSet = Instance.delta_q.value
    raise NotImplementedError('This function is not implemented yet')

    #for i in heatIntervalSet:



    return Instance
