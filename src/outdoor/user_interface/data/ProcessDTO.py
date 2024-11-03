from enum import Enum
from src.outdoor.user_interface.data.ComponentDTO import ComponentDTO
from src.outdoor.user_interface.data.ReactionDTO import ReactionDTO
from src.outdoor.user_interface.utils.OutdoorLogger import outdoorLogger
import logging
from typing import Union


class ProcessType(Enum):
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
    OUTGOINGCHEMICALS = 'OutgoingChemicals'
    CONNECTION = 'Connection'
    MATERIALFLOW = 'MaterialFlow'
    DISTRIBUTION_OWNER = 'BooleanOwner'
    DISTRIBUTION_CONNECTION = 'BooleanConnection'
    DISTRIBUTION_CONTAINER = 'BooleanContainer'

class ProcessDTO(object):
    def __init__(self, uid="", name="", type:ProcessType=ProcessType.PHYSICAL, outGoingChemicals:list=[]):

        # add the logger
        self.logger = outdoorLogger(name="outdoor_logger", level=logging.DEBUG)

        # identification variables
        self.uid = uid
        self.name = name
        self.type = type

        # port variables
        self.entryPorts = []
        self.exitPorts = []

        self.materialFlow = {1: {},
                             2: {},
                             3: {}} # dictionary with the material flow to other processes

        self.outgoingChemicals = outGoingChemicals

        self.incomingStreams: list[str] = [] # list of uid's of processes where the stream enter the current process
        self.incomingChemicals: list[str] = [] # list of chemicals that enter the process

        self.outgoingStreams: list[str] = [] # list of uid's of processes where the stream exit the current process
        self.outgoingChemicals: list[str] = []

        self.output_components: list[tuple[ComponentDTO, int, str]] = []
        self.reactions: list[ReactionDTO] = []
        self.dialogData: dict = {}

        # variable related to distribution units
        # todo it might be more logical for distribution units to be a separate class
        # self.booleanOwner = None  # the id of the process to which the boolean distributor belongs to
        # self.booleanContainer = []  # list of processes connected to the exit port of the boolean distributor

        self.distributionOwner = None  # the id of the process to which the distributor belongs to
        self.distributionContainer = []  # list of processes connected to the exit port of the distributor

        # stream classification
        # can either be 'Normal', 'Boolean', or 'Distributed' for each stream depending on the distribution unit
        self.classificationStreams = {1: None, 2: None, 3: None}


    def addDialogData(self, dialogData):
        self.dialogData.update(dialogData)

    def addEnteringConnection(self, enteringProcessID):
        #portType, startIconID, endIconID, starPosition, endPosition):
        # Add a connection between two icons
        self.incomingStreams.append(enteringProcessID)
        # todo figure out how to add the chemicals that are coming in the process and add them to the dialogs which are
        # relavant to incomming chemicals

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

    def updateProcessDTO(self, field: UpdateField, value: Union[str, list, tuple, None, tuple]):

        if field == UpdateField.NAME:
            self.name = value

        elif field == UpdateField.OUTGOINGCHEMICALS:
            self.outgoingChemicals = value

        elif field == UpdateField.CONNECTION:
            # value is a tuple with the sending port and the receiving port
            self._updateConnection(sendingPort=value[0], reciveingPort=value[1])

        elif field == UpdateField.MATERIALFLOW:
            self._updateMaterialFlow()

        elif field == UpdateField.DISTRIBUTION_OWNER:
            # the value is a tuple containing the ID to which the boolean distributor belongs to and the stream number
            # it is distributing
            self.distributionOwner = value
            streamNumber = value[1]
            distributorType = value[2]  # the type of distributor either 'Boolean' or 'Distributor'
            self.classificationStreams[streamNumber] = distributorType

        elif field == UpdateField.DISTRIBUTION_CONNECTION:
            unitID2Add = value[0]
            streamNumber = value[1]
            self.updateDistributionConnection(unitID2Add, streamNumber)

        elif field == UpdateField.DISTRIBUTION_CONTAINER:
            # the value is a tuple with the id of the process and the stream number
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

        self.logger.info(f"Material flow updated for process {self.name}")
        #print(self.materialFlow)


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
