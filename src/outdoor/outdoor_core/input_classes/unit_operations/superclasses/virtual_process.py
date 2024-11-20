from .process import Process



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#--------------------------VIRTUAL PROCESSES-----------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class VirtualProcess(Process):
    """
    Class description
    -----------------

    This class builds the basis for all virtual processes / unit-operations,
    which are more or less helpers and would not been build or constructed in
    the real application. This includes e.g. the Distributor units which are
    modelling multi-output vales, or the raw materials and product pools which
    are especially designed for collected mass flows but are not really depicted
    as tanks or other real units.

    """


    def __init__(self, Name, UnitNumber, Parent=None, *args, **kwargs):

        super().__init__(Name, UnitNumber, Parent)

