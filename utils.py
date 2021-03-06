# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 23:41:16 2019

@author: Marci
Plot scores to visualize performance of an agent.
Run multiple instances of flappy.py for faster training.
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#-------------------Plotting scores-------------------------------------------------------
scores=pd.read_csv('q_learning_scores.csv')
scores=scores.iloc[:,:].values
plt.scatter(range(len(scores)),scores, s=2)

means=[]
l=[]
for idx, value in enumerate(scores):
    l.append(value)
    if idx % 20 ==0 :
        means.append(np.mean(l)*1.5)
        l.clear()

x_axis=np.arange(len(means))*20        
plt.scatter(range(len(scores)),scores*1.5, s=2,color='black')
plt.plot(x_axis,means,label='average score')
plt.legend()


#---------------------run multiple instances of flappy bird-------------------------------
import sys
import subprocess

procs = []
for i in range(5):
    proc = subprocess.Popen([sys.executable, 'flappy.py'])
    procs.append(proc)

for proc in procs:
    proc.wait()
    
    
    