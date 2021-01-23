#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________
#
# Imports
#
#import math
import pandas as pd 
import csv
import numpy as np
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory

#
# Model
#
#model = AbstractModel()
J = 50
model = ConcreteModel()

model.NumVarTimes = Param(within = PositiveIntegers, default = 2) # 2-stage problem
model.VarTimes    = RangeSet(model.NumVarTimes) # from 1 to 2

model.IndexReturn= Param(mutable=True) #r_{t,j} stochastic: monthly return rate 

model.Tbill = Param(mutable = True) #f_t: 1-month T-bill rate

model.alpha = Param(default=0.75) # confidence level for CVaR

model.lamda = Param(default = 0.3) # risk-aversion parameter

#
# Variables
#
model.weight = Var(bounds = (-1,1)) #w_t First-stage

model.eta = Var() # eta_{t+1} First stage 

model.ExcessAvail = Var() #x_(t+1,j) Second stage 

model.nu = Var(within=NonNegativeReals) # nu_{t+1,j} Second stage 

model.StageCost = Var(model.VarTimes)

#
# Constraints
# 
def cvar_rule(model):
    return model.nu + model.eta + model.ExcessAvail >= 0.0
model.CVaRConstraint = Constraint(rule=cvar_rule)

def ExcessReturn_rule(model):
     return (model.IndexReturn - model.Tbill)*(model.weight) == model.ExcessAvail
model.ExcessReturnConstraint = Constraint(rule = ExcessReturn_rule)

#
# Stage-specific cost computations
#
def stage_cost_rule(model,t):
    if t == 1:
        return model.StageCost[t] - model.lamda * model.eta == 0 # since eta do not need to multiply any probability
    else:
        return model.StageCost[t] + model.ExcessAvail - model.lamda * model.nu/(1-model.alpha) == 0.0
model.ComputeStageCost = Constraint(model.VarTimes,rule=stage_cost_rule)

def total_cost_rule(model):
    return model.StageCost[1] + model.StageCost[2]
model.Total_Cost_Objective = Objective(rule=total_cost_rule, sense=minimize)


# Reference: https://github.com/Pyomo/pyomo/blob/master/examples/pysp/farmer/concreteNetX/ReferenceModel.py
# load data for monthly index return 
fin = open("/Users/xiaoshiguo/Desktop/model"+str(J)+"/R_gen"+str(J)+".csv", "r")
reader = csv.reader(fin)
count = 0
scen = []
for row in reader:
    if count == 0:
        label = row
    else:
        scen.append(row)
    count += 1
b = np.array(scen)
b.shape
a = b.astype(np.float)  
IndexReturn = {}
for i in range(1, (a.shape[0]+1)):
    IndexReturn[f"Scenario{i}"] = a[(i-1),0].tolist() #the second placeholder k is used for the iteration of instances 


# load the data of 1-month T-bill rate 
# load the data of 1-month T-bill rate 
df2 = pd.read_csv("/Users/xiaoshiguo/Desktop/GS1M.csv") 
G = 4
T = 12
F = 1
tbill = df2["GS1M"]/1200 #as the data is presented in percent and annualized 
 # delete the first (G+T+F+1) rows of tbill to match the data with scenarios of index return 

Tbill = {}
for i in range(1, (a.shape[0]+1)):
    Tbill[f"Scenario{i}"] = tbill[(G+T+1)].tolist() #the second placeholder k is used for the iteration of instances 


# instantiate scenarios 
def pysp_instance_creation_callback(scenario_tree_model, scenario_name, node_names):
    instance = model.clone()
    IndexReturn = scenario_tree_model.IndexReturn
    Tbill = scenario_tree_model.Tbill
    instance.IndexReturn.store_values(IndexReturn[scenario_name])
    instance.Tbill.store_values(Tbill[scenario_name])
    return instance




