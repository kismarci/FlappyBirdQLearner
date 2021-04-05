from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *
from greedy_agent import greedy_agent
from q_learning_agent import q_learning_agent

# import for disabling screen
import os

TAG = "" if len(sys.argv) <= 1 else sys.argv[1]
dumping_rate=10 #after how many iteration update the Q table csv

#initialize the agents
agents={'greedy': greedy_agent(),
            'Q': q_learning_agent()}

#chose agent
agent_name='greedy'
agent=agents[agent_name]

# ctrl + c
import signal
def sigint_handler(signum, frame):
    agent.stop()
    exit()

#-----------------------------------------constants:----------------------------------------
SPEED = 30 # 30 - default, 0 - max speed
SHOW_SCREEN = True
FREEZ_AT_THE_END = False

FLAP = True
NOT_FLAP = False

HORIZONTAL_VELOCITY = 4
FLAP_VELOCITY = -9
MAX_VELOCITY = 10
IMAGES_PLAYER_HEIGHT = 24

PIPE_WIDTH = 52
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
VERTICAL_GAP_SIZE = 100
INFINITE_GAMES = -1
SCREENWIDTH  = 288
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
#---------------------------------------------------------------------------    
FPS = SPEED
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# disable screen
if not SHOW_SCREEN: os.environ["SDL_VIDEODRIVER"] = "dummy"

PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
)



#NUMBER_OF_GAMES = 100
NUMBER_OF_GAMES = -1 #infinite game
def main():
    played_games = 0

    signal.signal(signal.SIGINT, sigint_handler)
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')
    
    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )
    
    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()
    
    while NUMBER_OF_GAMES == INFINITE_GAMES or played_games < NUMBER_OF_GAMES:
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[0]).convert()

        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[0][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[0][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[0][2]).convert_alpha(),
        )
    
        pipeindex = 0
        IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )
    
        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )
    
        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )
    
        #movementInfo = showWelcomeAnimation()
        start_info=start_game()
        crashInfo = mainGame(start_info,played_games)
        showGameOverScreen(crashInfo)
        played_games += 1
        if played_games % dumping_rate == 0 and agent_name!='greedy':
            agent._save_q_values()

def start_game():
    playerIndexGen = cycle([0, 1, 2, 1])
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)
    basex = 0
    while True:
        return {
            'playery': playery,
            'basex': basex,
            'playerIndexGen': playerIndexGen,
        }



def flap(playery, playerFlapAcc):
    if playery > -2 * IMAGES['player'][0].get_height():
        return playerFlapAcc, True
        
def mainGame(start_info, played_games):
    score = playerIndex = loopIter = 0
    playerIndexGen = start_info['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), start_info['playery']
    
    basex = start_info['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
    
    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 =  getRandomPipe()
    newPipe2 =  getRandomPipe()
    
    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    
    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]
    
    myPipe = lowerPipes[0]
    pipeVelX = -4
    
    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerAccY    =   1   # players downward accleration
    playerFlapAcc =  -9   # players speed on flapping
    playerFlapped = False # True when player flaps
    
  
    while True:
        #print(playerx, playery)
        if lowerPipes[0]['x'] + IMAGES['pipe'][0].get_width() - playerx\
            > 0: myPipe = lowerPipes[0]
        else: myPipe = lowerPipes[1]
    
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): #exit the game with Escapce bottun
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP): #flap with space ot up arrow
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY, playerFlapped = flap(playery, playerFlapAcc)
    
        xdif = myPipe['x'] + IMAGES['pipe'][0].get_width() - playerx
        ydif = myPipe['y'] - playery - IMAGES['player'][0].get_height()

        move = agent.act(xdif, ydif, playerVelY) 

        if move and playery > -2 * IMAGES['player'][0].get_height(): 
            playerVelY, playerFlapped = flap(playery, playerFlapAcc) 
    

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
        
        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)
        
        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)
               
        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX
        
        new_xdif = myPipe['x'] + IMAGES['pipe'][0].get_width() - playerx
        new_ydif = myPipe['y'] - playery - IMAGES['player'][0].get_height() 
        if(agent_name!='greedy'):
            agent.get_new_state(new_xdif, new_ydif, playerVelY) #observe new state 
        
        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                            upperPipes, lowerPipes)
        

        if crashTest[0]:
            agent.dead(score) 
            if played_games %10 ==0: print('Score: ', score)
            if(agent_name!='greedy'):
                agent.update_Q_table(alive=False)
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
            }
        else:
            if(agent_name!='greedy'): agent.update_Q_table()
    
        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe =  getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])
        
        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))
        
        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)
        SCREEN.blit(IMAGES['player'][playerIndex], (playerx, playery))
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        

def showGameOverScreen(crashInfo):
    """crashes the player down and shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    
    basex = crashInfo['basex']
    
    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']
    

    if not FREEZ_AT_THE_END: return
    else: 
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    return
        
    
            # draw sprites
            SCREEN.blit(IMAGES['background'], (0,0))
    
            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))
    
            SCREEN.blit(IMAGES['base'], (basex, BASEY))
            showScore(score)
            SCREEN.blit(IMAGES['player'][1], (playerx,playery))
    
            FPSCLOCK.tick(FPS)
            pygame.display.update()



def getRandomPipe(idx=None):
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed
    
    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()
    
    Xoffset = (SCREENWIDTH - totalWidth) / 2
    
    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collides with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()
    
    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:
    
        playerRect = pygame.Rect(player['x'], player['y'],
                    player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)
    
            if uCollide or lCollide:
                return [True, False]
    
    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)
    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y
    
    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    global display
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask


if __name__ == '__main__':
    main()
