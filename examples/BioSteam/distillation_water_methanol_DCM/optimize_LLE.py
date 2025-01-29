import biosteam as bst
import numpy as np
import pandas as pd

# Set thermo and feed stream
bst.settings.set_thermo(['Water', 'Methanol', 'Dichloromethane'])
df = 1
feed = bst.Stream('feed',
                  Water=80 * 1000 / df,  # Convert m3/h to kg/h using density (1 m3 = 1000 kg for water)
                  Methanol=80 * 791 / df,  # Methanol density ~791 kg/m3
                  Dichloromethane=500 * 1320 / df,  # Dichloromethane density ~1320 kg/m3
                  units='kg/hr')

# Define range of solvent flow rates to test
solvent_ratios = np.linspace(0.001, 0.01, 20)  # Solvent-to-feed mass ratios (adjust as needed)
results = []

for ratio in solvent_ratios:
    # Adjust solvent flow rate based on the ratio
    solvent = bst.Stream('solvent', Water=feed.F_mass * ratio, units='kg/hr')

    # Create Multi-Stage Mixer Settler
    MSMS1 = bst.MultiStageMixerSettlers('MSMS1', ins=(feed, solvent), outs=('extract', 'raffinate'), N_stages=3)
    MSMS1.simulate()

    # Check DCM purity in raffinate
    raffinate_purity_dcm = MSMS1.raffinate.imass['Dichloromethane'] / MSMS1.raffinate.F_mass

    # Store results
    results.append({
        'Solvent Ratio': ratio,
        'DCM Purity (Raffinate)': raffinate_purity_dcm,
        'Solvent Flow Rate (kg/hr)': solvent.F_mass
    })

# Convert results to DataFrame
df_results = pd.DataFrame(results)

# Find optimal solvent ratio
optimal = df_results[df_results['DCM Purity (Raffinate)'] >= 0.95].iloc[0]  # First solvent ratio meeting the purity target
print(f"Optimal solvent-to-feed ratio: {optimal['Solvent Ratio']}")
print(f"Solvent flow rate: {optimal['Solvent Flow Rate (kg/hr)']:.2f}")
print(df_results)

# Plot results
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 6))
plt.plot(df_results['Solvent Ratio'], df_results['DCM Purity (Raffinate)'], marker='o', label='DCM Purity in Raffinate')
plt.axhline(0.95, color='red', linestyle='--', label='Target Purity (95%)')
plt.xlabel('Solvent-to-Feed Ratio')
plt.ylabel('DCM Purity in Raffinate')
plt.title('Optimization of Solvent Addition')
plt.grid()
plt.legend()
plt.show()
