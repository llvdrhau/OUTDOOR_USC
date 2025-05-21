import logging
from enum import Enum
from typing import Union

from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO
from outdoor.user_interface.data.ComponentDTO import ComponentDTO
from outdoor.user_interface.data.ReactionDTO import ReactionDTO
from outdoor.user_interface.utils.OutdoorLogger import outdoorLogger


class ProcessType(Enum):
    LCA = -3
    DISTRIBUTOR = -2
    BOOLDISTRIBUTOR = -1
    INPUT = 0
    PHYSICAL = 1
    STOICHIOMETRIC = 2
    YIELD = 3
    GEN_HEAT = 4
    GEN_ELEC = 5
    GEN_CHP = 6
    OUTPUT = 7

class UpdateField(Enum):  # to much of a hassle to use the Enum class use Literal instead for the update fields
    NAME = 'Name'
    INPUT_FLOW = 'InputFlow'
    INCOMING_UNIT_FLOWS = 'IncomingUnitFlows'
    OUTGOINGCHEMICALS = 'OutgoingChemicals'
    CONNECTION = 'Connection'
    MATERIALFLOW = 'MaterialFlow'
    DISTRIBUTION_OWNER = 'BooleanOwner'
    DISTRIBUTION_CONNECTION = 'BooleanConnection'
    DISTRIBUTION_CONTAINER = 'BooleanContainer'
    STREAM_CLASSIFICATION = 'StreamClassification'


class ProcessDTO(OutdoorDTO):
    def __init__(self, uid="", name="", type: ProcessType = ProcessType.PHYSICAL, outGoingChemicals: list = [],
                 positionOnCanvas=None):

        # add the logger
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # identification variables
        self.uid = uid
        self.name = name
        self.type = type

        # position variables
        self.positionOnCanvas = positionOnCanvas

        # port variables
        self.entryPorts = []
        self.exitPorts = []

        # curvature of leaving lines
        self.curvatureLines = {1: None,   # position control point
                              2: None,   # None if there is no curvature
                              3: None}

        # input flow variables
        self.inputFlows = []  # list of the ID of the input process type that flow into the current process
        # Dictionary of the ID's units that flow into the current process unit and the stream number
        # they are connected to
        self.incomingUnitFlows = {}

        # the material flow is a dictionary with the stream number as the key and the value is a dictionary with the
        # process id as the keys and the split dictionary as the value
        self.materialFlow = {1: {},
                             2: {},
                             3: {}}  # dictionary with the material flow to other processes

        self.outgoingChemicals = outGoingChemicals

        # self.incomingStreams: list[str] = [] # list of uid's of processes where the stream enter the current process
        # self.incomingChemicals: list[str] = [] # list of chemicals that enter the process
        # self.outgoingStreams: list[str] = [] # list of uid's of processes where the stream exit the current process
        # self.outgoingChemicals: list[str] = []

        self.output_components: list[tuple[ComponentDTO, int, str]] = []
        self.reactions: list[ReactionDTO] = []
        self.dialogData: dict = {}

        # variables related to the distribution units only applicable to distributors
        if self.type in [ProcessType.BOOLDISTRIBUTOR, ProcessType.DISTRIBUTOR]:
            # distributionOwner: a tuple with the id of the process to which the distributor belongs to and the
            # stream number it is connected to
            self.distributionOwner = None
            self.distributionContainer = []  # list of processes connected to the exit port of the distributor

        # stream classification
        # can either be 'Normal', 'Boolean', or 'Distributed' for each stream depending if it is conected
        # to a distribution unit. the value are either None or ProcessType.BOOLDISTRIBUTOR or ProcessType.DISTRIBUTOR
        self.classificationStreams = {1: None, 2: None, 3: None}
        # the classificationId is a dictionary with the stream number as the key and the value is the id of the
        # distributor that is connected to the stream
        self.classificationId = {1: None, 2: None, 3: None}


    def addDialogData(self, dialogData):
        self.dialogData.update(dialogData)

    def addEnteringConnection(self, enteringProcessID):
        #portType, startIconID, endIconID, starPosition, endPosition):
        # Add a connection between two icons
        self.incomingStreams.append(enteringProcessID)


    def addMaterialFlow(self, streamType:int, reciveingID:str, splitFactorDict:dict):
        """
        Define where the material flow is going to
        :param reciveingID: the id of the process that the material flow is going to
        :param streamType: the stream number that is being sent from the port either 1, 2, or 3
        :param splitFactorDict: dictionary with the separation fractions for each chemical of the specified the stream
        :return:
        """
        self.materialFlow[streamType].update({reciveingID: splitFactorDict})
        # print(self.materialFlow)
        # self.materialFlow[reciveingID] = {streamType: splitFactorDict}

    def removeFromMaterialFlow(self, reciveingID:str):
        """
        Remove the material flow to a specific process
        :param reciveingID:
        :return:
        """
        for streamType in self.materialFlow:
            if reciveingID in self.materialFlow[streamType]:
                self.materialFlow[streamType].pop(reciveingID)

        #self.materialFlow.pop(reciveingID)

    def updateProcessDTO(self, field: UpdateField, value: Union[str, str, dict, list, tuple, None, tuple, tuple, tuple, str]):

        if field == UpdateField.NAME:
            # value is a string with the name of the process
            self.name = value

        elif field == UpdateField.INPUT_FLOW:
            # update the incoming chemicals
            # self.incomingChemicals = value
            self.inputFlows.append(value) # the value is the ID of the input process type

        elif field == UpdateField.INCOMING_UNIT_FLOWS:
            # update the incoming unit flows
            if list(value.keys())[0] in self.incomingUnitFlows:
                errorFlag = True
                return errorFlag
            else:
                self.incomingUnitFlows.update(value)
                errorFlag = False
                return errorFlag  # if no error return False

        elif field == UpdateField.OUTGOINGCHEMICALS:
            self.outgoingChemicals = value # the value is a list of the outgoing chemicals

        elif field == UpdateField.CONNECTION:
            # value is a tuple with the sending port and the receiving port
            self._updateConnection(sendingPort=value[0], reciveingPort=value[1])

        elif field == UpdateField.MATERIALFLOW:
            self._updateMaterialFlow()
            self.logger.info(f"Material flow updated for process {self.name}")
            self.logger.debug(f"Material flow: {self.materialFlow}")
            self.logger.debug(f"stream classification: {self.classificationStreams}")

        elif field == UpdateField.DISTRIBUTION_OWNER:
            # the value is a tuple containing the ID to which the boolean distributor belongs to and the stream number
            # it is distributing
            self.distributionOwner = value

        elif field == UpdateField.STREAM_CLASSIFICATION:
            streamNumber = value[0]
            distributorType = value[1]  # the type of distributor either 'Boolean' or 'Distributor'
            distributorID = value[2]  # the id of the distributor
            self.classificationStreams[streamNumber] = distributorType
            self.classificationId[streamNumber] = distributorID

        elif field == UpdateField.DISTRIBUTION_CONNECTION:
            unitID2Add = value[0]
            streamNumber = value[1]
            self.updateDistributionConnection(unitID2Add, streamNumber)

        elif field == UpdateField.DISTRIBUTION_CONTAINER:
            # the value is the id of the process that is connected to the distributor
            self.distributionContainer.append(value)

        else:
            self.logger.error(f"Field {field} does not exist in ProcessDTO")

    def _updateConnection(self, sendingPort, reciveingPort):
        """
        Update the material flow of the process based on the current dialog data and how the ports are connected
        :return: updated material flow dictionary
        """
        # retrieve the unit process DTO from the centralDataManager that is sending the connection
        # loop over the exit ports

        streamNumber = sendingPort.exitStream  # get the stream number of the port either 1, 2, or 3
        splitDict = self._getSeparationDict(streamNumber)
        self.addMaterialFlow(streamNumber, reciveingPort.iconID, splitDict)

    def _getSeparationDict(self, streamType):
        """
        Get the separation dictionary for the stream that is being sent from the startPort
        :param streamType: the stream number that is being sent from the port either 1, 2, or 3
        :return: splitDict: dictionary with the separation fractions for each chemical of the specified the stream
        """
        # if the process is an input process, all the chemicals are sent to the stream
        if self.type.value == 0:  # input
            return {'all': 1}


        if self.dialogData == {}: # if the dialog data is empty, return an empty dictionary with the default values
            return {}  # to be updated with the dialog data!

        # retrieve the unit process DTO from the centralDataManager that is sending the connection
        separationList = self.dialogData['Separation Fractions']

        if streamType == 1:
            streamKey = 'Stream 1'
        elif streamType == 2:
            streamKey = 'Stream 2'
        elif streamType == 3:
            streamKey = 'Stream 3'
        else:
            streamKey = ''
            self.logger.error("Stream type not recognized when connecting to the port in function"
                              " _getSeparationDict()")

        # get the specific separation dictionary for the stream
        splitDict = {splitDict['Component']: splitDict[streamKey] for splitDict in separationList}

        return splitDict

    def _updateMaterialFlow(self):
        """
        Update the material flow of the process based on the current dialog data and how the ports are connected
        :return: updated material flow dictionary
        """
        # loop over the existing connections
        for streamType, separationDict in self.materialFlow.items():
            for id, splitDict in separationDict.items():
                splitDict = self._getSeparationDict(streamType)
                self.addMaterialFlow(streamType, id, splitDict)

    def updateDistributionConnection(self, unitID2Add, streamNumber):
        """
        Update the boolean connection to the process
        :param unitID2Add: the id of the process to which the boolean distributor is connected to
        :param streamNumber: the stream number that is being sent from the port either 1, 2, or 3
        :return:
        """
        # get the separation dictionary for the stream
        splitDict = self._getSeparationDict(streamNumber)
        self.addMaterialFlow(streamNumber, unitID2Add, splitDict)
        self.logger.info(f"Boolean connection updated for process {self.name}")
        #print(self.materialFlow)


    def getOutgoingChemicals(self, streamNumber):
        """
        Get the outgoing chemicals from the process unit of a specific stream

        :return: the outgoing chemicals
        """
        outgoingChemicals = []
        if streamNumber in self.materialFlow:
            streamDict = self.materialFlow[streamNumber]
            #get the keys of the dictionary (all the dictionaries in the stream are the same for each ID)
            firstKey = list(streamDict.keys())[0]
            outGoingComponentsDict = streamDict[firstKey]
            for chemical, fraction in outGoingComponentsDict.items():
                if fraction > 0:
                    outgoingChemicals.append(chemical)

        return outgoingChemicals
