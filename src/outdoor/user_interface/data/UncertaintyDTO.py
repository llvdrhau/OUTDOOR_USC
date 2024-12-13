import logging
from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO

class UncertaintyDTO(OutdoorDTO):
    def __init__(self, rowPosition: int = None, uid: str = "",
                parameterType: str = "", unitUid: str = "", componentName: str = "",
                reactionUid: str = "", uncertaintyFactor: float = 0.0, distributionType: str = "Uniform"):

        # add the logger
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.rowPosition = rowPosition
        self.uid = uid
        self.parameterType = parameterType
        self.unitUid = unitUid
        self.targetUnitProcess = ""
        self.componentName = componentName
        self.reactionUid = reactionUid
        self.uncertaintyFactor = uncertaintyFactor
        self.distributionType = distributionType

    def as_dict(self):
        d = {
            "uuid": self.uid,
            "rowPosition": self.rowPosition,
            "parameterType": self.parameterType,
            "unitUid": self.unitUid,
            "targetUnitProcess": self.targetUnitProcess,
            "componentName": self.componentName,
            "reactionUid": self.reactionUid,
            "uncertaintyFactor": str(self.uncertaintyFactor),
            "distributionType": self.distributionType,
        }
        return d

    def updateRow(self):
        self.rowPosition -= 1

    def upadateField(self, field, value):
        match field:
            case "rowPosition":
                self.rowPosition = value
            case "parameterType":
                self.parameterType = value
            case "unitUid":
                self.unitUid = value
            case "componentName":
                self.componentName = value
            case "targetUnitProcess":
                self.targetUnitProcess = value
            case "reactionUid":
                self.reactionUid = value
            case "uncertaintyFactor":
                self.uncertaintyFactor = float(value)
            case "distributionType":
                self.distributionType = value
