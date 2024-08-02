import math

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#--------------------------GENERAL PROCESS CLASS-------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class ProcessNode():
    """
    Simple node of a process

    """



    def __init__(self:None, Inputs = {}, Energy_Requirements = {}, Direct_Emissions = {},Outputs = {}, **kwargs):

        super().__init__()

        # Lists
        self.ParameterList =[]

        # Non-indexed Attributes
        self.Edges = {}

        # Indexed Attributes
        self.Inputs = Inputs
        self.Energy_Requirements = Energy_Requirements
        self.Direct_Emissions = Direct_Emissions
        self.Outputs = Outputs

        self.Attributes = {
            "name":None,
            "type":None, #process/splitter/what have you
            "feed":None, #Batch or continuous
            "temperature_in":None,
            "temperature_out":None,
            "feed_flow_rate":None,
            "ffr_unit":None, #kg/hour g/min etc.
            "retention_time":None,
            "reactor_total_volume":None,
            "reactor_working_volume":None,
            "reactor_mixing_conditions":None, #Continuous or intermittent
            "reactor_mixing_rate":None, #if continuous RPM; intermittent Hz
            "stoichiometry":None, #is this even usable...?
            "conversion_efficiency":None,
            "yield":None, #per dry input
            "purity":None,#percentage
            "total_solids":None,
            "total_nitrogen":None,
            "carbohydrates":None,
            "proteins":None,
            "fats":None,
            "volatile_solids":None,
            "total_solids":None,
            "total_nitrogen":None,
            "carbohydrates":None,
            "proteins":None,
            "fats":None,
            "volatile_solids"
            "equipment_purchase_year":None,
            "equipment_cost":None,
            "economy_of_scale":None,
            "maintenance_time":None,
            "maintenance_cost":None,
            "selling_price":None,
            "input_price":None
        }

        for att in kwargs:
            self.Attributes[att] = None if kwargs[att] is None else kwargs[att]
