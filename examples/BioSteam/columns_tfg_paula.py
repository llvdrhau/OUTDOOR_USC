import biosteam as bst
from biosteam import settings, Stream, Chemical, Chemicals, Thermo
from biosteam.units import MultiEffectEvaporator

# Define chemicals
water = bst.Chemical('Water')  # Add water
ethanol = bst.Chemical('Ethanol')  # Built-in chemical
acetate = bst.Chemical('Acetate')  # Custom chemical


# Compile chemicals
chemicals = bst.Chemicals([ethanol, acetate, water])
chemicals.compile()

# Set thermo
bst.settings.set_thermo(chemicals)

# Define the feed stream
feed = bst.Stream('feed',
                  Water=1000,  # kg/h
                  Ethanol=200,  # kg/h
                  Acetate=100,  # kg/h
                  Formate=50,  # kg/h
                  T= 35 + 273,  # Feed temperature in K
                  P=101325,  # Pressure in Pa
                  units='kg/hr')

# bp = feed.bubble_point_at_P()
# feed.T = bp.T  # Feed at bubble point T

# Design the distillation column
column = bst.BinaryDistillation(
    'column',
    ins=feed,
    outs=('distillate', 'bottoms'),
    LHK=('Hexane', 'Glycerol'),  # Light and heavy keys
    y_top=0.90,  # 95% hexane in the distillate
    x_bot=0.1,  # 5% hexane in the bottoms
    k=3.5,  # Relative volatility factor
    P=101325,  # Operating pressure in Pa
)

# Simulate the column
column.simulate()

# Display results
column.show(flow='kg/hr')
print(column.results())

