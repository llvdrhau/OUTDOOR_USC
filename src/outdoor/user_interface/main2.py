import os
import pickle
import sys

from PyQt5.QtWidgets import QTabWidget, QApplication, QMainWindow, QAction, QFileDialog

from data.CentralDataManager import CentralDataManager
from data.CentralDataManager import OutputManager
from data.superstructure_frame import SuperstructureFrame
from src.outdoor.outdoor_core.input_classes.superstructure import Superstructure

from outdoor.user_interface.dialogs.ConfigEditor import ConfigEditor
from src.outdoor.outdoor_core.input_classes.unit_operations.library.pool import ProductPool
from src.outdoor.outdoor_core.input_classes.unit_operations.library.source import Source
from src.outdoor.outdoor_core.input_classes.unit_operations.library.stoich_reactor import StoichReactor
from src.outdoor.outdoor_core.input_classes.unit_operations.library.yield_reactor import YieldReactor
from src.outdoor.outdoor_core.input_classes.unit_operations.library.distributor import Distributor
from src.outdoor.outdoor_core.input_classes.unit_operations.library.splitter import Splitter
from src.outdoor.outdoor_core.input_classes.unit_operations.library.furnace import HeatGenerator
from src.outdoor.outdoor_core.input_classes.unit_operations.library.turbine import ElectricityGenerator
from src.outdoor.outdoor_core.input_classes.unit_operations.library.CHP import CombinedHeatAndPower
from src.outdoor.outdoor_core.input_classes.unit_operations.superclasses.physical_process import PhysicalProcess

from outdoor.user_interface.WelcomeTab import WelcomeTab
from tabs.ComponentsTab import ComponentsTab
from tabs.GeneralSystemDataTab import GeneralSystemDataTab
from tabs.UtilityTab import UtilityTab
from tabs.SuperstructureMappingTab import SuperstructureMappingTab
from tabs.ReactionTab import ReactionsTab
from tabs.ProjectDescriptionTab import ProjectDescriptionTab
from src.outdoor.user_interface.utils.OutdoorLogger import outdoorLogger
from outdoor.user_interface.data.ProcessDTO import ProcessType

import logging

# Get the current working directory
current_path = os.getcwd()
# Print the current working directory
print(f"Current working directory: {current_path}")


class MainWindow(QMainWindow):  # Inherit from QMainWindow

    """
    This class creates the main window for the application and sets up the menu bar and tabbed interface.
    """

    def __init__(self):
        super().__init__()

        # add the logger
        self.logger = outdoorLogger(name='outdoor_logger', level=logging.DEBUG)

        self.setWindowTitle("OUTDOOR 2.0 - Open Source Process Simulator")
        self.setGeometry(100, 100, 1200, 800)
        self.ProjectName = ""
        self.ProjectPath = ""
        self.centralDataManager = CentralDataManager()  # Initialize the data manager
        self.outputManager = OutputManager()  # Initialize the output manager

        menu_bar = self.menuBar()
        fileMenu = menu_bar.addMenu('File')

        # Creating actions for the 'File' menu
        openAction = QAction('Open', self)
        self.saveAction = QAction('Save', self)
        if self.ProjectName == '':
            self.saveAction.setDisabled(True)
        saveAsAction = QAction('Save As', self)

        # Adding actions to the 'File' menu
        fileMenu.addAction(openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(saveAsAction)

        # Connect actions to methods here (you'll implement these methods)
        openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        saveAsAction.triggered.connect(self.saveAsFile)

        editMenu = menu_bar.addMenu('Edit')
        self.editAction = QAction('Configuration', self)
        if self.ProjectName == '':
            self.editAction.setDisabled(True)
        self.editAction.triggered.connect(self.editConfigs)
        editMenu.addAction(self.editAction)
        self.initTabs()

    def enableSave(self):
        self.saveAction.setEnabled(True)
        self.editAction.setEnabled(True)

    def openFile(self):
        #There has to be a way to handle "i cancelled the load" that's not this trash
        filepath = QFileDialog(self, caption='Open Saved Project', filter='*.outdr', directory='data/frames')
        filepath.exec()

        self.ProjectPath = filepath.selectedFiles()[0]
        self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]
        with open(self.ProjectPath, 'rb') as file:
            self.centralDataManager = pickle.load(file)
        self.centralDataManager.metadata["PROJECT_NAME"] = self.ProjectName
        self.centralDataManager.loadConfigs()
        self.initTabs()
        self.enableSave()
        self.logger.info("Opened File: {}".format(self.ProjectPath))

        # todo: set this in appropriate place (save methods), just for ease of use for now to test the superstructure
        self._makeSuperstructureObject()

        # comment for now to make bebugging easier
        # try:
        #     #if filepath.accept():
        #     self.ProjectPath = filepath.selectedFiles()[0]
        #     self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]
        #     with open(self.ProjectPath, 'rb') as file:
        #         self.centralDataManager = pickle.load(file)
        #     self.centralDataManager.data["PROJECT_NAME"] = self.ProjectName
        #     self.centralDataManager.loadConfigs()
        #     self.initTabs()
        #     self.enableSave()
        #     self.logger.info("Opened File: {}".format(self.ProjectPath))
        # except Exception as e:
        #     self.logger.error("File opening cancelled: {}".format(e))

    def saveFile(self):
        """
        Save the current project to the file path specified in self.ProjectPath
        :return:
        """
        for unitDTO in self.centralDataManager.unitProcessData.values():
            unitDTO.exitPorts = []
            unitDTO.entryPorts = []

        with open(self.ProjectPath, 'wb') as file:
            pickle.dump(self.centralDataManager, file)
        print("Saved File: ", self.ProjectPath)
        self.centralDataManager.metadata["PROJECT_NAME"] = self.ProjectName

        # generate the superstructure frame
        self._makeSuperstructureObject()
        #Frame = SuperstructureFrame()
        #Frame.constructSuperstructureFrame(self.centralDataManager)

    def saveAsFile(self):
        """
        Save the current project to a new file path
        :return:
        """
        try:
            self.ProjectPath = QFileDialog.getSaveFileName(self, 'Save As', filter='*.outdr', directory='data/frames')[
                0]
            self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]

            # temporary fix for a bug during saving: can not pickle QT objects!!
            # I'm not using the DTO to acess the ports so this is relatively safe for now
            for unitDTO in self.centralDataManager.unitProcessData.values():
                unitDTO.exitPorts = []
                unitDTO.entryPorts = []

            with open(self.ProjectPath, 'wb') as file:
                pickle.dump(self.centralDataManager, file)
            self.setWindowTitle(self.ProjectName)
            self.enableSave()
            print("Saved File: ", self.ProjectPath)
            self.centralDataManager.metadata["PROJECT_NAME"] = self.ProjectName

        except Exception as e:
            self.logger.error("Save cancelled.", e)

    def editConfigs(self):
        dialog = ConfigEditor(self.centralDataManager)
        if dialog.exec_():
            print("Editing configs")
        else:
            print("Editing configs concluded.")
        self.initTabs()

    def initTabs(self):
        # Create a QTabWidget and set it as the central widget
        tabWidget = QTabWidget()
        self.setCentralWidget(tabWidget)

        # Create the tabs
        createWelcomeTab = WelcomeTab(centralDataManager=self.centralDataManager)
        projectDescriptionTab = ProjectDescriptionTab(centralDataManager=self.centralDataManager)
        generalSystemDataTab = GeneralSystemDataTab(centralDataManager=self.centralDataManager,
                                                    outputManager=self.outputManager)
        componentsTab = ComponentsTab(centralDataManager=self.centralDataManager)
        reactionsTab = ReactionsTab(centralDataManager=self.centralDataManager)
        utilityTab = UtilityTab(centralDataManager=self.centralDataManager)
        superstructureMappingTab = SuperstructureMappingTab(centralDataManager=self.centralDataManager,
                                                            outputManager=self.outputManager)

        # Add tabs to the QTabWidget
        tabWidget.addTab(createWelcomeTab, "Welcome")
        tabWidget.addTab(projectDescriptionTab, "Project Description")
        tabWidget.addTab(generalSystemDataTab, "General System Data")
        tabWidget.addTab(componentsTab, "Chemical Components")
        tabWidget.addTab(reactionsTab, "Reactions")
        tabWidget.addTab(utilityTab, "Utilities")
        tabWidget.addTab(superstructureMappingTab, "Superstructure Mapping")
        if self.ProjectName != '':
            self.setWindowTitle(f'OUTDOOR 2.0 - {self.ProjectName}')

    def _makeSuperstructureObject(self):
        """
        This methode makes the superstructure object used to run to OUTDOOR in the
        back end. The old functions used to wrapp the data from excel to the superstructure object should come here
        :return:
        """

        # make a dictionary of the reaction names and the corresponding reaction dto for easy access later on
        self.reactionDict = {dto.name: dto for dto in self.centralDataManager.reactionData}
        self.reactionNumberDict = {dto.name: i+1 for i, dto in enumerate(self.centralDataManager.reactionData)}

        # make the initial object:
        self.superstructureObject = self._setGeneralData()
        self._setUnitProcessData()

    def _setGeneralData(self):
        """
        Initiates the superstructure object and fills in general data

        :return: Superstructure Object
        """
        # model name
        modelName = self.centralDataManager.generalData['projectName']

        # retrieve the objective
        objectiveFull = self.centralDataManager.generalData['objective']
        objectiveMap = {'EBIT: Earnings Before Income Taxes': 'EBIT',
                        "NPC: Net Production Costs": "NPC",
                        "NPE: Net Produced CO2 Emissions": "NPE",
                        "FWD: Freshwater Demand": "FWD"}

        objective = objectiveMap[objectiveFull]

        productDriven = self.centralDataManager.generalData['productDriver']

        mainProduct = self.centralDataManager.generalData['mainProduct']
        if mainProduct == '':
            mainProduct = None
        productLoad = self.centralDataManager.generalData['productLoad']

        if productLoad == '':
            productLoad = None
        else:
            productLoad = float(productLoad)

        optimizationMode = self.centralDataManager.generalData['optimizationMode']

        obj = Superstructure(ModelName=modelName,
                             Objective=objective,
                             productDriver=productDriven,
                             MainProduct=mainProduct,
                             ProductLoad=productLoad,
                             OptimizationMode=optimizationMode)

        opH = float(self.centralDataManager.generalData['operatingHours'])
        obj.set_operatingHours(opH)

        year = int(self.centralDataManager.generalData['yearOfStudy'])
        obj.set_cecpi(year)

        interestRate = float(self.centralDataManager.generalData['interestRate'])
        obj.set_interestRate(interestRate)

        obj.set_linearizationDetail()

        obj.set_omFactor(0.04)  # as default, nornally it is specified per unit process

        # Heat Pump values
        heatPumpSwitch = self.centralDataManager.generalData['heatPumpSwitch']
        if heatPumpSwitch == 'Yes':
            COP = float(self.centralDataManager.generalData['COP'])
            Costs = float(self.centralDataManager.generalData['cost'])
            Lifetime = float(self.centralDataManager.generalData['lifetime'])

            T_IN = self.centralDataManager.generalData['TIN']
            T_OUT = self.centralDataManager.generalData['TOUT']
            if T_IN == '' or T_OUT == '':
                T_IN = 0
                T_OUT = 0
                if T_IN == '':
                    errorTemp = 'Inlet Temperature'
                else:
                    errorTemp = 'Outlet Temperature'
                self.logger.error("{} for the Heat Pump is not set correctly \n"
                                  "Defaulted to T_in = 0 and T_out = 0.".format(errorTemp))

            obj.set_heatPump(Costs,
                             Lifetime,
                             COP,
                             T_IN,
                             T_OUT
                             )

        # ADD LISTS OF COMPONENTS, ETC.
        # ----------------------------
        utilityNames = ['Electricity', 'Heat', 'Chilling']
        obj.add_utilities(utilityNames)

        componentList = [dto.name for dto in self.centralDataManager.componentData]
        obj.add_components(componentList)

        reactionNumberList = [i + 1 for i in range(len(self.centralDataManager.reactionData))]
        obj.add_reactions(reactionNumberList)

        # todo this seems redundant I don't know why this is done, must optimize this in the future
        reactantsList = []
        for dto in self.centralDataManager.reactionData:
            key = list(dto.reactants.keys())[0]
            reactantsList.append(key)
        obj.add_reactants(reactantsList)

        lhvDict = {dto.name: float(dto.lowerHeat) for dto in self.centralDataManager.componentData}
        obj.set_lhv(lhvDict)

        mwDict = {dto.name: float(dto.molecularWeight) for dto in self.centralDataManager.componentData}
        obj.set_mw(mwDict)

        cpDict = {dto.name: float(dto.heatCapacity) for dto in self.centralDataManager.componentData}
        obj.set_cp(cpDict)

        # ADD OTHER PARAMETERS
        # ---------------------
        utilityDTO = self.centralDataManager.utilityData
        co2Factors = utilityDTO.utilityParameters['CO2 Emissions (t/MWh)']
        emissionsUtilityDict = {utility: float(co2Factors[i]) for i, utility in enumerate(utilityNames)}
        obj.set_utilityEmissionsFactor(emissionsUtilityDict)

        freshWaterFactors = utilityDTO.utilityParameters['Fresh water depletion (t/MWh)']
        emissionsWaterUtilityDict = {utility: float(freshWaterFactors[i]) for i, utility in enumerate(utilityNames)}
        obj.set_utilityFreshWaterFator(emissionsWaterUtilityDict)

        co2ComponentList = [0 for dto in self.centralDataManager.componentData]
        # replaced by the lca data not important any more, just make a list of zeros to not break the code
        obj.set_componentEmissionsFactor(co2ComponentList)

        # get the price of cooling water and the various steam prices
        superHeatedSteam = utilityDTO.temperatureParameters['Costs (€/MWh)']['Superheated steam']
        highPressureSteam = utilityDTO.temperatureParameters['Costs (€/MWh)']['High pressure steam']
        mediumPressureSteam = utilityDTO.temperatureParameters['Costs (€/MWh)']['Medium pressure steam']
        lowPressureSteam = utilityDTO.temperatureParameters['Costs (€/MWh)']['Low pressure steam']
        costCooling = utilityDTO.temperatureParameters['Costs (€/MWh)']['Cooling water']
        # set the cost prices
        dictTemperaturePrices = {'super': superHeatedSteam,
                                 'high': highPressureSteam,
                                 'medium': mediumPressureSteam,
                                 'low': lowPressureSteam}

        obj.temperaturePricesDict = dictTemperaturePrices
        obj.set_deltaCool(costCooling)

        temperatureList = list(utilityDTO.temperatureParameters['Temperature (°C)'].values())
        priceList = list(utilityDTO.temperatureParameters['Costs (€/MWh)'].values())
        obj.set_heatUtilities(temperatureList, priceList)

        utilityPrices = {'Electricity': utilityDTO.utilityParameters['Costs (€/MWh)'][0],
                         'Chilling': utilityDTO.utilityParameters['Costs (€/MWh)'][-1]}
        obj.set_deltaUt(utilityPrices)

        return obj

    def _setUnitProcessData(self):
        """
        Continue filling in the superstructure with data from unit operations
        :return: Superstructure Object
        """
        self.processUnit_ObjectList = []  # in outdoor this is PU_ObjectList in main.py in the excel wrapper
        unitDTODictionary = self.centralDataManager.unitProcessData
        for uuid, dto in unitDTODictionary.items():
            if dto.type == ProcessType.INPUT:
                InputObject = self._setInputData(dto)
                self.processUnit_ObjectList.append(InputObject)
            elif dto.type == ProcessType.OUTPUT:
                OutputObject = self._setOutputData(dto)
                self.processUnit_ObjectList.append(OutputObject)
            elif dto.type == ProcessType.DISTRIBUTOR:
                DistributorObject = self._setDistributionData(dto)
                self.processUnit_ObjectList.append(DistributorObject)
            elif dto.type.value in list(range(1, 7)):  # not an input, output or distributor
                ProcessObject = self._setProcessData(dto)
                self.processUnit_ObjectList.append(ProcessObject)

    def _setInputData(self, dto):
        """
        Continue filling in the superstructure with data from input units
        :return: Superstructure Object
        """
        # todo you might need to change the number to hex code instead of using the UID directly

        # Initiate object
        InputObject = Source(Name=dto.name, UnitNumber=dto.uid)

        # Set of default vales of the data if not provided
        default_lowerLimit = 0
        default_upperLimit = 100000
        default_costs = 0
        default_emissionFactor = 0
        default_freshwaterFactor = 0

        upperLimit = dto.dialogData['upperLimit']
        lowerLimit = dto.dialogData['lowerLimit']
        composition = dto.dialogData['components']
        dicComposition = {comp[0]: float(comp[1]) for comp in composition}
        cost = dto.dialogData['priceInput']

        # these have been deleted in the new version, replaced by the LCA object
        # emissionFactor = dto.dialogData['CO2 Emission Factor']
        # freshwaterFactor = dto.dialogData['Freshwater Factor']

        if upperLimit == '':
            upperLimit = default_lowerLimit
        else:
            upperLimit = float(upperLimit)

        if lowerLimit == '':
            lowerLimit = default_upperLimit
        else:
            lowerLimit = float(lowerLimit)

        if cost == '':
            costs = default_costs
        else:
            costs = float(cost)

        InputObject.set_sourceData(Costs=costs,
                                   UpperLimit=upperLimit,
                                   LowerLimit=lowerLimit,
                                   EmissionFactor=default_emissionFactor,
                                   FreshwaterFactor=default_freshwaterFactor,
                                   Composition_dictionary=dicComposition)

        return InputObject

    def _setOutputData(self, dto):
        """
        Continue filling in the superstructure with data from output units
        :return: Superstructure Object
        """
        # main or by product
        if 'productType' in list(dto.dialogData.keys()):
            productType = dto.dialogData['productType']
        else:
            productType = "MainProduct"  # default value

        # initiate the output object
        OutputObject = ProductPool(Name=dto.name,
                                   UnitNumber=dto.uid,
                                   ProductType=productType)
        # price
        price = float(dto.dialogData['priceOutput'])
        OutputObject.set_productPrice(price)

        if 'processingGroup' in list(dto.dialogData.keys()):
            processingGroup = dto.dialogData['processingGroup']
            if processingGroup != '':
                OutputObject.set_group(float(processingGroup))
            else:
                OutputObject.set_group(None)

        # emission credits and freshwater credits are not used anymore, replaced by the LCA object
        # defaulting to 0

        default_EmissionCredits = 0
        default_FreshWaterCredits = 0
        default_minProduction = 0
        default_maxProduction = 100000

        minProduction = dto.dialogData['minProduction']
        maxProduction = dto.dialogData['maxProduction']

        if minProduction == '':  # that is nothing, choose default value
            minProduction = default_minProduction
        else:
            minProduction = float(minProduction)
        if maxProduction == '':
            maxProduction = default_maxProduction
        else:
            maxProduction = float(maxProduction)

        OutputObject.set_productionLimits(minProduction, maxProduction)
        OutputObject.set_emissionCredits(default_EmissionCredits)
        OutputObject.set_freshwaterCredits(default_FreshWaterCredits)

        return OutputObject

    def _setDistributionData(self, dto):
        """
        Continue filling in the superstructure with data from distributor units
        :return: Superstructure Object
        """
        name = dto.name
        unitNumber = dto.uid
        # todo add a dialog to the distributor to set the decimal place
        decimalPlace = 2  # default value for decimal place

        distributorObject = Distributor(Name=name,
                                        UnitNumber=unitNumber,
                                        Decimal_place=decimalPlace)
        distributionList = dto.distributionContainer
        distributorObject.set_targets(distributionList)

        return distributorObject

    def _setProcessData(self, dto):

        name = dto.name
        unitNumber = dto.uid

        if dto.type == ProcessType.STOICHIOMETRIC:
            ProcessObject = StoichReactor(Name=name, UnitNumber=unitNumber)
            self._energyData(dto, ProcessObject)
            self._reactionData(dto, ProcessObject)

        elif dto.type == ProcessType.YIELD:
            ProcessObject = YieldReactor(Name=name, UnitNumber=unitNumber)
            self._energyData(dto, ProcessObject)
            self._reactionData(dto, ProcessObject)

        elif dto.type == ProcessType.GEN_HEAT:
            heatEff = dto.dialogData['heatEfficiency']
            ProcessObject = HeatGenerator(Name=name, UnitNumber=unitNumber, Efficiency=heatEff)
            self._reactionData(dto, ProcessObject)

        elif dto.type == ProcessType.GEN_ELEC:
            elecEff = dto.dialogData['electricalEfficiency']
            ProcessObject = ElectricityGenerator(Name=name, UnitNumber=unitNumber, Efficiency=elecEff)
            self._reactionData(dto, ProcessObject)

        elif dto.type == ProcessType.GEN_CHP:
            elecEff = dto.dialogData['electricalEfficiency']
            heatEff = dto.dialogData['heatEfficiency']
            efficiency = (elecEff, heatEff)
            ProcessObject = CombinedHeatAndPower(Name=name, UnitNumber=unitNumber, Efficiency=efficiency)
            self._reactionData(dto, ProcessObject)

        # everything else is a PhysicalProcess (which can only split or distribute streams)
        else:
            ProcessObject = PhysicalProcess(Name=name, UnitNumber=unitNumber)
            self._energyData(dto, ProcessObject)

        wrapp_GeneralData(obj, dfi.iloc[GeneralDataRange])
        wrapp_EconomicData(obj, dfi.iloc[EconomicDataRange], dfi.iloc[GeneralDataRange])
        wrapp_AdditivesData(obj, dfi.iloc[PossibleSourcesRange], dfi.iloc[ConcDataRange], dfi.iloc[BalanceDataRange])

        return ProcessObject

    def _energyData(self, dto, processObject):
        """
        This method reads the energy data from the dto and writes it to the process object
        :param dto:
        :param processObject:
        :return:
        """

        # # General data
        # 'Type': 'Physical Process',
        # 'Name': self.nameInput.text(),
        # 'Processing Group': self._getWidgetData(self.processingGroupInput, "int"),
        # 'Life Time Unit Process': self._getWidgetData(self.lifeTimeUnitProcess, "float"),
        # 'Working Time Unit Process': self._getWidgetData(self.fullLoadingHours, "float"),
        # 'CO2 Building': self._getWidgetData(self.co2EmissionsBuilding, "float"),
        # 'TemperatureIn1': self._getWidgetData(self.temperatureEnteringProcess, "float", returnAlternative=None),
        # 'TemperatureOut1': self._getWidgetData(self.temperatureLeavingProcess, "float", returnAlternative=None),
        # 'TemperatureIn2': self._getWidgetData(self.temperatureEnteringUnitProcess2, "float", returnAlternative=None),
        # 'TemperatureOut2': self._getWidgetData(self.temperatureLeavingUnitProcess2, "float", returnAlternative=None),
        # 'O&M': self._getWidgetData(self.operatingAndMaintenanceCost, "float"),
        # 'Direct Cost Factor': self._getWidgetData(self.directCostFactor, "float"),
        # 'Indirect Cost Factor': self._getWidgetData(self.indirectCostFactor, "float"),

        # Utility Consumption data
        # 'Reference Flow Type Energy':
        # 'Energy Consumption':
        # 'Components Energy Consumption':
        # 'Reference Flow Type Chilling':
        # 'Chilling Consumption':
        # 'Components Chilling Consumption':

        # Heat Consumption data
        # 'Reference Flow Type Heat1': self._getWidgetData(self.referenceFlowTypeHeat1, "str"),
        # 'Heat Consumption 1': self._getWidgetData(self.heatConsumption, "float"),
        # 'Components Heat Consumption 1': self._collectTableData(self.componentsTableHeat1),
        # 'Reference Flow Type Heat2': self._getWidgetData(self.referenceFlowTypeHeat2, "str"),
        # 'Heat Consumption 2': self._getWidgetData(self.heatConsumption2, "float"),
        # 'Components Heat Consumption 2': self._collectTableData(self.componentsTableHeat2),
        #
        # # Concentration data
        # 'Concentration Factor': self._getWidgetData(self.concentrationFactor, "float"),
        # 'Reference Flow 1': self._getWidgetData(self.referenceFlow1Concentration, "str"),
        # 'Components Flow1': self._collectTableData(self.componentsTableConcentration1),
        # 'Reference Flow 2': self._getWidgetData(self.referenceFlow2Concentration, "str"),
        # 'Components Flow2': self._collectTableData(self.componentsTableConcentration2),
        #
        # # Separation Efficiency data
        # 'Separation Fractions': self._collectTableData(self.separationEfficiencyTable,
        #                                                tableType="separationEfficiency"),
        # 'Waste Management': self._getWidgetData(self.wasteManagement, "str"),
        # "Check box stream 1": self.stream1CheckBox.isChecked(),
        # "Check box stream 2": self.stream2CheckBox.isChecked(),
        # "Check box stream 3": self.stream3CheckBox.isChecked(),


        ProcessElectricityDemand = dto.dialogData['Energy Consumption']
        if not pd.isnull(ProcessElectricityDemand):
            ProcessElectricityReferenceFlow = dto.dialogData['Reference Flow Type Energy']
            ProcessElectricityReferenceComponentList = dto.dialogData['Components Energy Consumption']
        else:
            ProcessElectricityDemand = 0
            ProcessElectricityReferenceFlow = None
            ProcessElectricityReferenceComponentList = []

        ProcessHeatDemand = dto.dialogData['Heat Consumption 1']
        if not pd.isnull(ProcessHeatDemand):
            ProcessHeatReferenceFlow = dto.dialogData['Reference Flow Type Heat1']
            ProcessHeatReferenceComponentList = dto.dialogData['Components Heat Consumption 1']
        else:
            ProcessHeatDemand = None
            ProcessHeatReferenceFlow = None
            ProcessHeatReferenceComponentList = []

        ProcessHeat2Demand = dto.dialogData['Heat Consumption 2']
        if not pd.isnull(ProcessHeat2Demand):
            ProcessHeat2ReferenceFlow = dto.dialogData['Reference Flow Type Heat2']
            ProcessHeat2ReferenceComponentList = dto.dialogData['Components Heat Consumption 2']
        else:
            ProcessHeat2Demand = None
            ProcessHeat2ReferenceFlow = None
            ProcessHeat2ReferenceComponentList = []

        ChillingDemand = dto.dialogData['Chilling Consumption']
        if not pd.isnull(ChillingDemand):
            ChillingReferenceFlow = dto.dialogData['Reference Flow Type Chilling']
            ChillingReferenceComponentList = dto.dialogData['Components Chilling Consumption']
        else:
            ChillingDemand = 0
            ChillingReferenceFlow = None
            ChillingReferenceComponentList = []

        # set the temperatures
        temperatureIn1 = dto.dialogData['TemperatureIn1']
        temperatureOut1 = dto.dialogData['TemperatureOut1']
        temperatureIn2 = dto.dialogData['TemperatureIn2']
        temperatureOut2 = dto.dialogData['TemperatureOut2']

        processObject.set_Temperatures(T_IN_1=temperatureIn1, T_OUT_1=temperatureOut1, tau1=ProcessHeatDemand ,
                                       T_IN_2=temperatureIn2, T_OUT_2=temperatureOut2, tau2=ProcessHeat2Demand)

        processObject.set_energyData(None,
                                     None,
                                     ProcessElectricityDemand,
                                     ProcessHeatDemand,
                                     ProcessHeat2Demand,
                                     ProcessElectricityReferenceFlow,
                                     ProcessElectricityReferenceComponentList,
                                     ProcessHeatReferenceFlow,
                                     ProcessHeatReferenceComponentList,
                                     ProcessHeat2ReferenceFlow,
                                     ProcessHeat2ReferenceComponentList,
                                     ChillingDemand,
                                     ChillingReferenceFlow,
                                     ChillingReferenceComponentList
                                     )

    def _reactionData(self, dto, processObject):
        """
        This method reads the reaction data from the dto and writes it to the process object
        type can be either stoichiometric or yield reactor
        :param dto:
        :param processObject:
        :return:
        """

        if dto.type == ProcessType.YIELD:
            product = dto.dialogData['Product']
            yieldFactor = dto.dialogData['Yield Factor']
            yieldDict = {product: yieldFactor}
            processObject.set_xiFactors(yieldDict)
            inertList = dto.dialogData['Inert Components']
            obj.set_inertComponents(inertList)

        elif dto.type == ProcessType.STOICHIOMETRIC:
            reactions = dto.dialogData['Reactions']
            conversionRateDict = {}
            reactionStoichiometryDict = {}

            for rxn in reactions:
                # rxn is a tuple (reactionName, conversion, main reactant)
                rxnName = rxn[0]
                rxnDTO = self.reactionDict[rxnName]
                rxnNumber = self.reactionNumberDict[rxnName]
                for reactants, stoi in rxnDTO.reactants.items():
                    reactionStoichiometryDict.update({(reactants, rxnNumber): float(stoi)})
                for products, stoi in rxnDTO.products.items():
                    reactionStoichiometryDict.update({(products, rxnNumber): float(stoi)})

                conversionRateDict.update({(rxn[-1], rxnNumber): float(rxn[1])})

            processObject.set_gammaFactors(reactionStoichiometryDict)
            processObject.set_thetaFactors(dict2)


def checkFocus():
    """
     for debugging purposes, check which widget currently has the focus.
    """
    currentFocusWidget = QApplication.instance().focusWidget()
    if currentFocusWidget:
        print(f"Current focus widget: {currentFocusWidget.objectName()}")
    else:
        print("No widget currently has the focus.")
        currentFocusWidget = []
    return currentFocusWidget


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
