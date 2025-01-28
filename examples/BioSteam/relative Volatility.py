import numpy as np

# Antoine constants for Water and Methanol (P in mmHg, T in °C)
antoine_constants = {
    'Water': {'A': 8.07131, 'B': 1730.63, 'C': 233.426},
    'Methanol': {'A': 8.08097, 'B': 1582.27, 'C': 239.726}
}

def antoine_psat(A, B, C, T):
    """Calculate saturation pressure using Antoine equation."""
    return 10**(A - B / (T + C))  # Returns P_sat in mmHg

# Operating temperature and total pressure
T = 80  # Temperature in °C
P_total = 101.325 * 7.50062  # Convert kPa to mmHg

# Calculate saturation pressures
P_sat_water = antoine_psat(**antoine_constants['Water'], T=T)
P_sat_methanol = antoine_psat(**antoine_constants['Methanol'], T=T)

# Calculate K values
K_water = P_sat_water / P_total
K_methanol = P_sat_methanol / P_total

# Relative volatility
relative_volatility = K_methanol / K_water

print(f"Saturation Pressure of Water: {P_sat_water:.2f} mmHg")
print(f"Saturation Pressure of Methanol: {P_sat_methanol:.2f} mmHg")
print(f"Relative Volatility (Methanol/Water): {relative_volatility:.2f}")
