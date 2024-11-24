import logging


class OutdoorDTO(object):
    name: str
    uid: str
    LCA: dict
    calculated: bool

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pass

    def getLCAImpacts(self) -> dict:
        if self.calculated:
            return {self.uid: {"NR": self.LCA['NR'], "GWP": self.LCA['GWP']}}
        else:
            self.logger.warning("No LCA impacts calculated")
            return {self.uid: {"NR": 0, "GWP": 0}}
