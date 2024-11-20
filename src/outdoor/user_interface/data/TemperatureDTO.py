from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO


class TemperatureDTO(OutdoorDTO):
    subDTO: {} # We need some nested DTOs because of how the Utilities table is set up

    def __init__(self, temperatureName: str, uid: str, LCA: dict = {}, temp: float = 0, cost: float = 0, calculated: bool = False):

        # set initial values for utilityData and temperatureData if they are not provided
        super().__init__()
        self.name = temperatureName
        self.cost = cost
        self.temp = temp
        self.LCA = LCA
        self.uid = uid
        self.calculated = calculated

    def as_dict(self):
        d = {
            "name": self.name,
            "cost": self.cost,
            "temp": self.temp,
            "LCA": self.LCA,
            "uid": self.uid,
            "calculated": self.calculated
        }
        return d

    def upadateField(self, field, value):
        match field:
            case 'name':
                self.name = value
            case 'cost':
                self.cost = value
            case 'temp':
                self.temp = value
            case 'calculated':
                self.calculated = value
