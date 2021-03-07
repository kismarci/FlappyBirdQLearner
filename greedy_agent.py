# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 22:44:55 2019

@author: Marci
Simpliest Greedy Agent, flaps every time the ydif is smaller the a set threshold, no learning is done.
"""
Save_Score_File = "saver/greedy_scores.csv"

class greedy_agent(object):
    def __init__(self):
        self.__count=1
        self.th=15 #threshold

    def act(self, xdif, ydif, playerVelY):
        if ydif<self.th: return True #Flap
        else: return False #don't Flap
        
    def dead(self, score):
        with open(Save_Score_File, 'a') as f:
            f.write(str(score) + '\n')

        if (self.__count % 10 == 0):
            print(str(self.__count) + ". game score saved.")
        self.__count += 1


    def stop(self):
        return