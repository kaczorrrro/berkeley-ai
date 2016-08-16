# powerAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# powerAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from util import manhattanDistance
from game import Directions
from pacman import BLAST_RADIUS, LASER_RANGE, COLLISION_TOLERANCE
import random, util
from game import Agent,AgentPowers

def canShootLaser(shooterPosition, targetPosition, shooterDirection, walls):
    if(util.manhattanDistance(shooterPosition,targetPosition) <= COLLISION_TOLERANCE):
        return False
    (px,py) = shooterPosition
    (gx,gy) = targetPosition
    pxr = int(round(px))
    pyr = int(round(py))
    gxr = int(round(gx))
    gyr = int(round(gy))

    if(abs(px-gx) <= COLLISION_TOLERANCE/2 and py < gy and shooterDirection == Directions.NORTH and not(any([ walls[pxr][y] for y in range(pyr,gyr)]))):
        return True
    if(abs(px-gx) <= COLLISION_TOLERANCE/2 and py > gy and shooterDirection == Directions.SOUTH and not(any(walls[pxr][y] for y in range(gyr,pyr)))):
        return True
    if(px < gx and abs(py - gy) <= COLLISION_TOLERANCE/2 and shooterDirection == Directions.EAST and not(any( walls[x][pyr] for x in range(pxr,gxr)))):
        return True
    if(px > gx and abs(py - gy) <= COLLISION_TOLERANCE/2 and shooterDirection == Directions.WEST and not(any(walls[x][pyr] for x in range(gxr,pxr)))):
        return True
    return False

class ReflexPowerAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.
    """

    def __init__(self):
        self.index = 0 # Pacman is always agent index 0

    def getPowers(self,ghostPowers):
        return AgentPowers(self.laser,self.timeStepsBetweenMoves,self.blast)

    def getAction(self, gameState):
        """
        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """

        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        A sample evaluation function
        """
        successorGameState = currentGameState.generateSuccessor(action)
        x, y = successorGameState.getPacmanPosition()
        pacman = successorGameState.getPacmanState()
        newFood = successorGameState.getFood()

        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [g.scaredTimer for g in newGhostStates]
        score =successorGameState.getScore()
        walls = successorGameState.getWalls()

        ## check if powers etc can land you in trouble
        for ghost in newGhostStates:
            if(ghost.scaredTimer < 2):
                if(self.canKill(ghost,pacman,walls)):
                    score+= -100
            if(self.canKill(pacman,ghost,walls)):
                score+= 50

        ## classical ghost rules : stay away from them
        newScaredTimes = [g.scaredTimer for g in newGhostStates]
        newGhostPos = [g.getPosition() for g in newGhostStates if g.scaredTimer <= 2]
        ghostDists = [abs(x - gx) + abs(y - gy) for gx, gy in newGhostPos]
        deathDist = min(ghostDists) if ghostDists else 0
        #score += 10 * min(deathDist, 5)

        ## food
        numFood = sum([food.count(True) for food in newFood])
        if numFood > 0:
            score -= 10 * numFood
            closestFood = float("inf")
            for i in range(newFood.width):
                for j in range(newFood.height):
                    if newFood[i][j]:
                        closestFood = min(closestFood, abs(x - i) + abs(y - j))
            score -= closestFood
        else:
            score += 100000
        if action == Directions.STOP or action == Directions.LASER or action == Directions.BLAST:
            score -= 1 #small penalty to keep pacman moving
        return score

    def canKill(self, attackerState,victimState,walls):
        #checks if attacker can blast or shoot victim
        attackerPos = attackerState.getPosition()
        victimPos = victimState.getPosition()
        laserPower = attackerState.getLaserPower()
        speed = attackerState.getSpeed()
        blastPower = attackerState.getBlastPower()
        dist = manhattanDistance(victimPos,attackerPos)

        if(not attackerState.isPacman and dist <= speed+0.5):
            return 1

        if(attackerState.isPacman and dist <= speed+0.5 and victimState.scaredTimer > 1):
            return 1

        if(blastPower):
            radius = BLAST_RADIUS[blastPower-1]
            if(dist <= radius):
                return 1

        if(laserPower > 1 or (laserPower==1 and dist<=LASER_RANGE)):
            if(canShootLaser(attackerPos,victimPos,attackerState.getDirection(),walls)):
                return 1

        return 0
