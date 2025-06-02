from PyQt5.QtCore import QThread, pyqtSignal
import bw2data as bw
import bw2calc
import json


class LCAWorker(QThread):
    progress = pyqtSignal(str)        # emits status strings
    finished = pyqtSignal(dict)       # emits final results
    errored  = pyqtSignal(str)        # emits error messages

    def __init__(self, biglist, inventory, getFunction, write=False, parent=None):
        super().__init__(parent)
        self.biglist    = biglist
        self.inventory  = inventory
        self.getFunction = getFunction
        self.write      = write

    # ------------------------------------------------------------------
    def run(self):
        try:

            # Continue with calculations
            execution = uuid.uuid4().__str__()
            methodconfs = self.getImpactMethods()
            calc_setup = {"inv": self.inventory, "ia": methodconfs}
            bw.calculation_setups[execution] = calc_setup

            text_label.setText("Please wait, calculating environmental impacts of each component \n ...")
            QApplication.processEvents()

            mlca = bw2calc.MultiLCA(execution)

            indic = []
            for f in mlca.func_units:
                for k in f:
                    indic.append(k['code'])
            cols = []
            for c in mlca.methods:
                cols.append(c[3])

            results = pd.DataFrame(mlca.results, columns=cols, index=indic).transpose().to_dict()

            text_label.setText("Processing results...")
            QApplication.processEvents()

            for k, v in results.items():
                self.logger.debug(f"Calculation results for {k}: {v}")
                for item in self.biglist:
                    if k == item.uid:
                        item.LCA['Results'] = v
                        item.calculated = True

            self.logger.info("Calculations complete.")

            if self.write:
                text_label.setText("Writing results to file...")
                QApplication.processEvents()

                self.logger.info("Writing results to file.")
                out_file = open("mlca_dump.json", "w")
                json.dump(results, out_file, indent=4)
                self.logger.info("Results written to mlca_dump.json")

            text_label.setText("Calculations complete!")
            QTimer.singleShot(1000, spinner_dialog.accept)  # Close after 1 second

        except Exception as e:
            self.logger.error(f"Error during calculations: {e}")
            #text_label.setText(f"Error during calculations: {str(e)}")
            QTimer.singleShot(3000, spinner_dialog.accept)  # Close after 3 seconds if error



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
            results[meth[2]] = (meth[3].split("(")[1].split(")")[0] if "midpoint" in str(meth) else meth[3],
                                bw.Method(meth).metadata.get("unit"))
        return results
