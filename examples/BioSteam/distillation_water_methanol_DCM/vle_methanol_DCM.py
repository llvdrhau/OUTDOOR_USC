import biosteam as bst
from thermosteam import equilibrium as eq

# define chemicals
water = bst.Chemical('Water')
methanol = bst.Chemical('Methanol')
dichloromethane = bst.Chemical('Dichloromethane')

print('the Tb of water is (ºC): ', water.Tb-273.15)
print('the Tb of methanol is (ºC): ', methanol.Tb-273.15)
print('the Tb of dichloromethane is (ºC): ', dichloromethane.Tb-273.15)

eq.plot_vle_binary_phase_envelope( ['Methanol', 'Water'], P=101325)
eq.plot_vle_binary_phase_envelope( ['Dichloromethane', 'Methanol'], P=101325)
