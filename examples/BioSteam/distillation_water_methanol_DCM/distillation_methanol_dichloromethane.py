import biosteam as bst
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from thermosteam import settings, Stream, Chemical, Chemicals

def distillation_water_methanol_DCM(df, pprint=False):
    """
    This function simulates a two distillation columns for the separation of a mixture of water,
    methanol and dichloromethane. The composition has already been set in the feed stream.
    you can decide the dilution factor (df) of the feed stream.

    :param pprint: choose to print the results of the distillation columns
    :param df: dilution factor of the feed stream
    :return: CAPEX of the two distillation columns
    """
    # Define chemicals
    chemicals = Chemicals(['Water', 'Methanol', 'Dichloromethane'])
    chemicals.compile()
    settings.set_thermo(chemicals)

    # Define feed stream
    feed = Stream('feed',
                  Water=80 * 1000 / df,  # Convert m3/h to kg/h using density (1 m3 = 1000 kg for water)
                  Methanol=80 * 791 / df,  # Methanol density ~791 kg/m3
                  Dichloromethane=500 * 1320 / df,  # Dichloromethane density ~1320 kg/m3
                  units='kg/hr')

    # First distillation column: Water-Methanol-DCM separation
    distillation_1 = bst.units.BinaryDistillation(
        'distillation_1',
        ins=feed,
        outs=('distillate_1', 'bottoms_1'),
        LHK=('Methanol', 'Water'),
        y_top=0.95,  # 95% Methanol in the vapor
        x_bot=0.05,  # 5% Methanol in the liquid
        k=3.6,  # Approximation of relative volatility
        P=101325,  # Atmospheric pressure
    )

    distillation_1.simulate()
    # Display results
    # Second distillation column: Methanol-DCM separation
    flowIn2 = distillation_1.outs[0].F_mass  # Distillate from the first column

    distillation_2 = bst.units.BinaryDistillation(
        'distillation_2',
        ins=distillation_1.outs[0],  # Distillate from the first column
        outs=('distillate_2', 'bottoms_2'),
        LHK=('Dichloromethane', 'Methanol'),
        y_top=0.86,  # fraction DCM in the vapor
        x_bot=0.001,  # fraction DCM in the liquid
        k=3.18,       # 3.18 # Approximation of relative volatility for Methanol-DCM azeotrope
        P=101325,  # Atmospheric pressure
        Rmin=2     # Minimum reflux ratio
    )

    distillation_2.simulate()

    if pprint:
        # Display results
        # get the total flow rate from the feed stream
        # print("--- Chemical Plant Index (CECPI) ---")
        # # Check the reference Chemical Engineering Plant Index (CE)
        # distillation_ce = distillation_1.CE
        # print(f"reference CECPI used for cost estimation of distillation is: {distillation_ce}")
        # Check the current Chemical Plant Index (CPI)
        current_cpi = bst.CE
        print(f"Current Chemical Plant Index (CPI): {current_cpi} \n")


        print("--- First Distillation Column ---")
        print('Total flow rate in D1: {} kg/hr  \n'.format(feed.F_mass))
        distillation_1.show(flow='kg/hr')
        print(distillation_1.results())
        print("-------------------------------------------------\n")

        # Fraction split of each stream
        # Make a dataframe of the results, with columns as the streams (kg/h) and rows as the components
        components = ['Water', 'Methanol', 'Dichloromethane']

        data = {
            'feed': [feed.imass[component] for component in components],
            'distillate_1': [round(distillation_1.outs[0].imass[component]/feed.imass[component], 3) for component in components],
            'bottoms_1': [round(distillation_1.outs[1].imass[component]/feed.imass[component], 3)for component in components]
        }

        df = pd.DataFrame(data, index=components)
        print('')
        print(" --- Fraction split of each stream ---")
        print(df)
        print("-------------------------------------------------\n")

        print("--- Second Distillation Column ---")
        print('Feed flow rate in D2: {} kg/hr  \n'.format(flowIn2))
        distillation_2.show(flow='kg/hr')
        print(distillation_2.results())

        # Fraction split of each stream
        # Make a dataframe of the results, with columns as the streams (kg/h) and rows as the components
        components = ['Water', 'Methanol', 'Dichloromethane']
        data_2 = {
            'distillate_1': [distillation_1.outs[0].imass[component] for component in components],
            'distillate_2': [round(distillation_2.outs[0].imass[component]/distillation_1.outs[0].imass[component], 3) for component in components],
            'bottoms_2': [round(distillation_2.outs[1].imass[component]/distillation_1.outs[0].imass[component], 3) for component in components]
        }

        print(" --- Fraction split of each stream ---")
        df_2 = pd.DataFrame(data_2, index=components)
        print(df_2)
        print("-------------------------------------------------\n")



    # get the individual CAPEX of the two distillation columns
    CAPEX = [distillation_1.purchase_cost, distillation_2.purchase_cost]
    InFlow = [feed.F_mass, flowIn2]

    return CAPEX, InFlow, distillation_1, distillation_2


# Run the simulation
distillation_water_methanol_DCM(df=100, pprint=True)


# Uncomment the following code to plot the CAPEX vs flow rate for the two distillation columns
# capex_D1 = []
# capex_D2 = []
# flowIn_D1 = []
# flowIn_D2 = []
# for i in np.linspace(start=100, stop=200,num=50):
#     CAPEX, InFlow, _, _ = distillation_water_methanol_DCM(df=i, pprint=False)
#     capex_D1.append(CAPEX[0]*1e-6)
#     capex_D2.append(CAPEX[1]*1e-6)
#     flowIn_D1.append(InFlow[0]/1000)
#     flowIn_D2.append(InFlow[1]/1000)
#
# # plot the capex vs flowIn for the two distillation columns
# plt.figure(figsize=(10, 6))
# plt.plot(flowIn_D1, capex_D1, label='Distillation 1')
# plt.plot(flowIn_D2, capex_D2, label='Distillation 2')
# plt.xlabel('Flow rate (t/hr)')
# plt.ylabel('CAPEX (REACTANTS.USD)')
# plt.title('CAPEX vs Flow rate for the two distillation columns')
# plt.legend()
# plt.show()
