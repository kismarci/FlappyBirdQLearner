# FlappyBirdQLearner
Implementation of the Flappy Bird game with [pygame](https://www.pygame.org/news) and reinforcement learning AI bots: greedy learner and Q-learner that learns the skills to play the game. 

This work was done for a university assignment and it is based on [flappybird-qlearning-bot](https://github.com/chncyhn/flappybird-qlearning-bot) and [FlappyBirdBotsAI](https://github.com/martinglova/FlappyBirdBotsAI).


## Dependencies
To run the code you'll need the following packages:

* pygame
* numpy
* sklearn
* matplotlib
* pickle
* collections
* random

Normally the only package that you'll need to install additionally is pygame, which you can do by
    
    pip install pygame

## Running
`flappy.py`-Main file, runs the game with visual display, either you or the AI agent can play the game 

`greedy_agent.py`-Greedy agent class.

`q_learning_agent.py`-Q-learner agent class.

`utils.py`-Utility script to 1) plot the earned scores in function of training iterations; 2) to run multiple concurrent subprocesses (not parallel) with python module to speed up training of the reinforcement learning agent.

`conc_run.sh`- Bash script which executes multiple instances of 'flappy.py' which can run parallel on multicore devices. This helps to speed up training of the reinforcement learning agent.

Screenshot of concurrent training:

![conc_training](https://github.com/kismarci/FlappyBirdQLearner/blob/main/assets/concurrent_training.png)

## Directories

### assets

sprites and hitmasks for the visual output

### saver

`qvalues:` state and action pairs for the Q-learner agent

`q_learning_scores`, `greedy_scores`  achieved score after each play 
