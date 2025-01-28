import biosteam as bst

# Define chemicals
hexane = bst.Chemical('Hexane')  # Built-in chemical
triolein = bst.Chemical('Glycerol')  # Custom chemical
#    'Triolein',
#    formula='C57H104O6',
#    Tb=827.4,  # Boiling point in K
#    Tm=278.0,  # Melting point in K
#    Pc=1.02e6,  # Critical pressure in Pa (estimated)
#    Vc=2.19e-3,  # Critical volume in m³/mol (estimated)
#    omega=0.78,  # Acentric factor (estimated)
#    Hf=-197000,  # Heat of formation in J/mol (from ΔHf)
#    #phase='l',  # Triolein exists primarily in the liquid phase
#)

# Compile chemicals
chemicals = bst.Chemicals([hexane, triolein])
chemicals.compile()

# Set thermo
bst.settings.set_thermo(chemicals)

# Define feed stream (1000 kg/h hexane, 200 kg/h triolein)
feed = bst.Stream('feed',
                  Hexane=10,  # kg/h
                  Glycerol=2,  # kg/h
                  T=273+20,  # Temperature in K
                  P=101325,  # Pressure in Pa
                  units='t/hr')

# Define the flash unit
flash = bst.units.Flash('flash',
                        ins=feed,
                        outs=('vapor', 'liquid'),
                        P=101325,  # 95% Hexane in vapor
                        T=hexane.Tb-20)  # Vaporize 95% of the feed

# Simulate the flash unit
flash.simulate()

# Display results
flash.show(flow='t/hr')
print(flash.results())
