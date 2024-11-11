import logging
from enum import Enum

from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO
from src.outdoor.user_interface.data.ComponentDTO import ComponentDTO
from src.outdoor.user_interface.utils.OutdoorLogger import outdoorLogger


class DistributorType(Enum):
    BOOLDISTRIBUTOR = 0
    DISTRIBUTOR = 1


class DistributorDTO(OutdoorDTO):
    def __init__(self, uid="", type: DistributorType = DistributorType.DISTRIBUTOR):

        # add the logger
        super().__init__()
        self.logger = outdoorLogger(name="outdoor_logger", level=logging.DEBUG)

        # identification variables
        self.uid = uid
        self.type = type

        # port variables
        self.entryPorts = []
        self.exitPorts = []

        self.materialFlow = {}


        self.incomingStreams: list[str] = [] # list of uid's of processes where the stream enter the current process
        self.incomingChemicals: list[str] = [] # list of chemicals that enter the process

        self.outgoingStreams: list[str] = [] # list of uid's of processes receiving the stream exit the current process
        self.outgoingChemicals: list[str] = []

        self.output_components: list[tuple[ComponentDTO, int, str]] = []


    def addDialogData(self, dialogData):
        self.dialogData.update(dialogData)



    def addMaterialFlow(self, reciveingID:str, streamType:int, splitFactorDict:dict):
        """
        Define where the material flow is going to
        :param reciveingID: the id of the process that the material flow is going to
        :param streamType: the stream number that is being sent from the port either 1, 2, or 3
        :param splitFactorDict: dictionary with the separation fractions for each chemical of the specified the stream
        :return:
        """
        self.materialFlow[reciveingID] = {streamType: splitFactorDict}

    def removeFromMaterialFlow(self, reciveingID:str):
        """
        Remove the material flow to a specific process
        :param reciveingID:
        :return:
        """
        self.materialFlow.pop(reciveingID)

    def updateDistributorDTO(self, field, value):

        if field == 'Connection':
            # in this case the value is the id of the process that the material flow is going to
            self._updateConnection(sendingPort=value[0], reciveingPort=value[1])

        elif field == 'materialFlow':
            self._updateMaterialFlow()

        else:
            self.logger.error(f"Field {field} does not exist in ProcessDTO")


    def _updateConnection(self, sendingPort, reciveingPort):
        """
        Update the material flow of the process based on the current dialog data and how the ports are connected
        :return: updated material flow dictionary
        """
        # retrieve the unit process DTO from the centralDataManager that is sending the connection
        # loop over the exit ports

        streamNumber = sendingPort.exitStream # get the stream number of the port either 1, 2, or 3
        splitDict = self._getSeperationDict(streamNumber)
        self.addMaterialFlow(reciveingPort.iconID, streamNumber, splitDict)


    def _getSeperationDict(self, streamType):
        """
        Get the separation dictionary for the stream that is being sent from the startPort
        :param streamType: the stream number that is being sent from the port either 1, 2, or 3
        :return: splitDict: dictionary with the separation fractions for each chemical of the specified the stream
        """
        # if the process is an input process, all the chemicals are sent to the stream
        if self.type.value == 0: # input
            return {'all': 1}


        if self.dialogData == {}: # if the dialog data is empty, return an empty dictionary with the default values
            return {} # to be updated with the dialog data!

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
            self.logger.error("Stream type not recognized when connecting to the port")

        # get the specific separation dictionary for the stream
        splitDict = {splitDict['Component']: splitDict[streamKey] for splitDict in separationList}

        return splitDict


    def _updateMaterialFlow(self):
        """
        Update the material flow of the process based on the current dialog data and how the ports are connected
        :return: updated material flow dictionary
        """
        # loop over the existing connections
        for id, separationDict in self.materialFlow.items():
            for streamType, splitDict in separationDict.items():
                splitDict = self._getSeperationDict(streamType)
                self.addMaterialFlow(id, streamType, splitDict)

        self.logger.info(f"Material flow updated for process {self.name}")
        print(self.materialFlow)


