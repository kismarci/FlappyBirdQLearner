# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 17:58:59 2019

@author: Marci
Q learning player bot. This script contains the class of the Q learning agent, a reinforcement learning technique.
"""
import numpy as np 
from collections import defaultdict 
import pickle
Save_Score_File = "saver/q_learning_scores.csv"

#Q_first = defaultdict()
       

class q_learning_agent(object):
    def __init__(self):
        self.__count=1
        self.eta=0.7 #learning rate
        self.gamma=0.8 #discount factor
        self.epsilon=0.1
        self.base=5
        self.first_state = (420,240,0)
        self.state=(0,0,0)
        self.new_state=(0,0,0)
        self.action = 0
        self.Q_first=defaultdict(self._module_defaultdict)
        #self._save_q_values(first_run=True) #uncomment for the first run
        self.__load_qvalues()
    
    def _module_defaultdict(self):
        return np.zeros(2)

    def __load_qvalues(self):
        #loads Q table as default dict
        with open("saver/qvalues", "rb") as f:
             self.Q=pickle.load(f)
    
    def __state_round(self, number, base):
        return int(base * round(float(int(number))/base)) #round a number to the multiplicant of the base, e.g. 97->95


    def __get_state(self, xdif, ydif, yvel):
        return (self.__state_round(xdif, self.base),self.__state_round(ydif, self.base), yvel)
    

    def act(self, xdif, ydif, playerVelY):
        """
        Chooses the best action with respect to the current state
        """
        self.state = self.__get_state(xdif, ydif, playerVelY) #current state
        if self.Q[self.state][0] >= self.Q[self.state][1]:
            self.action = 0 #action taken
            return False #Don't Flap
        else:
            self.action = 1
            return True #Flap

        
    def get_new_state(self, new_xdif, new_ydif, new_yvel): #new state
        self.new_state=(self.__state_round(new_xdif, self.base),self.__state_round(new_ydif, self.base), new_yvel)
        
    def update_Q_table(self, alive=True): 
        """ 
        Q-Learning algorithm: Off-policy TD control. Finds the optimal greedy policy while improving 
        following an epsilon-greedy policy"""
       
        state=self.state
        act=self.action
        next_state=self.new_state
        if alive==True: reward=1
        else: reward= -1000
        
        # TD Update
        self.Q[state][act] += self.eta*(reward+self.gamma*max(self.Q[next_state])-self.Q[state][act]) 
        
    def _save_q_values(self,first_run=False):
        if first_run: 
            with open('saver/qvalues', 'wb') as f:
                self.Q_first[self.first_state][self.action]=0
                pickle.dump(self.Q_first, f)
        else:
            with open('saver/qvalues', 'wb') as f:
                pickle.dump(self.Q, f)
    
    def createEpsilonGreedyPolicy(self, Q, num_actions): 
        """ 
        Creates an epsilon-greedy policy based 
        on a given Q-function and epsilon. 
           
        Returns a function that takes the state 
        as an input and returns the probabilities 
        for each action in the form of a numpy array  
        of length of the action space(set of possible actions). 
        """
        epsilon=self.epsilon
        def policyFunction(state): 
            Action_probabilities = np.ones(num_actions, dtype = float) * epsilon / num_actions #set all action's prob. to uniform
                      
            best_action = np.argmax(Q[state]) 
            Action_probabilities[best_action] += (1.0 - epsilon) #set best action's prob to (1-e) plus random prob, so the sum makes 1
            return Action_probabilities 
   
        return policyFunction 
    
    def dead(self, score):
        with open(Save_Score_File, 'a') as f:
            f.write(str(score) + '\n')


    def stop(self):
        return
    
    
    

    
    
    
    