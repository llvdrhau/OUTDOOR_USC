class ComponentDTO:
    def __init__(self, rowposition: int, uid: str, name: str = "", lowerHeat: float = 0.0, heatCapacity: float = 0.0,
                 molecularWeight: float = 0.0, LCA: dict = {}):

        self.rowPosition = rowposition
        self.uid = uid
        self.name = name
        self.lowerHeat = lowerHeat
        self.heatCapacity = heatCapacity
        self.molecularWeight = molecularWeight
        self.LCA = LCA
        self.calculated = False

    def __getitem__(self, item):
        match item:
            case 0:
                return self.name
            case 1:
                return self.lowerHeat
            case 2:
                return self.heatCapacity
            case 3:
                return self.molecularWeight
            case 4:
                return self.LCA
            case 5:
                return self.uid
            case 6:
                return self.name
            case _:
                return self

    def as_dict(self):
        d = {
            "uuid": self.uid,
            "rowPosition": self.rowPosition,
            "name": self.name,
            "lowerHeat": str(self.lowerHeat),
            "heatCapacity": str(self.heatCapacity),
            "molecularWeight": str(self.molecularWeight),
            "LCA": self.LCA,
            "calculated": self.calculated,
        }
        return d

    def updateRow(self):
        self.rowPosition -= 1

    def upadateField(self, field, value):
        match field:
            case "rowPosition":
                self.rowPosition = value
            case "name":
                self.name = value
            case "lowerHeat":
                self.lowerHeat = value
            case "heatCapacity":
                self.heatCapacity = value
            case "molecularWeight":
                self.molecularWeight = value
            case "LCA":
                self.LCA = value
            case "calculated":
                self.calculated = True
            case "Results":
                self.results = value
