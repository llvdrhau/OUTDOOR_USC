import logging
import sys
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
        bw.projects.set_current(self.centralDataManager.BWPROJECTNAME)
        self.eidb = bw.Database('ecoinvent-3.9.1-consequential')
        self.bios = bw.Database('ecoinvent-3.9.1-biosphere')
        self.outd = bw.Database('outdoor')

    def possibleToCalculate(self):
        """
        This method runs through every set of OutdoorDTOs and checks if they can have MLCAs run on them.
        The concept is simple: count the total number of DTOs, and then count how many DTOs have exchanges. If there are
        fewer DTOs with exchanges than total, this means one of the DTOs hasn't been given any and thus that category isn't
        ready.
        """
        self.logger.info("Checking for valid categories...")
        required_components = len(self.centralDataManager.componentData)
        valid_components = 0
        missing_components = []
        for component in self.centralDataManager.componentData:
            if len(component.LCA['exchanges']) > 0:
                valid_components += 1
            else:
                missing_components.append(component.name)
        if valid_components == required_components & valid_components != 0:
            self.logger.info("All components are valid.")
            self.possibleLCAs['components'] = True
        else:
            if required_components == 0:
                self.logger.warning("No components to perform an LCA on.")
            else:
                self.logger.warning(f"There are {required_components - valid_components} components missing exchanges: {missing_components}")
        ##Check if waste can be calculated
        required_waste = len(self.centralDataManager.wasteData)
        valid_waste = 0
        missing_waste = []
        for waste in self.centralDataManager.wasteData:
            if len(waste.LCA['exchanges']) > 0:
                valid_waste += 1
            else:
                missing_waste.append(waste.name)
        if valid_waste == required_components & valid_waste != 0:
            self.logger.info("All wastes are valid.")
            self.possibleLCAs['waste'] = True
        else:
            self.logger.warning(f"There are {required_waste - valid_waste} wastes missing exchanges: {missing_waste}.")
        ##Check if utilities can be calculated
        required_utilities = len(self.centralDataManager.utilityData)
        valid_utilities = 0
        missing_utilities = []
        for utilities in self.centralDataManager.utilityData:
            if len(utilities.LCA['exchanges']) > 0:
                valid_utilities += 1
            else:
                missing_utilities.append(utilities.name)
        if valid_utilities == required_components & valid_utilities != 0:
            self.logger.info("All utilities are valid.")
            self.possibleLCAs['utilities'] = True
        else:
            self.logger.warning(f"There are {required_utilities - valid_utilities} utilities missing exchanges: {missing_utilities}.")

    def calculate(self, write=False):
        """
        This method checks which DTO categories are valid and then adds all of them to a single MLCA calculation_setup.
        After calculating all the LCAs that have been lined up it needs to put the data back into the DTO.LCA['Results'].
        To do this, the results are put into a dataframe, transposed, and put into a dictionary such that the key is a
        given DTO's UUID and the value can be dumped straight into the results dict.
        All MLCAs are calculated for "1", as in the UI the user inputs inventory-per-ton and the backend scales it automatically.
        :param self:
        :return:
        """
        self.logger.info("Calculation beginning. Please wait, this may take a moment.")
        midpoint = [m for m in bw.methods if "ReCiPe 2016 v1.03, midpoint (H)" in str(m) and not "no LT" in str(m)]
        endpoints = [m for m in bw.methods if "ReCiPe 2016 v1.03, endpoint (H)" in str(m) and not "no LT" in str(m)]
        methodconfs = midpoint + endpoints
        inventory = []

        for key, value in self.possibleLCAs.items():
            if value:
                match key:
                    case 'components':
                        for component in self.centralDataManager.componentData:
                            inventory.append({self.outd.get(component.uid):1})
                    case 'waste':
                        for component in self.centralDataManager.wasteData:
                            inventory.append({self.outd.get(component.uid): 1})
                    case 'utilities':
                        for component in self.centralDataManager.utilityData:
                            inventory.append({self.outd.get(component.uid): 1})

        calc_setup = {"inv": inventory, "ia": methodconfs}
        bw.calculation_setups["set"] = calc_setup
        mlca = bw2calc.MultiLCA("set")
        indic = []
        for f in mlca.func_units:
            for k in f:
                indic.append(k['code'])
        cols = []
        for c in mlca.methods:
            cols.append(c[3])

        results = pd.DataFrame(mlca.results, columns=cols, index=indic).transpose().to_dict()

        for k, v in results.items():
            for n in self.centralDataManager.componentData:
                if k in n.name:
                    n.LCA['Results'] = v
                    continue
            for n in self.centralDataManager.wasteData:
                if k in n.name:
                    n.LCA['Results'] = v
                    continue
            for n in self.centralDataManager.utilityData:
                if k in n.name:
                    n.LCA['Results'] = v
                    continue

        if write:
            self.logger.info("Writing results to file.")
            import json
            out_file = open("mlca_dump.json", "w")
            json.dump(results, out_file, indent=4)

        self.logger.info("Calculation complete.")
