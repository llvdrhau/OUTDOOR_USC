import logging
import sys
import uuid
from types import TracebackType

import bw2calc
import bw2calc as bc
import bw2data
import bw2data as bw
import pandas as pd

from outdoor.user_interface.data.CentralDataManager import CentralDataManager
from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO

class LCACalculationMachine:
    def __init__(self, centralDataManager):
        self.logger = logging.getLogger(__name__)
        self.centralDataManager = centralDataManager
        self.possibleLCAs = {
            "components":False,
            "waste":False,
            "utilities":False,
        }
        # TODO: second todo here because clearly one in LCADialog wasn't enough
        bw.projects.set_current("superstructure")
        self.eidb = bw.Database('ecoinvent-3.9.1-consequential')
        self.bios = bw.Database('ecoinvent-3.9.1-biosphere')
        self.outd = bw.Database('outdoor')

    def calculateAllLCAs(self, write=False):
        """
        This method runs through every set of OutdoorDTOs and checks if they can have MLCAs run on them.
        The concept is simple: count the total number of DTOs, and then count how many DTOs have exchanges. If there are
        fewer DTOs with exchanges than total, this means one of the DTOs hasn't been given any and thus that category isn't
        ready.
        """
        self.logger.info("Collecting calculation-ready DTOs...")
        biglist = self.centralDataManager.componentData + self.centralDataManager.wasteData + self.centralDataManager.utilityData
        inventory = []
        incomplete = {}
        incomplete_count = 0
        for component in biglist:
            component.LCA['Results'] = {}
            if len(component.LCA['exchanges']) >0:
                try:
                    inventory.append({self.outd.get(component.uid): 1})
                    self.logger.debug(f"Component {component.uid} has exchanges:{component.LCA['exchanges']}")
                except Exception as e:
                    self.logger.warning(f"Looks like component {component.name} hasn't been saved to BW yet. Try reopening the LCA dialog and clicking the 'Persist' button.")
                    incomplete_count += 1
                    if component.__class__.__name__ in incomplete:
                        incomplete[component.__class__.__name__].append(component.name)
                    else:
                        incomplete[component.__class__.__name__] = [component.name]
            else:
                incomplete_count += 1
                if component.__class__.__name__ in incomplete:
                    incomplete[component.__class__.__name__].append(component.name)
                else:
                    incomplete[component.__class__.__name__] = [component.name]
        self.logger.info(f"Identified {len(inventory)} DTOs ready for calculation")
        self.logger.warning(f"There are {len(incomplete)} DTOs that are not ready for calculation: {incomplete}")
        self.logger.info(f"Beginning calculations. This may take a while.")
        execution = uuid.uuid4().__str__()
        methodconfs = self.getImpactMethods()
        calc_setup = {"inv": inventory, "ia": methodconfs}
        bw.calculation_setups[execution] = calc_setup
        mlca = bw2calc.MultiLCA(execution)
        indic = []
        for f in mlca.func_units:
            for k in f:
                indic.append(k['code'])
        cols = []
        for c in mlca.methods:
            cols.append(c[3])

        results = pd.DataFrame(mlca.results, columns=cols, index=indic).transpose().to_dict()
        biglist = self.centralDataManager.componentData + self.centralDataManager.wasteData + self.centralDataManager.utilityData
        for k, v in results.items():
            self.logger.debug(f"Calculation results for {k}: {v}")
            for item in biglist:
                if k == item.uid:
                    item.LCA['Results'] = v
                    item.calculated = True

        if write:
            self.logger.info("Writing results to file.")
            import json
            out_file = open("mlca_dump.json", "w")
            json.dump(results, out_file, indent=4)

    def getImpactMethods(self) -> list:
        midpoint = [m for m in bw.methods if "ReCiPe 2016 v1.03, midpoint (H)" in str(m) and not "no LT" in str(m)]
        endpoints = [m for m in bw.methods if
                     "ReCiPe 2016 v1.03, endpoint (H)" in str(m) and not "no LT" in str(m) and "total" in str(m)]
        methodconfs = midpoint + endpoints
        return methodconfs

    def getImpactDict(self):
        methods = self.getImpactMethods()
        results = {}
        for meth in methods:
            results[meth[2]] = (meth[3].split("(")[1].split(")")[0] if "midpoint" in str(meth) else meth[3], bw.Method(meth).metadata.get("unit"))
        return results

