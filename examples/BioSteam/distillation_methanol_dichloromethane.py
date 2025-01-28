import biosteam as bst
from thermosteam import settings, Stream, Chemical, Chemicals



# Define chemicals
chemicals = Chemicals(['Water', 'Methanol', 'Dichloromethane'])
chemicals.compile()
settings.set_thermo(chemicals)

# Define feed stream
feed = Stream('feed',
              Water=80 * 1000,  # Convert m3/h to kg/h using density (1 m3 = 1000 kg for water)
              Methanol=80 * 791,  # Methanol density ~791 kg/m3
              Dichloromethane=500 * 1320,  # Dichloromethane density ~1320 kg/m3
              units='kg/hr')

# Define distillation column
# Feed: Stream to the column
# LHK: Light (Methanol) and Heavy (Water) keys
# y_top: Desired mole fraction of Methanol in distillate (80% = 0.8)
# k: Relative volatility estimator
# P: Operating pressure (default is 101325 Pa)

distillation = bst.units.BinaryDistillation(
    'distillation',
    ins=feed,
    outs=('distillate', 'bottoms'),
    LHK=('Methanol', 'Water'),
    y_top=0.90,  # 80% Methanol in the vapor
    x_bot=0.05,  # 10% Methanol in the liquid
    k=1.2,  # Approximation of relative volatility
    P=101325,  # Atmospheric pressure
)

# Simulate the system
distillation.simulate()

# Simulate the column
distillation.simulate()
# Display results
distillation.show(flow='kg/hr')
print(distillation.results())

# # Display results
# feed.show()
# distillation.outs[0].show()  # Distillate stream
# distillation.outs[1].show()  # Bottoms stream
#
# # Show detailed specifications for the distillation column
# distillation.diagram()
#
