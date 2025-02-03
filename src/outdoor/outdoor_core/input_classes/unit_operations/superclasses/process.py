#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#--------------------------GENERAL PROCESS CLASS-------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class Process():
    """
    Class description
    -----------------

    This is the overall unit-operation / process class, from which all specific
    unit-operations classes inherit its structure. It includes the basic data
    like name, index number, or mass-balance splitfactors.

    It includes setter-methods to fill in the required data as
    single-data set-methods and lumping methods which set more parameters in one
    step.

    """



    def __init__(self, Name, UnitNumber, Parent= None, *args, **kwargs):

        super().__init__()

        # Lists
        self.ParameterList =[]



        # GENERAL ATTRIBUTES
        # ------------------

        # Non-indexed Attributes
        self.Name = Name
        self.Number = UnitNumber
        self.Type = None
        self.Group = None
        self.Connections = dict()
        self.WasteDisposalType = None



        self.Possible_Sources = []





        # Flow ATTRIBUTES
        # ---------------

        # Indexed Attributes
        self.myu ={'split_factor': {}}
        self.conc  ={'concentration': {self.Number: 0}}


        self.kappa_1_lhs_conc = {'lhs_concentration_bool': {}}
        self.kappa_2_lhs_conc = {'lhs_concentration_calc_mode': {}}
        self.kappa_1_rhs_conc = {'rhs_concentration_bool': {}}
        self.kappa_2_rhs_conc = {'rhs_concentration_calc_mode': {}}

        self.FLH = {'full_load_hours': {self.Number: None}}

        if Parent is not None:
            Parent.add_UnitOperations(self)






    def fill_unitOperationsList(self, superstructure):
        superstructure.UnitsList.append(self)
        superstructure.UnitsNumberList['UNIT_PROCESSES'].append(self.Number)
        superstructure.UnitsNumberList2['UU'].append(self.Number)

        for i in self.Possible_Sources:
            if i is not self.Number:
                superstructure.SourceSet['CONNECTED_RAW_MATERIAL_UNIT_OPERATION'].append((i,self.Number))


        if self.Group is not None:
            try:
                superstructure.groups[self.Group].append(self.Number)
            except:
                superstructure.groups[self.Group] = [self.Number]

        if self.Connections:
            superstructure.connections[self.Number] = dict()
            for i,j in self.Connections.items():
                superstructure.connections[self.Number][i] = j



    # GENERAL DATA SETTING
    # --------------------

    def set_generalData(self,
                        ProcessGroup,
                        lifetime,
                        emissions=0,
                        full_load_hours=None,
                        maintenancefactor=None,
                        CostPercentage=None,
                        TimeSpan=None,
                        TimeMode=None,
                        wasteDisposalType=None,
                         ):

        self.set_group(ProcessGroup)
        self.set_full_load_hours(full_load_hours)

        # if wasteDisposalType is not None, set it only works with the UI interface, hence the if statement
        if wasteDisposalType:
            self.set_wasteDisposalType(wasteDisposalType)



    def set_name(self, Name):
        self.Name = Name

    def set_number(self, Number):
        self.Number = Number

    def set_group(self, processgroup):
        self.Group = processgroup

    def set_full_load_hours(self, full_load_hours = None):
        self.FLH['full_load_hours'][self.Number] = full_load_hours


    def set_connections(self, units_dict):
        self.Connections = units_dict

    def set_wasteDisposalType(self, WasteDisposalType):
        self.WasteDisposalType = WasteDisposalType


    # Flow DATA SETTING
    # -----------------

    def set_flowData(self,
                      RequiredConcentration = None,
                      RightHandSideReferenceFlow = None,
                      LeftHandSideReferenceFlow = None,
                      RightHandSideComponentList = [],
                      LeftHandSideComponentList = [],
                      SplitfactorDictionary = None,
                      ):


        self.__set_conc(RequiredConcentration)
        self.__set_myuFactors(SplitfactorDictionary)


        self.__set_kappa_1_lhs_conc(LeftHandSideComponentList)
        self.__set_kappa_1_rhs_conc(RightHandSideComponentList)
        self.__set_kappa_2_lhs_conc(LeftHandSideReferenceFlow)
        self.__set_kappa_2_rhs_conc(RightHandSideReferenceFlow)


    def __set_conc(self, concentration):
        self.conc['concentration'][self.Number] = concentration


    def __set_myuFactors(self, myu_dic):
        """

        Parameters
        ----------
        myu_dic : Dictionary
            Example: dict = {(u'1,i1):value1, (u'1,i2): value2}

        """
        for i in myu_dic:
            self.myu['split_factor'][self.Number,i] = myu_dic[i]


    def __set_kappa_1_lhs_conc(self, kappa_1_lhs_conc_list):
        """
        Parameters
        ----------
        kappa_1_lhs_conc_dic : Dictionary
            Example: dict = ['I1','I2',...]

        """
        for i in kappa_1_lhs_conc_list:
            if type(i) == list:
                for j in i:
                    self.kappa_1_lhs_conc['lhs_concentration_bool'][self.Number,j] = 1
            else:
                self.kappa_1_lhs_conc['lhs_concentration_bool'][self.Number,i] = 1



    def __set_kappa_1_rhs_conc(self, kappa_1_rhs_conc_list):
        """
        Parameters
        ----------
        kappa_1_rhs_conc_dic : Dictionary
            Example: dict = ['I1','I2',...]

        """
        for i in kappa_1_rhs_conc_list:
            if type(i) == list:
                for j in i:
                    self.kappa_1_rhs_conc['rhs_concentration_bool'][self.Number,j] = 1
            else:
                self.kappa_1_rhs_conc['rhs_concentration_bool'][self.Number,i] = 1



    def __set_kappa_2_lhs_conc(self, kappa_2_lhs_conc_string):
        """
        Parameters
        ----------
        kappa_2_lhs_conc_dic : String
            Example: 'FIN' or 'FOUT'

        """

        if kappa_2_lhs_conc_string  == 'FIN':
            self.kappa_2_lhs_conc['lhs_concentration_calc_mode'][self.Number]  = 1
        elif kappa_2_lhs_conc_string  == 'FOUT':
            self.kappa_2_lhs_conc['lhs_concentration_calc_mode'][self.Number]  = 0
        else:
            self.kappa_2_lhs_conc['lhs_concentration_calc_mode'][self.Number]  = 3



    def __set_kappa_2_rhs_conc(self, kappa_2_rhs_conc_string):
        """
        Parameters
        ----------
        kappa_2_rhs_conc_dic : String
            Example: 'FIN' or 'FOUT'

        """
        if kappa_2_rhs_conc_string  == 'FIN':
            self.kappa_2_rhs_conc['rhs_concentration_calc_mode'][self.Number]  = 1
        elif kappa_2_rhs_conc_string  == 'FOUT':
            self.kappa_2_rhs_conc['rhs_concentration_calc_mode'][self.Number]  = 0
        else:
            self.kappa_2_rhs_conc['rhs_concentration_calc_mode'][self.Number]  = 3


    def set_possibleSources(self, SourceList):

        if type(SourceList) == list:
            for i in SourceList:
                if i not in self.Possible_Sources:
                    self.Possible_Sources.append(i)
        else:
            if SourceList not in self.Possible_Sources:
                self.Possible_Sources.append(SourceList)






    # ADDITIONAL METHODS
    # ------------------




    def fill_parameterList(self):
        """
        Fills ParameterList of Process Unit u which is used to fill Data_File
        In Superstructure Class

        """


        self.ParameterList.append(self.conc)
        self.ParameterList.append(self.myu)
        self.ParameterList.append(self.kappa_1_lhs_conc)
        self.ParameterList.append(self.kappa_2_lhs_conc)
        self.ParameterList.append(self.kappa_1_rhs_conc)
        self.ParameterList.append(self.kappa_2_rhs_conc)
        self.ParameterList.append(self.FLH)





