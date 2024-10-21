class ReactionDTO:
    def __init__(self,
                 rowposition: int,
                 uid: str,
                 name: str = "",
                 reactants: dict = {},
                 products: dict = {},
                 reactionEquation: str = ""
                 ):

        self.rowPosition = rowposition
        self.uid = uid
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
