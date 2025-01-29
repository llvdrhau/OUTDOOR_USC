import biosteam as bst
import numpy as np
import pandas as pd

bst.settings.set_thermo(['Water', 'Methanol', 'Dichloromethane'])
df = 1
feed = bst.Stream('feed',
                  Water=80 * 1000 / df,  # Convert m3/h to kg/h using density (1 m3 = 1000 kg for water)
                  Methanol=80 * 791 / df,  # Methanol density ~791 kg/m3
                  Dichloromethane=500 * 1320 / df,  # Dichloromethane density ~1320 kg/m3
                  units='kg/hr')

solvent = bst.Stream('solvent', Water=0.1 * feed.F_mass, units='kg/hr')

MSMS1 = bst.MultiStageMixerSettlers('MSMS1', ins=(feed, solvent), outs=('extract', 'raffinate'), N_stages=5)
MSMS1.simulate()

# print results
MSMS1.feed.show(flow='kg/hr')
MSMS1.solvent.show(flow='kg/hr')
MSMS1.extract.show(flow='kg/hr')
MSMS1.raffinate.show(flow='kg/hr')
print("")
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
print(df)
print(MSMS1.results())
