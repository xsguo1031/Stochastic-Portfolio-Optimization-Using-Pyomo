#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 15:29:02 2020

@author: xiaoshiguo
"""

# documentation of pyomo: https://pyomo.readthedocs.io/en/stable/advanced_topics/pysp_rapper/demorapper.html
import pandas as pd
import csv
import numpy as np
import pyomo
from pyomo.core import *
import pyomo.pysp.util.rapper as rapper
import pyomo.pysp.plugins.csvsolutionwriter as csvw
from pyomo.pysp.scenariotree.tree_structure_model import CreateAbstractScenarioTreeModel
#import pyomo.environ as pyo
from pyomo.environ import *


# load the data of index return 
J = 50 
index = open("/Users/xiaoshiguo/Desktop/model"+str(J)+"/R_gen"+str(J)+".csv", "r")
reader = csv.reader(index)
count = 0
scen = []
for row in reader:
    if count == 0:
        label = row
    else:
        scen.append(row)
    count += 1
    
b = np.array(scen)
a = b.astype(np.float)  
J = a.shape[0] # number of scenarios 


# load the data of 1-month T-bill rate 
df2 = pd.read_csv("/Users/xiaoshiguo/Desktop/GS1M.csv") 
G = 4
T = 12
F = 1
tbill = df2["GS1M"]/1200 #as the data is presented in percent and annualized 



# define solver function 
def solve_sto(f, IndexReturn, Tbill):
    #The next two lines show one way to create a concrete scenario tree. There are
    #others that can be found in `pyomo.pysp.scenariotree.tree_structure_model`.
    abstract_tree = CreateAbstractScenarioTreeModel()
    concrete_tree = abstract_tree.create_instance("/Users/xiaoshiguo/Desktop/model"+str(J)+"/ScenarioStructure"+str(J)+".dat")
    concrete_tree.IndexReturn = IndexReturn # line added by DLW
    concrete_tree.Tbill = Tbill

    stsolver = rapper.StochSolver("ReferenceModel"+str(J)+".py", fsfct = "pysp_instance_creation_callback", tree_model = concrete_tree)
    #stsolver = rapper.StochSolver("/Users/xiaoshiguo/Desktop/portfolio/models/ReferenceModel.py",  tree_model = concrete_tree)
    
    ef_sol = stsolver.solve_ef('glpk', tee=False)
    # ef_sol = stsolver.solve_ph(subsolver = solvername, default_rho = 1)
    if ef_sol.solver.termination_condition != TerminationCondition.optimal: 
    	    print ("oops! not optimal:",ef_sol.solver.termination_condition) 
    
    #There is an iterator to loop over the root node solution:
    for varname, varval in stsolver.root_Var_solution(): 
        if varname == "weight":
            weight = varval
        else:
            eta = varval
        #print (varname, str(varval)) 
    #a function to compute compute the objective function value
    obj = stsolver.root_E_obj()
    #print ("Expecatation take over scenarios=", obj)
    
    # write down scenario tree in testcref file
    #csvw.write_csv_soln(stsolver.scenario_tree, str(f))
    return obj, weight, eta
 


# solve the instance K times 
List = []
for k in range(b.shape[1]): 
        # Define scenarios and instance
        IndexReturn= {}
        Tbill = {}
        for i in range(1, J+1):
            IndexReturn[f"Scenario{i}"] = a[(i-1),k].tolist() #the second placeholder k is used for the iteration of instances
            Tbill[f"Scenario{i}"] = tbill[(G+T+1)+k].tolist() # corresponding to the index of G+T+1 to G+T+K+1 in RStudio
        # Solve the problem 
        f = k
        List.append(solve_sto(f, IndexReturn, Tbill))

# Get the list of obj and weight 
OBJ = [obj[0] for obj in List]
WEIGHT = [weight[1] for weight in List]
ETA =  [eta[2] for eta in List]

# Get the list 
df = pd.DataFrame({'OBJ':OBJ, 'WEIGHT':WEIGHT, 'ETA': ETA})
df.to_csv("OBJ"+str(J)+".csv", index=False)


     
        
    
    
    
    
            
    
        