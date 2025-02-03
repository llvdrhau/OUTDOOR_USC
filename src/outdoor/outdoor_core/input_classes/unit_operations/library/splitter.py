from ..superclasses.physical_process import PhysicalProcess




class Splitter(PhysicalProcess):
    """
    Class description
    -----------------

    This Class models a typical splitting unit such as a distillation column.
    It inherit from the PhysicalProcess class.
    Therefore, they includes capital costs factors, energy demand factors and
    mass balance factors.
    """



    def __init__(self, Name, UnitNumber, Parent = None, *args, **kwargs):

        super().__init__(Name, UnitNumber,Parent)

        self.Type = "Splitter"

    def fill_unitOperationsList(self, superstructure):

        super().fill_unitOperationsList(superstructure)
        superstructure.SplitterNumberList['SPLITTERS'].append(self.Number)


