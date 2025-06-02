import logging
import os
import sys
import uuid
from types import TracebackType

from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout, QApplication
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QSize, QTimer

from outdoor.user_interface.utils.LCAWorker import LCAWorker

import bw2calc
import bw2calc as bc
import bw2data
import bw2data as bw
import pandas as pd

from outdoor.user_interface.data.CentralDataManager import CentralDataManager
from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO
from outdoor.user_interface.dialogs.LcaButton import LcaButton


class LCACalculationMachine:

    def __init__(self, centralDataManager):
        self.logger = logging.getLogger(__name__)
        self.centralDataManager = centralDataManager
        if not centralDataManager:
            self.logger.error("CentralDataManager is not set. Please initialize it before using LCACalculationMachine.")
            return

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
        Shows a spinning wheel animation during calculations.
        """
        # Create a custom dialog with spinning wheel
        spinner_dialog = QDialog()
        spinner_dialog.setWindowTitle("LCA Calculation")
        spinner_dialog.setWindowFlags(spinner_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint & ~Qt.WindowCloseButtonHint)
        spinner_dialog.setFixedSize(300, 150)

        # Create layout
        layout = QVBoxLayout(spinner_dialog)

        # Create label for the spinner
        spinner_label = QLabel()
        spinner_label.setAlignment(Qt.AlignCenter)

        # Create label for the text
        text_label = QLabel("Calculating LCAs. Please be patient, this may take a while...")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)

        # Add loading spinner animation
        gifPath = os.path.join(os.path.dirname(__file__), "loading.gif")
        movie = QMovie(gifPath)
        # If you don't have a GIF, you can use one from PyQt resources
        # or specify a full path like "C:/path/to/spinner.gif"
        movie.setScaledSize(QSize(50, 50))
        spinner_label.setMovie(movie)
        movie.start()

        # Add widgets to layout
        layout.addWidget(spinner_label)
        layout.addWidget(text_label)

        # Show the dialog
        spinner_dialog.show()
        QApplication.processEvents()

        try:
            # Do calculations
            self.logger.info("Collecting calculation-ready DTOs...")
            biglist = self.centralDataManager.componentData + self.centralDataManager.wasteData + self.centralDataManager.utilityData
            inventory = []
            incomplete = {}
            incomplete_count = 0

            # Rest of your calculation code...
            for component in biglist:
                component.LCA['Results'] = {}
                if len(component.LCA['exchanges']) > 0:
                    try:
                        inventory.append({self.outd.get(component.uid): 1})
                        self.logger.debug(f"Component {component.uid} has exchanges:{component.LCA['exchanges']}")
                    except Exception as e:
                        self.logger.warning(f"Looks like component {component.name} hasn't been saved to BW yet.")
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

            # Update status text
            text_label.setText(f"Found {len(inventory)} DTOs ready for calculation. Processing...")
            QApplication.processEvents()

            self.logger.info(f"Identified {len(inventory)} DTOs ready for calculation")
            self.logger.warning(f"There are {len(incomplete)} DTOs that are not ready for calculation: {incomplete}")
            self.logger.info(f"Beginning calculations. This may take a while.")

            # Continue with calculations
            execution = uuid.uuid4().__str__()
            methodconfs = self.getImpactMethods()
            calc_setup = {"inv": inventory, "ia": methodconfs}
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
                for item in biglist:
                    if k == item.uid:
                        item.LCA['Results'] = v
                        item.calculated = True

            self.logger.info("Calculations complete.")

            if write:
                text_label.setText("Writing results to file...")
                QApplication.processEvents()

                self.logger.info("Writing results to file.")
                import json
                out_file = open("mlca_dump.json", "w")
                json.dump(results, out_file, indent=4)
                self.logger.info("Results written to mlca_dump.json")

            text_label.setText("Calculations complete!")
            QTimer.singleShot(1000, spinner_dialog.accept)  # Close after 1 second



        except Exception as e:
            self.logger.error(f"Error during calculations: {e}")
            text_label.setText(f"Error during calculations: {str(e)}")
            QTimer.singleShot(3000, spinner_dialog.accept)  # Close after 3 seconds if error

        finally:
            # Always close the dialog when done
            if spinner_dialog.isVisible():
                spinner_dialog.accept()

            # update all LCA buttons in the application
            num_updated = self._updateAll_LCAButtons()
            self.logger.info(f"Updated the color of {num_updated} LCA buttons")

    def calculateAllLCAs_worker(self, write=False):
        """
        This method runs through every set of OutdoorDTOs and checks if they can have MLCAs run on them.
        Shows a spinner dialog during calculations. is deprecated in favor of calculateAllLCAs.

        This method was an attempt to use a worker thread for LCA calculations, but it is not used anymore.
        :param write:
        :return:
        """
        # spinner dialog
        dlg = QDialog()
        dlg.setWindowTitle("LCA calculation")
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowContextHelpButtonHint & ~Qt.WindowCloseButtonHint)
        dlg.setFixedSize(300, 150)

        vbox = QVBoxLayout(dlg)
        spinner = QLabel(alignment=Qt.AlignCenter)
        text = QLabel("Collecting DTOs …", wordWrap=True, alignment=Qt.AlignCenter)

        movie_path = os.path.join(os.path.dirname(__file__), "loading.gif")
        self._movie = QMovie(movie_path, parent=dlg)  # keep reference!
        self._movie.setScaledSize(QSize(50, 50))
        spinner.setMovie(self._movie)
        self._movie.start()

        vbox.addWidget(spinner)
        vbox.addWidget(text)
        dlg.show()

        # prepare data
        biglist = (self.centralDataManager.componentData +
                   self.centralDataManager.wasteData +
                   self.centralDataManager.utilityData)
        inventory = []
        incomplete = {}
        incomplete_count = 0

        # Rest of your calculation code...
        for component in biglist:
            component.LCA['Results'] = {}
            if len(component.LCA['exchanges']) > 0:
                try:
                    inventory.append({self.outd.get(component.uid): 1})
                    self.logger.debug(f"Component {component.uid} has exchanges:{component.LCA['exchanges']}")
                except Exception as e:
                    self.logger.warning(f"Looks like component {component.name} hasn't been saved to BW yet.")
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

        # Update status text
        text_label.setText(f"Found {len(inventory)} DTOs ready for calculation. Processing...")
        QApplication.processEvents()

        self.logger.info(f"Identified {len(inventory)} DTOs ready for calculation")
        self.logger.warning(f"There are {len(incomplete)} DTOs that are not ready for calculation: {incomplete}")
        self.logger.info(f"Beginning calculations. This may take a while.")


        QApplication.processEvents()

        # ---------- launch worker thread ----------
        self._worker = LCAWorker(biglist, inventory,
                                 self.getImpactMethods(), write)
        self._worker.progress.connect(text.setText)
        self._worker.finished.connect(lambda _: dlg.accept())
        self._worker.errored.connect(lambda msg:
                                     (text.setText("Error: " + msg),
                                      QTimer.singleShot(3000, dlg.accept)))
        self._worker.start()

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

    def _updateAll_LCAButtons(self):
        """
        Find and update all LcaButton instances across the entire application.
        """
        # Get all top-level windows instead of just the active one
        all_windows = QApplication.topLevelWidgets()

        if not all_windows:
            self.logger.warning("No top-level widgets found in the application")
            return 0

        lca_buttons = []

        # Search through all top-level windows
        for window in all_windows:
            # Find all LcaButton instances in this window
            buttons = window.findChildren(LcaButton)
            if buttons:
                lca_buttons.extend(buttons)

        # Update each button
        updated_count = 0
        for button in lca_buttons:
            button.changeColorBnt()
            updated_count += 1

        return updated_count

