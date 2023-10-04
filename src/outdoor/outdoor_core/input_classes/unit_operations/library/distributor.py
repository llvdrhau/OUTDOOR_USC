import math 

from ..superclasses.virtual_process import VirtualProcess



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-------------------------DISTRIBUTOR CLASS------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class Distributor (VirtualProcess): 
    
    """
    Class description
    -----------------
    
    This Class models distributor unit. It works as a (virtual) multi-output 
    valve and enables the SuperstructureModel class the variable splitting of
    flows with constant (inlet-based) concentration profiles.
    
    It inherits from the VirtualProcess class.
    Therefore, it includes mass balance factors.
    
    This class adds parameters which define 
        - Required decimal places
        - Potential target processes 

    Note: 
    Based on the defined decimal numbers the inlet flows can be split to the 
    potential target processes (unit-operations) using different accuracy. Meaning
    decimal number = 1 : 10 % steps, dn = 2: 1 % steps and so on. However, the
    modelling approach uses an inter programming algorithm which introduces 
    a rising number of integer variables for higher decimal numbers, therefore 
    a trade-off between accuracy and calcuation performance should be used. Often
    decimal numbers of 4 are sufficient. 
    
    """
    

    
    
    def __init__(self, Name, UnitNumber, Decimal_place= 3, Targets= None,
                 Parent= None, *args, **kwargs):

        super().__init__(Name, UnitNumber,  Parent) 

        self.Type = "Distributor"  
        self.decimal_numbers = {'Decimal_numbers': {}}
        self.decimal_set = []
        self.decimal_place = self.set_decimalPlace(Decimal_place)
        self.targets = []
        
        
        
    def set_targets(self, targets_list): 
        self.targets = targets_list

    def set_decimalPlace (self, decimal_place):
        self.decimal_place = decimal_place
        self.calc_decimalNumbers()
        
            
        
        
    def calc_decimalNumbers(self):
        X = [1, 2, 4 ,8]
        XO = 0        
        self.decimal_numbers['Decimal_numbers'][self.Number,0] = XO
        self.decimal_set.append((self.Number,0))
        
        for i in range(1,self.decimal_place+1):
            for j in X:
                idx = X.index(j)+1
                idx = idx + (i-1) * 4
                entr = j / (10**i)
                
                self.decimal_numbers['Decimal_numbers'][self.Number,idx] = entr 
                self.decimal_set.append((self.Number,idx))
                
                
                


    def fill_unitOperationsList(self, superstructure):
        
        super().fill_unitOperationsList(superstructure)
        
        if not hasattr(superstructure, 'distributor_list'):
            setattr(superstructure, 'distributor_subset', {'U_DIST_SUB': []})
            setattr(superstructure, 'distributor_list', {'U_DIST': []})
            setattr(superstructure, 'decimal_vector', {'D_VEC': []})
            setattr(superstructure, 'decimal_set', {'DC_SET': []})
            setattr(superstructure, 'distributor_subset2', {'U_DIST_SUB2': []})
        
 
        superstructure.distributor_list['U_DIST'].append(self.Number)
        superstructure.decimal_set['DC_SET'].extend(self.decimal_set)
        
            
        for i in self.targets:
            combi = (self.Number,i) 
            
            if i not in superstructure.distributor_subset['U_DIST_SUB']:
                superstructure.distributor_subset['U_DIST_SUB'].append(combi)

        for i in self.targets:
            for j in self.decimal_numbers['Decimal_numbers'].keys():
                combi2 = (self.Number,i,self.Number,j[1])
                
                superstructure.distributor_subset2['U_DIST_SUB2'].append(combi2)
                

    def fill_parameterList(self):
        

        super().fill_parameterList()
        
        self.ParameterList.append(self.decimal_numbers)
        
            



