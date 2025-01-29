import biosteam as bst

# Define chemicals
water = bst.Chemical('Water')  # water for steam
hexane = bst.Chemical('Hexane')  # Built-in chemical
triolein = bst.Chemical(
    'Triolein',
    formula='C57H104O6',
    Tb=827.4,  # Boiling point in K
    Tm=278.0,  # Melting point in K
    Pc=1.02e6,  # Critical pressure in Pa
    Vc=2.19e-3,  # Critical volume in m³/mol
    omega=0.78,  # Acentric factor
    Hf=-197000,  # Heat of formation in J/mol
    phase='l',  # Non-volatile under typical conditions
)
print(hexane.MW)  # Molecular weight of hexane
print(triolein.MW)  # Molecular weight of triolein


# Compile chemicals
chemicals = bst.Chemicals([hexane, triolein, water])
chemicals.compile()

# Set thermo
bst.settings.set_thermo(chemicals)

# Define the feed stream
feed = bst.Stream('feed',
                  Hexane=1000,  # kg/h
                  Triolein=200,  # kg/h
                  water=0,
                  T=273+20,  # Temperature in K
                  P=101325,  # Pressure in Pa
                  units='kg/hr')

print(feed.imol)  # Check mole flows of each component
print(feed.imass)  # Check mass flows of each component

initPressure = feed.P

# Define the multi-effect evaporator
MEE = bst.MultiEffectEvaporator(
    'MEE',
    ins=feed,
    outs=('hexane_vapor', 'concentrated_liquid'),
    P=(initPressure, initPressure-2700, initPressure-5500),  # Pressures for 3 effects (Pa)
    V=0.99,  # Vaporize 90% of the feed
    V_definition='Overall',  # Fraction vaporized overall
)

# Simulate the MEE
MEE.simulate()

# Display results
MEE.show()
MEE.results()
