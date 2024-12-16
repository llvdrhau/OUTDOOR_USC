import logging

class TabManager:
    """
    This class is responsible for managing and storing the main tabs in the application. Used to manipulate visual
    elements in the application, when for example, chemical names or reaction names change. That is the changes need
    to propagate through all tabs visully.
    """
    def __init__(self):

        # define the logger
        self.logger = logging.getLogger(__name__)
        # define all the possible tabs in the main window of the application
        self.welcomeTab = None
        self.projectDescriptionTab = None
        self.generalSystemDataTab = None
        self.compoundsTab = None
        self.reactionsTab = None
        self.utilityTab = None
        self.superstructureMappingTab = None
        self.uncertaintyTab = None

    def addTab(self, tab, tabType):
        """
        Adds a tab to the TabManager
        """
        match tabType:
            case "UtilityTab":
                self.utilityTab = tab
            case "ComponentsTab":
                self.compoundsTab = tab
            case "ReactionsTab":
                self.reactionsTab = tab
            case "GeneralSystemDataTab":
                self.generalSystemDataTab = tab
            case "ProjectDescriptionTab":
                self.projectDescriptionTab = tab
            case "WelcomeTab":
                self.welcomeTab = tab
            case "SuperstructureMappingTab":
                self.superstructureMappingTab = tab
            case "UncertaintyTab":
                self.uncertaintyTab = tab
            case _:
                self.logger.error(f"Tab {tab} not found")

