# multiAgents.py
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
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

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

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newGhostPositions = successorGameState.getGhostPositions()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        
        finalScore = 0
        minDistanceInitial = 10000

        # very negative if close to unscared, very positive if close to 
        for ghostState in newGhostStates:
            #unscared ghost
            ghostPos = ghostState.getPosition()
            if ghostState.scaredTimer == 0:
                if manhattanDistance(newPos,ghostPos) <= 1 :
                    finalScore -=10000
            #scared ghost        
            else :
                if manhattanDistance(newPos,ghostPos) == 0 :
                    finalScore +=9000
        
        if finalScore != 0:
            return finalScore

        #checks for scared ghosts, and if it is possible to catch them it tries
        minDistance = minDistanceInitial
        for ghostState in newGhostStates:
            if ghostState.scaredTimer > 0 :
                dist = manhattanDistance(ghostState.getPosition(),newPos)
                if minDistance > dist:
                    minDistance = dist
        if minDistance != minDistanceInitial:
            return 1000 - minDistance

        #if going to new pos means eating food, return 1000
        if newPos in currentGameState.getFood().asList():
            return 100

            
        finalScore = -5000
        #distance to food
        minDistance = minDistanceInitial
        for foodPos in newFood.asList():
            if manhattanDistance(newPos,foodPos)<minDistance :
                minDistance = manhattanDistance(newPos,foodPos)
        
        
        #ghost distance
        minGhostDist = minDistanceInitial
        for ghostState in newGhostStates:
            if ghostState.scaredTimer == 0 :
                dist = manhattanDistance(ghostState.getPosition(),newPos) 
                if dist < minGhostDist :
                    minGhostDist = dist


        finalScore -= minDistance
        finalScore += successorGameState.getScore()
        if minGhostDist != minDistanceInitial :
            finalScore -=(minGhostDist/10) 

        
        

        "*** YOUR CODE HERE ***"
        return finalScore

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game

          gameState.isWin():
            Returns whether or not the game state is a winning state

          gameState.isLose():
            Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"

        

        maxValue = -1000000000
        bestAction = None
        for action in gameState.getLegalActions(0):
            value = self.getValue(gameState.generateSuccessor(0,action), 1, 1)
            if value > maxValue :
                maxValue = value
                bestAction = action   
        return bestAction




    def getValue(self, gameState, currentDepth, agentIndex):
        if currentDepth > self.depth:
            return self.evaluationFunction(gameState)

        if gameState.isWin() or gameState.isLose() :
            return self.evaluationFunction(gameState)
        
        #pacman the maximizer
        if agentIndex == 0:
            bestValue = -1000000000
        #minimizer    
        else :
            bestValue = 1000000000

        bestAction = None

        nextAgentIndex  = (agentIndex + 1)%(gameState.getNumAgents())
        nextDepth = currentDepth
        if nextAgentIndex == 0:
            nextDepth += 1
        
        
        for action in gameState.getLegalActions(agentIndex):
            value = self.getValue(gameState.generateSuccessor(agentIndex,action), nextDepth, nextAgentIndex)
            #pacman the maximizer
            if agentIndex == 0:
                if value > bestValue :
                    bestValue = value
                    bestAction = action
            #minimizer        
            else :
                if value < bestValue:
                    bestValue = value
                    bestAction = action

        return bestValue





        

        



class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

        

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        
        
        maximizersBiggest = -999999
        minimizersLowest = 10000

        maxValue = -1000000000
        bestAction = None
        for action in gameState.getLegalActions(0):
            value = self.getMinValue(gameState.generateSuccessor(0,action), 1, 1,minimizersLowest,maximizersBiggest)
            if value > maxValue :
                maxValue = value
                bestAction = action
                if value > maximizersBiggest:  
                    maximizersBiggest = value


        return bestAction

    def getMaxValue(self, gameState, currentDepth, agentIndex, minimizersLowest, maximizersBiggest):
        if currentDepth > self.depth:
            return self.evaluationFunction(gameState)

        if gameState.isWin() or gameState.isLose() :
            return self.evaluationFunction(gameState)
        
        #pacman the maximize
        biggestValue = -1000000000


        nextAgentIndex  = (agentIndex + 1)%(gameState.getNumAgents())
        nextDepth = currentDepth
        if nextAgentIndex == 0:
            nextDepth += 1
        
        
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex,action)
            value = self.getMinValue(successor, nextDepth, nextAgentIndex,minimizersLowest, maximizersBiggest)

            if value > minimizersLowest:
                #print "maximizer zwraca " + str(value) + " bo minSmallVal to" +  str(minimizersLowest)
                return value

            if value > biggestValue :
                biggestValue = value
                if value > maximizersBiggest:
                    maximizersBiggest = value
                

        #print "max zwraca normalnie " + str(biggestValue)
        return biggestValue

    def getMinValue(self, gameState, currentDepth, agentIndex, minimizersLowest, maximizersBiggest):
        if currentDepth > self.depth:
            return self.evaluationFunction(gameState)

        if gameState.isWin() or gameState.isLose() :
            return self.evaluationFunction(gameState)
        
        #minimizer      
        lowestValue = 1000000000

        nextAgentIndex  = (agentIndex + 1)%(gameState.getNumAgents())
        nextDepth = currentDepth
        if nextAgentIndex == 0:
            nextDepth += 1
        
        
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex,action)

            if nextAgentIndex == 0 :
                value = self.getMaxValue(successor, nextDepth, nextAgentIndex,minimizersLowest, maximizersBiggest)
            else :
                value = self.getMinValue(successor, nextDepth, nextAgentIndex,minimizersLowest, maximizersBiggest)

            if value < maximizersBiggest:
                #print "minimizer zwraca szybciej" + str(value) + "bo maxBigVal to " + str(maximizersBiggest)
                return value    

            if value < lowestValue:
                lowestValue = value
                if value < minimizersLowest:
                    minimizersLowest = value
                
        #print "min zwraca normalnie " + str(lowestValue)
        return lowestValue

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        maxValue = -1000000000
        bestAction = None
        for action in gameState.getLegalActions(0):
            value = self.getExpectedValue(gameState.generateSuccessor(0,action), 1, 1)
            if value > maxValue :
                maxValue = value
                bestAction = action


        return bestAction


    def getMaxValue(self, gameState, currentDepth, agentIndex):
        if currentDepth > self.depth:
            return self.evaluationFunction(gameState)

        if gameState.isWin() or gameState.isLose() :
            return self.evaluationFunction(gameState)
        
        #pacman the maximize
        biggestValue = -1000000000


        nextAgentIndex  = (agentIndex + 1)%(gameState.getNumAgents())
        nextDepth = currentDepth
        if nextAgentIndex == 0:
            nextDepth += 1
        
        
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex,action)
            value = self.getExpectedValue(successor, nextDepth, nextAgentIndex)

            if value > biggestValue :
                biggestValue = value

        #print "max zwraca normalnie " + str(biggestValue)
        return biggestValue

    def getExpectedValue(self, gameState, currentDepth, agentIndex):
        if currentDepth > self.depth:
            return self.evaluationFunction(gameState)

        if gameState.isWin() or gameState.isLose() :
            return self.evaluationFunction(gameState)

        nextAgentIndex  = (agentIndex + 1)%(gameState.getNumAgents())
        nextDepth = currentDepth
        if nextAgentIndex == 0:
            nextDepth += 1
        
        sumOfValues = 0.0
        numberOfActions = len( gameState.getLegalActions(agentIndex) )

        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex,action)

            if nextAgentIndex == 0 :
                value = self.getMaxValue(successor, nextDepth, nextAgentIndex)
            else :
                value = self.getExpectedValue(successor, nextDepth, nextAgentIndex)
            sumOfValues +=value
                
        #print "min zwraca normalnie " + str(lowestValue)
        #print value/numberOfActions  
        return sumOfValues/numberOfActions     

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"

    pacman = currentGameState.getPacmanPosition()
    foodList = currentGameState.getFood().asList()
    capsulesList = currentGameState.getCapsules()
    ghostStates = currentGameState.getGhostStates()
    score = currentGameState.getScore()

    if currentGameState.isWin():
        return score + 500
    elif currentGameState.isLose():
        return score - 500


    #food distance
    minFooddistance = 1000
    for food in foodList:
        if minFooddistance > manhattanDistance(food, pacman):
            minFooddistance = manhattanDistance(food, pacman)
    minFooddistance = 1.0/minFooddistance


    #capsules distance
    minCapsuleDistance = 1000
    if len(capsulesList) > 0:
        for capsule in capsulesList:
            if minCapsuleDistance > manhattanDistance(capsule, pacman):
                minCapsuleDistance = manhattanDistance(capsule, pacman)

        minCapsuleDistance = 1.0/minCapsuleDistance    
    else:
        minCapsuleDistance = 1

    minCapsuleDistance += 40* (2-len(capsulesList))   



    goodGhostDistance = 1000
    for ghostState in ghostStates:
        #scared ghost
        if ghostState.scaredTimer > 0:
            ghostPos = ghostState.getPosition()
            if manhattanDistance(pacman,ghostPos) < goodGhostDistance :
                goodGhostDistance = manhattanDistance(pacman,ghostPos)
    if goodGhostDistance == 1000:
        goodGhostDistance = 0
    else:
        goodGhostDistance  = 1.0/goodGhostDistance   

    


    badGhostDistance = 1000  
    for ghostState in ghostStates:
        #scared ghost
        if ghostState.scaredTimer == 0:
            ghostPos = ghostState.getPosition()
            if manhattanDistance(pacman,ghostPos) < badGhostDistance :
                badGhostDistance = manhattanDistance(pacman,ghostPos) 
    if badGhostDistance == 1000:
        badGhostDistance = 0
    elif badGhostDistance == 2:
        badGhostDistance = -10
    elif badGhostDistance == 1:
        badGhostDistance = -50

    

             
    finalValue = score + 4*minFooddistance + 0.4* minCapsuleDistance + 50.0*goodGhostDistance + 3.0*badGhostDistance
    return finalValue

# Abbreviation
better = betterEvaluationFunction



