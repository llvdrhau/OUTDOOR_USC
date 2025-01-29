import biosteam as bst
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def simulate_cost_vs_df(df_values):
    """
    Simulate equipment costs for Multi-Stage Mixer Settlers at different values of df (dilution factor).

    Parameters:
    df_values (list of int): List of dilution factors to test.

    Returns:
    pd.DataFrame: DataFrame containing df values and corresponding equipment costs.
    """
    # Initialize thermo
    bst.settings.set_thermo(['Water', 'Methanol', 'Dichloromethane'])

    # Store results
    results = []

    # Loop over different flowrate scaling factors
    for df in df_values:
        # Define feed stream
        feed = bst.Stream('feed',
                          Water=80 * 1000 / df,
                          Methanol=80 * 791 / df,
                          Dichloromethane=500 * 1320 / df,
                          units='kg/hr')

        # Define solvent stream
        solvent = bst.Stream('solvent', Water=0.1 * feed.F_mass, units='kg/hr')

        # Define Multi-Stage Mixer Settler
        MSMS1 = bst.MultiStageMixerSettlers('MSMS1', ins=(feed, solvent), outs=('extract', 'raffinate'), N_stages=5)
        MSMS1.simulate()

        # Store results
        results.append({
            'df': df,
            'Equipment Cost (USD)': MSMS1.purchase_cost,
            'flow': MSMS1.feed.F_mass + MSMS1.solvent.F_mass
        })

    # Convert to DataFrame
    return pd.DataFrame(results)

# Example usage
if __name__ == "__main__":
    df_values = [10, 50, 100, 200, 500, 1000]  # Different dilution factors
    results_df = simulate_cost_vs_df(df_values)

    # Display results
    print(results_df)

    # Plot the results
    plt.figure(figsize=(8, 6))
    plt.plot(results_df['flow'], results_df['Equipment Cost (USD)'], marker='o', label='Equipment Cost')
    plt.xlabel('Flow')
    plt.ylabel('Equipment Cost (USD)')
    plt.title('Equipment Cost vs Feed Flowrate (Scaling Factor)')
    plt.grid()
    plt.legend()
    plt.show()
