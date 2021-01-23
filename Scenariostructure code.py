#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 21:05:02 2020

@author: xiaoshiguo
"""
from fractions import Fraction
J = 50
f = open("ScenarioStructure1.dat", 'w+')

print("set Stages := FirstStage SecondStage; ", file=f)
print("set Nodes :=", file = f)

print("RootNode", file = f)
for i in range(1, J+1):
    print("Node" + str(i), file = f)
print(";", file = f)

print("param NodeStage := RootNode FirstStage", file = f)
for i in range(1, J+1):
    print("Node" + str(i)+ " "+ "SecondStage", file = f)
print(";", file = f)

print("set Children[RootNode] := ", file = f)
for i in range(1, J+1):
    print("Node" + str(i), file = f)
print(";", file = f)

print("param ConditionalProbability := ", file = f)
print("RootNode 1.0", file = f)
fraction = 1/J
for i in range(1, J+1):
    print("Node" + str(i)+ " "+ str(fraction), file = f)
print(";", file = f)

print("set Scenarios :=", file = f)
for i in range(1, J+1):
    print("Scenario" + str(i), file = f)
print(";", file = f)


print("param ScenarioLeafNode :=", file =f)
for i in range(1, J+1):
    print("Scenario" + str(i)+" "+"Node"+ str(i), file = f)
print(";", file = f)


print("set StageVariables[FirstStage] :=", file =f)
print("weight", file =f)
print("eta;", file =f)

print("set StageVariables[SecondStage] :=", file =f)
print("ExcessAvail", file =f)
print("nu;", file =f)


print("param StageCost := ", file =f)
print("FirstStage  StageCost[1]", file =f)
print("SecondStage StageCost[2];", file =f)

print("param ScenarioBasedData := True ;", file =f)

f.close()
