import biosteam as bst
from biosteam import settings, Stream, Chemical, Chemicals, Thermo
from biosteam.units import MultiEffectEvaporator

# Define chemicals
water = bst.Chemical('Water')  # Add water
hexane = bst.Chemical('Hexane')  # Built-in chemical
#linoleic_acid = bst.Chemical('LinoleicAcid', Tb=230 + 273.15, Tc=613.15, Pc=2.24e6, MW=280.44548, phase='l')  # Custom chemical
triolein = bst.Chemical('Triolein')

# Compile chemicals
chemicals = Chemicals([hexane, triolein, water])
chemicals.compile()

# Set thermo object
thermo = Thermo(chemicals)
settings.set_thermo(thermo)

feed = Stream('feed', water=3000, Hexane=1000, Triolein=200,
              T=350,  # Temperature in K
              P=101325,  # Pressure in Pa
              units='kg/hr')

# Define feed stream (e.g., 1000 kg/hr, 80% hexane, 20% soybean oil)

# Define three-effect evaporator
multi_effect_evaporator = MultiEffectEvaporator('MEE',
                                                ins=feed,
                                                outs=('hexane_vapor', 'concentrated_oil'),
                                                V_definition='Overall',
                                                P=(101325, 50662),
                                                V=0.1)  # Pressures for 3 effects (Pa)

# Simulate the process
multi_effect_evaporator.simulate()
multi_effect_evaporator.show(flow='kg/hr')

# Display results
print(multi_effect_evaporator.results())
