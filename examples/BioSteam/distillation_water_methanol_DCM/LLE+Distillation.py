import biosteam as bst
import numpy as np
import pandas as pd

bst.settings.set_thermo(['Water', 'Methanol', 'Dichloromethane'])
df = 100
feed = bst.Stream('feed',
                  Water=80 * 1000 / df,  # Convert m3/h to kg/h using density (1 m3 = 1000 kg for water)
                  Methanol=80 * 791 / df,  # Methanol density ~791 kg/m3
                  Dichloromethane=500 * 1320 / df,  # Dichloromethane density ~1320 kg/m3
                  units='kg/hr')

solvent = bst.Stream('solvent', Water=0.1 * feed.F_mass, units='kg/hr')

MSMS1 = bst.MultiStageMixerSettlers('MSMS1', ins=(feed, solvent), outs=('extract', 'raffinate'), N_stages=5)
MSMS1.simulate()

# print results
print("Total mass of feed stream: {} kg/hr \n".format(feed.F_mass))
print("------- \n")
MSMS1.feed.show(flow='kg/hr')
MSMS1.solvent.show(flow='kg/hr')
print("------ \n")
MSMS1.extract.show(flow='kg/hr')
print("------ \n")
MSMS1.raffinate.show(flow='kg/hr')
print("")
print("------ \n")
components = ['Water', 'Methanol', 'Dichloromethane']
data = {
    'feed': [MSMS1.feed.imass[component] + MSMS1.solvent.imass[component]  for component in components],
    'extract': [round(MSMS1.extract.imass[component]/(feed.imass[component]+MSMS1.solvent.imass[component]), 3)
                for component in components],
    'raffinate': [round(MSMS1.raffinate.imass[component]/(feed.imass[component] + MSMS1.solvent.imass[component]), 3)
                  for component in components]
        }

# Create DataFrame
df = pd.DataFrame(data, index=components)
print('-------------------')
print("Mass fraction of each component in the extract and raffinate streams:")
print(df)
print('-------------------\n')

print("Results of the mixer-settler:")
print(MSMS1.results())

#  define the feed stream

feed_D1 = bst.Stream('feed',
                     Water= MSMS1.extract.imass['Water'],  # water
                     Methanol= MSMS1.extract.imass['Methanol'],  # Methanol
                     units='kg/hr')

# First distillation column: Water-Methanol-DCM separation
distillation_1 = bst.units.BinaryDistillation(
    'distillation_1',
    ins=feed_D1,
    outs=('distillate_1', 'bottoms_1'),
    LHK=('Methanol', 'Water'),
    y_top=0.95,  # 95% Methanol in the vapor
    x_bot=0.01,  # 5% Methanol in the liquid
    k=3.6,  # Approximation of relative volatility
    P=101325,  # Atmospheric pressure
)

distillation_1.simulate()


current_cpi = bst.CE
print(f"Current Chemical Plant Index (CPI): {current_cpi} \n")


print("--- First Distillation Column ---")
print('Total flow rate in D1: {} kg/hr  \n'.format(feed.F_mass))
distillation_1.show(flow='kg/hr')
print(distillation_1.results())
print("-------------------------------------------------\n")

# Fraction split of each stream
# Make a dataframe of the results, with columns as the streams (kg/h) and rows as the components
components = ['Water', 'Methanol']

data = {
    'feed': [distillation_1.feed.imass[component] for component in components],
    'distillate_1': [round(distillation_1.outs[0].imass[component]/distillation_1.feed.imass[component], 3)
                     for component in components],
    'bottoms_1': [round(distillation_1.outs[1].imass[component]/distillation_1.feed.imass[component], 3)
                  for component in components]
}

df = pd.DataFrame(data, index=components)
print('')
print(" --- Fraction split of each stream ---")
print(df)

