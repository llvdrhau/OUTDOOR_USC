from enum import Enum
import ComponentDTO

class ProcessType(Enum):
    PHYSICAL = 1
    STOICHIOMETRIC = 2
    YIELD = 3
    GEN_HEAT = 4
    GEN_ELEC = 5
    GEN_CHP = 6

class ProcessDTO(object):
    def __init__(self, uid="", name="", type:ProcessType = ProcessType.PHYSICAL):
        self.uid = uid
        self.name = name
        self.type = type
        self.input_components: list[ComponentDTO] = []
        self.output_components: list[tuple[ComponentDTO, int, str]] = []

    def add_input_component(self, component: ComponentDTO):
        self.input_components.append(component)
        
