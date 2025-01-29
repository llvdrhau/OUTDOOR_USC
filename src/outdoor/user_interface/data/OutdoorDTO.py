import logging
#import bw2calc as bc

class OutdoorDTO(object):
    name: str
    uid: str
    LCA: dict
    calculated: bool

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.LCA = {'Results': {},
                    'exchanges':{}}

        # self.logger.warning("No LCA impacts calculated")
        # todo This empty dict needs to be initialized with the correct keys based on the LCA method used!
        # now always the same keys are used midpoints and endpoint methods, But future versions of the software may
        # use different keys.

        # possible solution??
        # mlca = bc.MultiLCA("setup")
        # for category in mlca.methods:
        #     nameCategory = category[3].split("(")[0]
        #     self.emptyResults[nameCategory] = 0

        self.emptyCategories = {
            'acidification: terrestrial': 0,
            'agricultural land occupation ': 0,
            'climate change: freshwater ecosystems': 0,
            'climate change: human health': 0,
            'climate change: terrestrial ecosystems': 0,
            'ecosystem quality': 0,
            'ecotoxicity: freshwater': 0,
            'ecotoxicity: marine': 0,
            'ecotoxicity: terrestrial': 0,
            'energy resources: non-renewable, fossil': 0,
            'eutrophication: freshwater': 0,
            'eutrophication: marine': 0,
            'fossil fuel potential ': 0,
            'freshwater ecotoxicity potential ': 0,
            'freshwater eutrophication potential ': 0,
            'global warming potential ': 0,
            'human health': 0,
            'human toxicity potential ': 0,
            'human toxicity: carcinogenic': 0,
            'human toxicity: non-carcinogenic': 0,
            'ionising radiation': 0,
            'ionising radiation potential ': 0,
            'land use': 0,
            'marine ecotoxicity potential ': 0,
            'marine eutrophication potential ': 0,
            'material resources: metals/minerals': 0,
            'natural resources': 0,
            'ozone depletion': 0,
            'ozone depletion potential ': 0,
            'particulate matter formation': 0,
            'particulate matter formation potential ': 0,
            'photochemical oxidant formation potential: ecosystems ': 0,
            'photochemical oxidant formation potential: humans ': 0,
            'photochemical oxidant formation: human health': 0,
            'photochemical oxidant formation: terrestrial ecosystems': 0,
            'surplus ore potential ': 0,
            'terrestrial acidification potential ': 0,
            'terrestrial ecotoxicity potential ': 0,
            'water consumption potential ': 0,
            'water use: aquatic ecosystems': 0,
            'water use: human health': 0,
            'water use: terrestrial ecosystems': 0}

        pass

    def getLCAImpacts(self) -> dict:
        if self.calculated:
            return {self.uid: self.LCA['Results']}
        else:
            return {self.uid: self.emptyCategories}
