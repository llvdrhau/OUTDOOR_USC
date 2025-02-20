import logging
from src.outdoor.outdoor_core.input_classes.superstructure import Superstructure
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
from outdoor.user_interface.data.ProcessDTO import ProcessType
import pandas as pd


class ConstructSuperstructure:
    def __init__(self, centralDataManager):

        self.logger = logging.getLogger(__name__)

        # pass on the centralDataManager
        self.centralDataManager = centralDataManager

        self.warningMessage = ''
        # stop the code if the centralDataManager is empty
        if not self.centralDataManager.unitProcessData:
            self.warningMessage = "The centralDataManager is empty, please fill in the data before running the simulation"
            return

        # set some default values
        # make a dictionary of the reaction names and the corresponding reaction dto for easy access later on
        self.reactionDict = {dto.name: dto for dto in self.centralDataManager.reactionData}
        self.reactionNumberDict = {dto.name: i + 1 for i, dto in enumerate(self.centralDataManager.reactionData)}
        # make the dictionary maps to link the right reference flow to in input from the widgets
        self.referenceFlowDictMap = {"Entering Mass Flow": 'FIN',
                                     "Exiting Mass Flow": 'FOUT',
                                     "Entering Molar Flow": 'FIN_M',
                                     "Exiting Molar Flow": 'FOUT_M',
                                     "Entering Flow Heat Capacity": 'FIN_CP',
                                     "Exiting Flow Heat Capacity": 'FOUT_CP',
                                     "Electricity consumption": 'PEL',
                                     "Electricity production (generators)": 'PEL_PROD',
                                     "Heat production (generators)": 'PHEAT', }

        # make the initial object:
        self.superstructureObject = self._setGeneralData()
        superstructureListUnits = self._setUnitProcessData()
        # add the units to the superstructure object
        self.superstructureObject.add_UnitOperations(superstructureListUnits)

    def _setGeneralData(self):
        """
        Initiates the superstructure object and fills in general data

        :return: Superstructure Object
        """
        # model name
        modelName = self.centralDataManager.metadata['PROJECT_NAME']
        # fixme: if no changes are made to the initial general data, the default values are never saved!
        # maybe generate a waring to signal that the general tab needs to be edited before running the simulation

        # retrieve the objective
        objectiveFull = self.centralDataManager.generalData['objective']
        objectiveMap = {'EBIT: Earnings Before Income Taxes': 'EBIT',
                        "NPC: Net Production Costs": "NPC",
                        "NPE: Net Produced CO2 Emissions": "NPE",
                        "FWD: Freshwater Demand": "FWD"}

        if objectiveFull in objectiveMap:
            objective = objectiveMap[objectiveFull]
        else:  # the LCA objectives are not abbreviated, so they need not be mapped
            objective = objectiveFull

        productDriven = self.centralDataManager.generalData['productDriver']

        mainProduct = self.centralDataManager.generalData['mainProduct']
        if mainProduct == '':
            mainProduct = None
        productLoad = self.centralDataManager.generalData['productLoad']

        if productLoad == '':
            productLoad = 1
        else:
            productLoad = float(productLoad)

        optimizationMode = self.centralDataManager.generalData['optimizationMode']

        obj = Superstructure(ModelName=modelName,
                             Objective=objective,
                             loadType=productDriven,
                             loadName=mainProduct,
                             load=productLoad,
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
            else:
                T_IN = float(T_IN)
                T_OUT = float(T_OUT)

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

        # reactionNumberList = [i + 1 for i in range(len(self.centralDataManager.reactionData))]
        reactionNumberIds = [dto.uid for dto in self.centralDataManager.reactionData]
        obj.add_reactions(reactionNumberIds)

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
        # TODO later on, make this a toggle for either self-entered data or the LCA data
        emissionsUtilityDict = {}
        emissionsWaterUtilityDict = {}
        utilityPrices = {}
        for dto in self.centralDataManager.utilityData:
            emissionsUtilityDict[dto.name] = dto.co2
            emissionsWaterUtilityDict[dto.name] = dto.fwd
            if dto.name in ["Electricity", "Chilling"]:
                utilityPrices[dto.name] = dto.cost

        obj.set_utilityEmissionsFactor(emissionsUtilityDict)
        obj.set_utilityFreshWaterFator(emissionsWaterUtilityDict)

        # replaced by the lca data not important any more, just make a list of zeros to not break the code
        co2ComponentList = {dto.name: 0 for dto in self.centralDataManager.componentData}
        obj.set_componentEmissionsFactor(co2ComponentList)
        # TODO Condense these into a single list when you have time.
        setterList = {}
        for dto in self.centralDataManager.temperatureData:
            if dto.shortname == "cool":
                obj.set_deltaCool(dto.cost)
                setterList[dto.shortname] = (dto.temp, dto.cost)
            else:
                obj.temperaturePricesDict[dto.shortname] = dto.cost
                setterList[dto.shortname] = (dto.temp, dto.cost)
        obj.set_heatUtilitiesFromList(setterList)
        obj.set_deltaUt(utilityPrices)

        # set new additions
        #         # Parameters INDEXED
        #         self.UtilityImpactFactors = {'util_impact_factors': {}}

        # set the impact categories
        # impactCategories = ['GWP', 'RM'] # dto.dialogData['Impact Categories']
        # you could also get the impact categories from the LCA data from the waste or Temperature dto's
        # the impact categories should be the same for all the dto's
        # todo this is mega convoluted,add attributes to the dto's to get the impact categories, wait until Mias has
        #  implemented methodes to select impact categories
        impactCategoriesDict = self.centralDataManager.utilityData[0].getLCAImpacts()
        impactCategories = list(list(impactCategoriesDict.values())[0].keys())
        obj._set_impact_categories(impactCategories)

        # set the waste management types
        wasteManagementTypes = self.centralDataManager.wasteManagementTypes
        obj._set_waste_management_types(wasteManagementTypes)

        # set waste types per Unit Process
        # links the waste types to the unit processes needs to be done after the unit processes are added
        obj._set_waste_type_u(self.centralDataManager.unitProcessData)

        # set the waste cost factor
        wasteCostFactorDict = {dto.name: float(dto.cost) for dto in self.centralDataManager.wasteData}
        obj._set_waste_cost(wasteCostFactorDict)

        # set the waste impact factors
        obj._set_waste_management_impact_factors(self.centralDataManager.wasteData)

        # set the impact inflow components
        obj._set_component_impact_factors(self.centralDataManager.componentData)

        # for debugging purposes
        # a = obj.ImpactInflowComponents['impact_inFlow_components']
        # print(a)

        # set the impact of utility factors
        obj._set_utility_impact_factors(self.centralDataManager.utilityData)

        return obj

    def _setUnitProcessData(self):
        """
        Continue filling in the superstructure with data from unit operations
        :return: Superstructure Object
        """
        processUnit_ObjectList = []  # in outdoor this is PU_ObjectList in main.py in the excel wrapper
        unitDTODictionary = self.centralDataManager.unitProcessData
        counter = 0 # to give unique names to the distributors
        for uuid, dto in unitDTODictionary.items():
            if dto.type == ProcessType.INPUT:
                InputObject = self._setInputData(dto)
                processUnit_ObjectList.append(InputObject)
            elif dto.type == ProcessType.OUTPUT:
                OutputObject = self._setOutputData(dto)
                processUnit_ObjectList.append(OutputObject)
            elif dto.type == ProcessType.DISTRIBUTOR:
                DistributorObject = self._setDistributionData(dto, counter)
                processUnit_ObjectList.append(DistributorObject)
                counter += 1 # to give unique names to the distributors
            elif dto.type.value in list(range(1, 7)):  # not an input, output or distributor
                ProcessObject = self._setProcessData(dto)
                processUnit_ObjectList.append(ProcessObject)
        return processUnit_ObjectList

    def _setInputData(self, dto):
        """
        Continue filling in the superstructure with data from input units
        :return: Superstructure Object
        """

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
            upperLimit = default_upperLimit
        else:
            upperLimit = float(upperLimit)

        if lowerLimit == '':
            lowerLimit = default_lowerLimit
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
            # get rid of the spaces so it is correctly formatted for the superstructure object
            productType = productType.replace(" ", "")
        else:
            productType = "MainProduct"  # default value

        # initiate the output object
        OutputObject = ProductPool(Name=dto.name,
                                   UnitNumber=dto.uid,
                                   ProductType=productType)
        # price
        if dto.dialogData['priceOutput'] == '':
            price = 0
        else:
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

    def _setDistributionData(self, dto, counter):
        """
        Continue filling in the superstructure with data from distributor units
        :return: Superstructure Object
        """
        name = dto.name
        name = 'Distr.{}'.format(counter) if name == '' else name
        unitNumber = dto.uid
        # todo add a dialog to the distributor to set the decimal place
        decimalPlace = 3  # default value for decimal place

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

        self._generalUnitData(dto, ProcessObject)
        self._economicUnitData(dto, ProcessObject)
        self._additivesUnitData(dto, ProcessObject)

        return ProcessObject

    def _energyData(self, dto, processObject):
        """
        This method reads the energy data from the dto and writes it to the process object
        :param dto:
        :param processObject:
        :return:
        """
        ProcessElectricityDemand = dto.dialogData['Energy Consumption']
        if ProcessElectricityDemand: # make sure it's always a number or None
            ProcessElectricityReferenceFlow = dto.dialogData['Reference Flow Type Energy']
            ProcessElectricityReferenceFlow = self.referenceFlowDictMap[ProcessElectricityReferenceFlow]
            ProcessElectricityReferenceComponentList = dto.dialogData['Components Energy Consumption']
        else:
            ProcessElectricityDemand = 0
            ProcessElectricityReferenceFlow = None
            ProcessElectricityReferenceComponentList = []

        ProcessHeatDemand = dto.dialogData['Heat Consumption 1']
        if ProcessHeatDemand:
            ProcessHeatReferenceFlow = dto.dialogData['Reference Flow Type Heat1']
            ProcessHeatReferenceFlow = self.referenceFlowDictMap[ProcessHeatReferenceFlow]
            ProcessHeatReferenceComponentList = dto.dialogData['Components Heat Consumption 1']
        else:
            ProcessHeatDemand = None
            ProcessHeatReferenceFlow = None
            ProcessHeatReferenceComponentList = []

        ProcessHeat2Demand = dto.dialogData['Heat Consumption 2']
        if ProcessHeat2Demand:
            ProcessHeat2ReferenceFlow = dto.dialogData['Reference Flow Type Heat2']
            ProcessHeat2ReferenceFlow = self.referenceFlowDictMap[ProcessHeat2ReferenceFlow]
            ProcessHeat2ReferenceComponentList = dto.dialogData['Components Heat Consumption 2']
        else:
            ProcessHeat2Demand = None
            ProcessHeat2ReferenceFlow = None
            ProcessHeat2ReferenceComponentList = []

        ChillingDemand = dto.dialogData['Chilling Consumption']
        if ChillingDemand:
            ChillingReferenceFlow = dto.dialogData['Reference Flow Type Chilling']
            ChillingReferenceFlow = self.referenceFlowDictMap[ChillingReferenceFlow]
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

        processObject.set_Temperatures(T_IN_1=temperatureIn1, T_OUT_1=temperatureOut1, tau1=ProcessHeatDemand,
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
            processObject.set_inertComponents(inertList)

        elif dto.type in [ProcessType.STOICHIOMETRIC, ProcessType.GEN_CHP, ProcessType.GEN_ELEC, ProcessType.GEN_HEAT]:
            reactions = dto.dialogData['Reactions']
            conversionRateDict = {}
            reactionStoichiometryDict = {}

            for rxn in reactions:
                # rxn is a tuple (reactionName, conversion, main reactant)
                rxnName = rxn[0]
                rxnDTO = self.reactionDict[rxnName]
                rxnNumber = rxnDTO.uid #self.reactionNumberDict[rxnName] use the uid instead of the number
                for reactants, stoi in rxnDTO.reactants.items():
                    reactionStoichiometryDict.update({(reactants, rxnNumber): float(stoi)})
                for products, stoi in rxnDTO.products.items():
                    reactionStoichiometryDict.update({(products, rxnNumber): float(stoi)})

                conversionRateDict.update({(rxnNumber, rxn[-1]): float(rxn[1])/100}) # dived by 100 to get the fraction

            processObject.set_gammaFactors(reactionStoichiometryDict)
            processObject.set_thetaFactors(conversionRateDict)

    def _generalUnitData(self, dto, processObject):
        """
        This method reads the general unit data from the dto and writes it to the process object
        :param dto:
        :param processObject:
        :return:
        """

        Name = dto.name

        LifeTime = dto.dialogData['Life Time Unit Process']

        ProcessGroup = dto.dialogData['Processing Group']
        if ProcessGroup:
            ProcessGroup = int(ProcessGroup)
        else:
            ProcessGroup = None

        CO2Emissions = dto.dialogData['CO2 Building']
        if CO2Emissions:
            emissions = CO2Emissions
        else:
            emissions = 0

        maintenance_factor = dto.dialogData['O&M']
        if maintenance_factor:
            maintenance_factor = None

        cost_percentage = dto.dialogData['Reoccurring Cost Factor']
        time_span = dto.dialogData['Turn Over Time']
        time_mode = dto.dialogData['Turn Over Unit']

        if not cost_percentage:
            # if the cost percentage is not set, set variables to None and the time mode to 'No Mode'
            cost_percentage = None
            time_span = None
            time_mode = 'No Mode'
        else:
            if time_mode == 'years':
                time_mode = 'Yearly'
            else:
                time_mode = 'Hourly'

        full_load_hours = dto.dialogData['Working Time Unit Process']
        if full_load_hours:
            full_load_hours = None

        wasteDisposalType = dto.dialogData['Waste Management']

        processObject.set_generalData(ProcessGroup,
                                      LifeTime,
                                      emissions,
                                      full_load_hours,
                                      maintenance_factor,
                                      cost_percentage,
                                      time_span,
                                      time_mode,
                                      wasteDisposalType)

    def _economicUnitData(self, dto, processObject):
        """
        This method reads the economic data from the dto and writes it to the process object
        :param dto:
        :param processObject:
        :return:
        """

        ReferenceCosts = dto.dialogData["Reference Cost Unit"]
        ReferenceFlow = dto.dialogData["Reference Flow Equipment Cost"]
        CostExponent = dto.dialogData["Exponent"]
        ReferenceYear = dto.dialogData["Reference Year"]

        DirectCostFactor = dto.dialogData["Direct Cost Factor"]

        IndirectCostFactor = dto.dialogData["Indirect Cost Factor"]

        ReferenceFlowType_dialog = dto.dialogData["Reference Flow Type"]
        ReferenceFlowType = self.referenceFlowDictMap[ReferenceFlowType_dialog] # get the correct abbreviation

        ReferenceFlowComponentList = dto.dialogData["Components Equipment Costs"]

        # this will make the cost practically 0 if the reference flow is 0
        if ReferenceCosts == 0:
            ReferenceCosts = 0.000001
            ReferenceFlow = 1000000

        # Set Economic Data in Process Unit Object

        processObject.set_economicData(DirectCostFactor,
                             IndirectCostFactor,
                             ReferenceCosts,
                             ReferenceFlow,
                             CostExponent,
                             ReferenceYear,
                             ReferenceFlowType,
                             ReferenceFlowComponentList
                             )

    def _additivesUnitData(self, dto, processObject):
        """
        This method reads the additives data from the dto and writes it to the process object
        :param dto:
        :param processObject:
        :return:
        """

        # # Concentration data
        # 'Concentration Factor': self._getWidgetData(self.concentrationFactor, "float"),
        # 'Reference Flow 1': self._getWidgetData(self.referenceFlow1Concentration, "str"),
        # 'Components Flow1': self._collectTableData(self.componentsTableConcentration1),
        # 'Reference Flow 2': self._getWidgetData(self.referenceFlow2Concentration, "str"),
        # 'Components Flow2': self._collectTableData(self.componentsTableConcentration2),

        lhs_comp_list = dto.dialogData["Components Flow1"]
        rhs_comp_list = dto.dialogData["Components Flow2"]
        lhs_ref_flow = self.referenceFlowDictMap[dto.dialogData["Reference Flow 1"]]
        rhs_ref_flow = self.referenceFlowDictMap[dto.dialogData["Reference Flow 2"]]

        req_concentration = dto.dialogData["Concentration Factor"]
        if not req_concentration:
            req_concentration = 0 # set to 0 if not provided

        # the myu dictionary is where the split fractions are stored and defined
        # {(unitNr_that_receives, component), Fraction}
        materialFlow = dto.materialFlow
        myu_dict = {}
        streamTypeDict = dto.classificationStreams
        for stream, dict in materialFlow.items():
            # check if it's a boolean stream
            streamType = streamTypeDict[stream]
            if streamType is None or streamType == ProcessType.BOOLDISTRIBUTOR:
                for unitID, dictComponents in dict.items():
                    for component, fraction in dictComponents.items():
                        myu_dict[(unitID, component)] = fraction
            else:  # get the id of the distributor
                distributorID = dto.classificationId[stream]
                for _, dictComponents in dict.items():
                    for component, fraction in dictComponents.items():
                        myu_dict[(distributorID, component)] = fraction

        processObject.set_flowData(req_concentration,
                                   rhs_ref_flow,
                                   lhs_ref_flow,
                                   rhs_comp_list,
                                   lhs_comp_list,
                                   myu_dict,
                                   )

        sourceslist = dto.inputFlows
        processObject.set_possibleSources(sourceslist)

        # Connections is a dictionary with the keys the streams and the values the unit
        # uids to which they are connected if the stream is a boolean stream add a list
        # E.g.: , {1:[222, 333], 2:[], 3:[]}
        connections = {}
        for stream, type in streamTypeDict.items():
            if type == ProcessType.BOOLDISTRIBUTOR:
                sendList = []
                for unitID in materialFlow[stream]:
                    sendList.append(unitID)
                connections[stream] = sendList
            elif type == ProcessType.DISTRIBUTOR:
                connections[stream] = [dto.classificationId[stream]]
            else: # just a normal process
                sendList = []
                for unitID in materialFlow[stream]:
                    sendList.append(unitID)
                connections[stream] = sendList

        processObject.set_connections(connections)

    def _addUncertaintyData(self):
        """
        This method reads the uncertainty data from the dto and writes it to the superstucture object
        the uncertainty data is a dataFrame,
        :return:
        """
        # todo implement this method
        pass

    def get_superstructure(self):
        return self.superstructureObject
