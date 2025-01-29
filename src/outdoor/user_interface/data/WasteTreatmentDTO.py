from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO


class WasteTreatmentDTO(OutdoorDTO):
    subDTO: {} # We need some nested DTOs because of how the Utilities table is set up

    def __init__(self, waste_name: str, uid: str, cost: float = 0, calculated: bool = False):

        # set initial values for utilityData and temperatureData if they are not provided
        super().__init__()
        self.name = waste_name
        self.cost = cost
        self.uid = uid
        self.calculated = calculated

    def as_dict(self):
        d = {
            "name": self.name,
            "cost": self.cost,
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

            case 'calculated':
                self.calculated = value
