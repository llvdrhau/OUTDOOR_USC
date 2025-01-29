from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO


class UtilityDTO(OutdoorDTO):
    subDTO: {} # We need some nested DTOs because of how the Utilities table is set up

    def __init__(self, utility_name: str, uid: str, temperatureParameters:{} = {},cost: float = 0, co2: float = 0, fwd: float = 0, calculated: bool = False):

        # set initial values for utilityData and temperatureData if they are not provided
        super().__init__()
        self.name = utility_name
        self.cost = cost
        self.co2 = co2
        self.fwd = fwd
        self.uid = uid
        self.calculated = calculated

    def as_dict(self):
        d = {
            "name": self.name,
            "cost": self.cost,
            "co2": self.co2,
            "fwd": self.fwd,
            "LCA": self.LCA,
            "uid": self.uid,
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
            case 'co2':
                if value == "":
                    self.co2 = 0
                else:
                    value = float(value)
                self.co2 = value
            case 'fwd':
                if value == "":
                    self.fwd = 0
                else:
                    value = float(value)
                self.fwd = value
            case 'calculated':
                self.calculated = value
