import numpy as np
import matplotlib.pyplot as plt

# Antoine coefficients for Methanol and Water (Pressure in bar, Temperature in K)
# https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Units=SI&Mask=4#Thermo-Phase
# https://webbook.nist.gov/cgi/cbook.cgi?ID=C75092&Units=SI&Mask=4#Thermo-Phase

antoine_params = {
    'Methanol': {'A': 5.20409, 'B': 1581.341, 'C': -33.50},  # Valid for T: 288.1 K to  356.83 K
    'Water': {'A': 4.6543, 'B': 1435.264, 'C': -64.848},     # Valid for T: 255.9 K to 373 K
    'Dichloromethane': {'A': 4.53691, 'B': 1327.016, 'C': -20.474}  # Valid for T: 233 to 313 K
}

def antoine_pressure(A, B, C, T):
    """
    Calculate saturation pressure (in bar) using Antoine equation.
    T: Temperature in Celsius.
    """
    return 10 ** (A - (B / (T + C)))


T = 85 + 273.15  # Temperature in Kelvin
P_total = 1.01325  # pressure in bar

# Calculate saturation pressures
P_sat_water = antoine_pressure(**antoine_params['Water'], T=T)
P_sat_methanol = antoine_pressure(**antoine_params['Methanol'], T=T)

# Calculate K values
K_water = P_sat_water / P_total
K_methanol = P_sat_methanol / P_total

# Relative volatility
relative_volatility = K_methanol / K_water

print(f"Saturation Pressure of Water: {P_sat_water:.2f} bar")
print(f"Saturation Pressure of Methanol: {P_sat_methanol:.2f} bar")
print(f"Relative Volatility (Methanol/Water): {relative_volatility:.2f}")


T = 30 + 273.15  # Temperature in Kelvin
P_total = 1.01325  # pressure in bar

# Calculate saturation pressures
P_sat_methanol = antoine_pressure(**antoine_params['Methanol'], T=T)
P_sat_DCM = antoine_pressure(**antoine_params['Dichloromethane'], T=T)

# Calculate K values
K_methanol = P_sat_methanol / P_total
K_DCM = P_sat_DCM / P_total

# Relative volatility
relative_volatility = K_DCM/K_methanol

print("")
print(f"Saturation Pressure of Methanol: {P_sat_methanol:.2f} bar")
print(f"Saturation Pressure of Dichloromethane: {P_sat_DCM:.2f} bar")
print(f"Relative Volatility (Methanol/Dichloromethane): {relative_volatility:.2f}")

