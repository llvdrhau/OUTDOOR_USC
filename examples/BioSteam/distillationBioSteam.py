import biosteam as bst

# Define chemicals
hexane = bst.Chemical('Hexane')
glycerol = bst.Chemical('Glycerol')
                      # search_ID=None,
                      # formula='C57H104O6',
                      # Tb=949.7,Tm=263.0,
                      # Pc=1.02e6,
                      # Vc=2.19e-3,
                      # omega=0.78,
                      # Hf=-1680.4,)


# Compile chemicals
chemicals = bst.Chemicals([hexane, glycerol])
chemicals.compile()

# Set thermo
bst.settings.set_thermo(chemicals)

# Define the feed stream
feed = bst.Stream('feed',
                  Hexane=1000,  # kg/h
                  Glycerol=200,  # kg/h
                  T=350,  # Feed temperature in K
                  P=101325,  # Pressure in Pa
                  units='kg/hr')

bp = feed.bubble_point_at_P()
feed.T = bp.T  # Feed at bubble point T

# Design the distillation column
column = bst.BinaryDistillation(
    'column',
    ins=feed,
    outs=('distillate', 'bottoms'),
    LHK=('Hexane', 'Glycerol'),  # Light and heavy keys
    y_top=0.95,  # 95% hexane in the distillate
    x_bot=0.05,  # 5% hexane in the bottoms
    k=1.2,  # Relative volatility factor
    P=101325,  # Operating pressure in Pa
)

# Simulate the column
column.simulate()

# Display results
column.show(flow='kg/hr')
print(column.results())
