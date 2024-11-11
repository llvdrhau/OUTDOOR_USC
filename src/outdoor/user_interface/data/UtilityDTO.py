from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO


class UtilityDTO(OutdoorDTO):
    def __init__(self, utilityData: dict = {}, temperatureData: dict = {}):

        # set initial values for utilityData and temperatureData if they are not provided
        super().__init__()
        if not utilityData:

            # ["Temperature (°C)", "Costs (€/MWh)"]
            # ["Costs (€/MWh)", "CO2 Emissions (t/MWh)", "Fresh water depletion (t/MWh)", "LCA"]

            self.utilityParameters = {"Costs (€/MWh)": [120, 0, 35], # costs in €/MWh
                              "CO2 Emissions (t/MWh)": [0.33, 0.248, 0.1], # CO2 emissions in t/MWh
                              "Fresh water depletion (t/MWh)": [0, 0, 0], # Fresh water depletion in t/MWh
                              "LCA": [0, 0, 0]} # Life cycle assessment in €/MWh Place holder values
        if not temperatureData:
            self.temperatureParameters = {
                "Temperature (°C)": { # temperatures in °C
                    "Superheated steam": 600,
                    "High pressure steam": 330,
                    "Medium pressure steam": 220,
                    "Low pressure steam": 130,
                    "Cooling water": 15
                },
                "Costs (€/MWh)": {
                    "Superheated steam": 34,  # costs in €/MWh
                    "High pressure steam": 32,
                    "Medium pressure steam": 30,
                    "Low pressure steam": 29,
                    "Cooling water": 0.22
                }
            }





