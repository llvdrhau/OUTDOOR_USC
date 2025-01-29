import biosteam as bst
from thermosteam import equilibrium as eq

# define chemicals
methanol = bst.Chemical('Methanol')
dichloromethane = bst.Chemical('Dichloromethane')

print('the Tb of methanol is: ', methanol.Tb-273.15)
print('the Tb of dichloromethane is: ', dichloromethane.Tb-273.15)

eq.plot_vle_binary_phase_envelope( ['Dichloromethane', 'Methanol'], P=101325)
