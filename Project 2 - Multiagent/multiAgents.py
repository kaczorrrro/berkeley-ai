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
    return betterEvaluationFunction(currentGameState)
    #return currentGameState.getScore()

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
    from util import nearestPoint
    pacman = currentGameState.getPacmanPosition()
    foodList = currentGameState.getFood().asList()
    capsulesList = currentGameState.getCapsules()
    ghostStates = currentGameState.getGhostStates()
    score = currentGameState.getScore()

    bonus = 20 * (2-len(capsulesList)) 

    if currentGameState.isWin():
        return score + 500 + bonus
    elif currentGameState.isLose():
        return score -500

    for ghostState in ghostStates:
        #scared ghost
        if ghostState.scaredTimer > 0 :
            return score + bonus + 100.0/mazeDistance(nearestPoint(ghostState.getPosition()), pacman, currentGameState)


   

    #food distance
    mfd1 = 1000
    mfd2 = 1000
    p1 = None
    p2 = None
    if len(capsulesList) != 0:
        minDist = 1000
        goodCap = None
        for cap in capsulesList:
            if manhattanDistance(cap,pacman) < minDist:
                minDist = manhattanDistance(cap,pacman) 
                goodCap = cap

        minFoodDistance = 1.0/mazeDistance(cap,pacman,currentGameState)
    else:
        for food in foodList:
            distance = manhattanDistance(food, pacman)
            if mfd2 > distance:
                if mfd1 > distance:
                    mfd2 = mfd1
                    mfd1 = distance
                    p2 = p1
                    p1 = food
                    if mfd1 == 1:
                        break
                else :
                    mfd2 = distance
                    p2 = food

        if p2 != None:
            minFoodDistance = min( (mazeDistance(pacman,p1,currentGameState)), mazeDistance(pacman,p2,currentGameState) )
        else :
           minFoodDistance = mazeDistance(pacman,p1,currentGameState)
        minFoodDistance = 1.0/minFoodDistance


          


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
    else :
        badGhostDistance = -0.5/badGhostDistance

    

             
    finalValue = score + minFoodDistance * 5 + bonus + badGhostDistance
    return finalValue

# Abbreviation
better = betterEvaluationFunction














from game import Directions
from game import Agent
from game import Actions
import util
import time

def mazeDistance(point1, point2, gameState):
    """
    Returns the maze distance between any two points, using the search functions
    you have already built. The gameState can be any game state -- Pacman's
    position in that state is ignored.

    Example usage: mazeDistance( (2,4), (5,6), gameState)

    This might be a useful helper function for your ApproximateSearchAgent.
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + str(point1)
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)
    return len(breadthFirstSearch(prob))

class SearchProblem:
    def getStartState(self):
        util.raiseNotDefined()

    def isGoalState(self, state):
        util.raiseNotDefined()

    def getSuccessors(self, state):
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        util.raiseNotDefined()

class PositionSearchProblem(SearchProblem):
    """
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problem can be used to find paths
    to a particular point on the pacman board.

    The state space consists of (x,y) positions in a pacman game.

    Note: this search problem is fully specified; you should NOT change it.
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print 'Warning: this does not look like a regular search maze'

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For display purposes only
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )

        # Bookkeeping for display purposes
        self._expanded += 1 # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999.
        """
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost



def breadthFirstSearch(problem):
    from util import Queue
    from game import Directions
    closed = set()
    fringe = Queue()
    fringe.push([problem.getStartState(),[]])

    while not fringe.isEmpty():
        queueElem = fringe.pop()
        node = queueElem[0]
        actionList = queueElem[1]

        #print "zawartosc sprawdzownych"
        #print closed

        if problem.isGoalState(node):
            return actionList

        if not node in closed:
            closed.add(node)
            for children in problem.getSuccessors(node):
                fringe.push([children[0], actionList + [children[1]] ])