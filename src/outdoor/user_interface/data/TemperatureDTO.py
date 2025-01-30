from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO


class TemperatureDTO(OutdoorDTO):
    subDTO: {} # We need some nested DTOs because of how the Utilities table is set up

    def __init__(self, temperatureName: str, uid: str, temp: float = 0, cost: float = 0, calculated: bool = False):

        # set initial values for utilityData and temperatureData if they are not provided
        super().__init__()
        self.name = temperatureName
        self.cost = cost
        self.temp = temp
        self.uid = uid
        self.calculated = calculated
        self.shortname = ""
        match temperatureName:
            case "Superheated steam":
                self.shortname = 'super'
            case "High pressure steam":
                self.shortname = 'high'
            case "Medium pressure steam":
                self.shortname = 'medium'
            case "Low pressure steam":
                self.shortname = 'low'
            case "Cooling water":
                self.shortname = 'cool'
            case _:
                self.shortname = ""

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
                if value == "":
                    self.cost = 0
                else:
                    value = float(value)
                self.cost = value
            case 'temp':
                if value == "":
                    self.temp = 0
                else:
                    value = float(value)
                self.temp = value
            case 'calculated':
                self.calculated = value
