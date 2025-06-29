from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO


class ReactionDTO(OutdoorDTO):
    def __init__(self, rowposition: int, uid: str, name: str = "", reactants: dict = {}, products: dict = {},
                 reactionEquation: str = ""):

        super().__init__()
        self.rowPosition = rowposition
        self.uid = uid
        self.oldName = None
        self.name = name
        self.reactants = reactants
        self.products = products
        self.reactionEquation = reactionEquation

    def __getitem__(self, item):
        match item:
            case 0:
                return self.name
            case 1:
                return self.reactants
            case 2:
                return self.products
            case 3:
                return self.reactionEquation
            case _:
                return self

    def as_dict(self):
        d = {
            "uuid": self.uid,
            "rowPosition": self.rowPosition,
            "name": self.name,
            "reactants": self.reactants,
            "products": self.products,
            "reactionEquation": self.reactionEquation
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
            case "reactants":
                self.reactants = value
            case "products":
                self.products = value
            case "reactionEquation":
                self.reactionEquation = value

    def makeStringEquation(self):
        """
        Extracts the data of the Reactants and Products tables and returns it as a string
        """
        reactants = self.reactants
        products = self.products

        reactants_str = " + ".join([f"{v} {k}" for k, v in reactants.items()])
        products_str = " + ".join([f"{v} {k}" for k, v in products.items()])
        reactionEquation = f"{reactants_str} -> {products_str}"

        self.reactionEquation = reactionEquation
