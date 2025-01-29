import logging


class OutdoorDTO(object):
    name: str
    uid: str
    LCA: dict
    calculated: bool

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.LCA = {'Results': {},
                    'exchanges':{}}
        pass

    def getLCAImpacts(self) -> dict:
        if self.calculated:
            return {self.uid: self.LCA['Results']}
        else:
            self.logger.warning("No LCA impacts calculated")
            return {self.uid: {"NR": 0, "GWP": 0}}
