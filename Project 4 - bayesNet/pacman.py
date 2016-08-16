# pacman.py
# ---------
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


# pacman.py
# ---------
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

"""
Pacman.py holds the logic for the classic pacman game along with the main
code to run a game.  This file is divided into three sections:

  (i)  Your interface to the pacman world:
          Pacman is a complex environment.  You probably don't want to
          read through all of the code we wrote to make the game runs
          correctly.  This section contains the parts of the code
          that you will need to understand in order to complete the
          project.  There is also some code in game.py that you should
          understand.

  (ii)  The hidden secrets of pacman:
          This section contains all of the logic code that the pacman
          environment uses to decide who can move where, who dies when
          things collide, etc.  You shouldn't need to read this section
          of code, but you can if you want.

  (iii) Framework to start a game:
          The final section contains the code for reading the command
          you use to set up the game, then starting up a new game, along with
          linking in all the external parts (agent functions, grapghostrulshics).
          Check this section out to see all the options available to you.

To play your first game, type 'python pacman.py' from the command line.
The keys are 'a', 's', 'd', and 'w' to move (or arrow keys).  Have fun!
"""
from events import EventQueue
from events import Event
from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from util import nearestPoint
from util import manhattanDistance
import util, layout
import sys, types, time, random, os

###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################

class GameState:
    """
    A GameState specifies the full game state, including the food, capsules,
    agent configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.  We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note that in classic Pacman, Pacman is always agent 0.
    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################

    # static variable keeps track of which states have had getLegalActions called
    explored = set()
    def getAndResetExplored():
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp
    getAndResetExplored = staticmethod(getAndResetExplored)

    def getLegalActions( self, agentIndex=0 ):
        """
        Returns the legal actions for the agent specified.
        """
#        GameState.explored.add(self)
        if self.isWin() or self.isLose(): return []

        if agentIndex == 0:  # Pacman is moving
            return PacmanRules.getLegalActions( self )
        else:
            return GhostRules.getLegalActions( self, agentIndex )

    def generateSuccessor( self, action ):
        """
        Returns the successor state after the specified agent takes the action.
        """
        # Check that successors exist
        if self.isWin() or self.isLose() or self.eventQueue.isEmpty():
            raise Exception('Can\'t generate a successor of a terminal state.')

        time, event = self.eventQueue.peek()
        assert event.isAgentMove(), 'Can only generate successors of a state where an agent is about to move'
        state = self.makeAgentMove(action)
        state.resolveEventsUntilAgentEvent()

        # Book keeping
        GameState.explored.add(self.data)
        GameState.explored.add(state.data)
        return state

    def makeAgentMove( self, action ):
        # Copy current state
        state = GameState(self)

        time, event = state.eventQueue.pop()
        agentIndex = event.getAgentIndex()
        agentState = state.data.agentStates[agentIndex]
        state.data.time = time
        delay = agentState.powers.timestepsBetweenMoves
        state.registerEventWithDelay(event, delay)

        # Let agent's logic deal with its action's effects on the board
        if agentIndex == 0:  # Pacman is moving
            state.data._eaten = [False for i in range(state.getNumAgents())]
            PacmanRules.applyAction( state, action )
            state.data.scoreChange -= TIME_PENALTY # Penalty for waiting around
        else:                # A ghost is moving
            GhostRules.applyAction(state, action, agentIndex)
            GhostRules.decrementTimer(agentState)

        # Resolve multi-agent effects
        GhostRules.checkDeath( state, agentIndex )
        if action == Directions.LASER:
            GhostRules.checkLaserShot(state,agentIndex)
        if action == Directions.BLAST:
            GhostRules.checkBlast(state,agentIndex)

        # Book keeping
        state.data._agentMoved = agentIndex
        # Note:  It is important that the following value accurately
        # reflects when Pacman will make the next move, even if the
        # speed changes (such as a speed-up power pellet).  Otherwise
        # the graphics will do weird things.
        state.data._timeTillAgentMovesAgain = delay
        state.data._action = action
        state.data.score += state.data.scoreChange

        return state

    def runEvent( self ):
        # Check that successors exist
        if self.eventQueue.isEmpty():
            raise Exception('Can\'t run an event of a terminal state.')

        time, event = self.eventQueue.pop()
        assert not event.isAgentMove(), 'Can\'t run an AgentMoveEvent'
        self.data.time = time
        event.trigger(self)
        return event

    def getNextEvent( self ):
        _, event = self.eventQueue.peek()
        return event

    def getLegalPacmanActions( self ):
        return self.getLegalActions( 0 )

    def getPacmanState( self ):
        """
        Returns an AgentState object for pacman (in game.py)

        state.pos gives the current position
        state.direction gives the travel vector
        """
        return self.data.agentStates[0].copy()

    def getPacmanPosition( self ):
        return self.data.agentStates[0].getPosition()

    def getPacmanDirection(self):
        return self.data.agentStates[0].getDirection()

    def getGhostStates( self ):
        return self.data.agentStates[1:]

    def getGhostState( self, agentIndex ):
        if agentIndex == 0 or agentIndex >= self.getNumAgents():
            raise Exception("Invalid index passed to getGhostState")
        return self.data.agentStates[agentIndex]

    def getGhostPosition( self, agentIndex ):
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostPosition")
        return self.data.agentStates[agentIndex].getPosition()

    def getGhostPositions(self):
        return [s.getPosition() for s in self.getGhostStates()]

    def getNextAgentIndex(self):
        for time, event in self.eventQueue.getSortedTimesAndEvents():
            if event.isAgentMove():
                return event.getAgentIndex()
        assert False, "No more moves can be made"

    def getAgentMoveTime(self, agentIndex):
        for time, event in self.eventQueue.getSortedTimesAndEvents():
            if event.isAgentMove():
                if event.getAgentIndex() == agentIndex:
                    return time
        assert False, "No more moves can be made by agent " + str(agentIndex)

    def getNumAgents( self ):
        return len( self.data.agentStates )

    def getScore( self ):
        return float(self.data.score)

    def getCapsules(self):
        """
        Returns a list of positions (x,y) of the remaining capsules.
        """
        return self.data.capsules

    def getNumFood( self ):
        return self.data.food.count()

    def getFood(self):
        """
        Returns a Grid of boolean food indicator variables.

        Grids can be accessed via list notation, so to check
        if there is food at (x,y), just call

        currentFood = state.getFood()
        if currentFood[x][y] == True: ...
        """
        return self.data.food

    def getWalls(self):
        """
        Returns a Grid of boolean wall indicator variables.

        Grids can be accessed via list notation, so to check
        if there is a wall at (x,y), just call

        walls = state.getWalls()
        if walls[x][y] == True: ...
        """
        return self.data.walls

    def hasFood(self, x, y):
        return self.data.food[x][y]

    def hasWall(self, x, y):
        return self.data.walls[x][y]

    def isLose( self ):
        return self.data._lose

    def isWin( self ):
        return self.data._win

    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__( self, prevState = None ):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None: # Initial state
            self.data = GameStateData(prevState.data)
            self.eventQueue = prevState.eventQueue.deepCopy()
        else:
            self.data = GameStateData()
            self.eventQueue = EventQueue()

    def resolveEventsUntilAgentEvent(self):
        # Resolve any events until the next agent event
        while not self.eventQueue.isEmpty():
            time, event = self.eventQueue.peek()
            if event.isAgentMove():
                return
            else:
                self.runEvent()

    def registerEventWithDelay(self, event, delay):
        self.eventQueue.registerEventAtTime(event, self.data.time + delay)

    def deepCopy( self ):
        state = GameState( self )
        state.data = self.data.deepCopy()
        # Event queue has already been copied in the constructor
        return state

    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        return hasattr(other, 'data') and self.data == other.data \
            and hasattr(other, 'eventQueue') and self.eventQueue == other.eventQueue \

    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        return hash( (self.data, self.eventQueue) )

    def __str__( self ):

        return str(self.data)

    def initialize( self, layout, pacmanPowers, ghostPowers, numGhostAgents=1000 ):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(layout, pacmanPowers, ghostPowers, numGhostAgents)
        numAgents = self.getNumAgents()
        for i in range(numAgents):
            self.registerEventWithDelay(AgentMoveEvent(i), i)
        self.registerEventWithDelay(WallTimerEvent(), 1)

class AgentMoveEvent(Event):
    """
    The GameStates could be generated in one of two modes - either by
    the main game logic, where actions are solicited from actual
    agents, or in planning mode, where one agent thinks about how
    another agent might respond.  As a result, we don't know what to
    do in trigger, so we do not implement it - instead, the logic in
    GameState should make sure to treat AgentMoveEvents specially.
    """
    def __init__(self, agentIndex, prevId=None):
        Event.__init__(self, prevId)
        self.index = agentIndex

    def getAgentIndex(self):
        return self.index

    def isAgentMove(self):
        return True

    def deepCopy(self):
        return AgentMoveEvent(self.index, self.eventId)

    def __eq__( self, other ):
        return isinstance(other, AgentMoveEvent) and \
            self.index == other.index and \
            self.eventId == other.eventId

    def __hash__( self ):
        return hash((self.index, self.eventId))

    def __str__(self):
        return "Agent " + str(self.getAgentIndex()) + " move"

class WallTimerEvent(Event):
    """
    The GameStates could be generated in one of two modes - either by
    the main game logic, where actions are solicited from actual
    agents, or in planning mode, where one agent thinks about how
    another agent might respond.  As a result, we don't know what to
    do in trigger, so we do not implement it - instead, the logic in
    GameState should make sure to treat AgentMoveEvents specially.
    """
    def trigger(self, state):
        timedWalls = state.data.timedWalls
        for pos in timedWalls.keys():
            if timedWalls[pos] == 1:
                del timedWalls[pos]
                x, y = pos
                state.data.walls[x][y] = False
                state.data._wallsChanged.append(pos)
            else:
                timedWalls[pos] -= 1
        # Repeat this work after 1 more timestep
        state.registerEventWithDelay(self, 1)

    def deepCopy(self):
        return WallTimerEvent(self.eventId)

    def __eq__( self, other ):
        return isinstance(other, WallTimerEvent) and \
            self.eventId == other.eventId

    def __hash__( self ):
        return hash(self.eventId)

############################################################################
#                     THE HIDDEN SECRETS OF PACMAN                         #
#                                                                          #
# You shouldn't need to look through the code in this section of the file. #
############################################################################

SCARED_TIME = 40    # Moves ghosts are scared
COLLISION_TOLERANCE = 0.7 # How close ghosts must be to Pacman to kill
TIME_PENALTY = 1 # Number of points lost each round
LASER_RANGE = 5 # max distance for shooting without full upgrade
BLAST_RADIUS = [2,3] # blast radius with half or full upgrade

class ClassicGameRules:
    """
    These game rules manage the control flow of a game, deciding when
    and how the game starts and ends.
    """
    def __init__(self, timeout=30):
        self.timeout = timeout

    def newGame( self, layout, pacmanAgent, pacmanPowers, ghostAgents, ghostPowers, powerLimit, display, quiet = False, catchExceptions=False):
        agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        initState = GameState()
        initState.initialize( layout, pacmanPowers, ghostPowers, len(ghostAgents) )
        game = Game(agents, powerLimit, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game

    def process(self, state, game):
        """
        Checks to see whether it is time to end the game.
        """
        if state.isWin(): self.win(state, game)
        if state.isLose(): self.lose(state, game)

    def win( self, state, game ):
        if not self.quiet: print "Pacman emerges victorious! Score: %d" % state.data.score
        game.gameOver = True

    def lose( self, state, game ):
        if not self.quiet: print "Pacman died! Score: %d" % state.data.score
        game.gameOver = True

    def getProgress(self, game):
        return float(game.state.getNumFood()) / self.initialState.getNumFood()

    def agentCrash(self, game, agentIndex):
        if agentIndex == 0:
            print "Pacman crashed"
        else:
            print "A ghost crashed"

    def getMaxTotalTime(self, agentIndex):
        return self.timeout

    def getMaxStartupTime(self, agentIndex):
        return self.timeout

    def getMoveWarningTime(self, agentIndex):
        return self.timeout

    def getMoveTimeout(self, agentIndex):
        return self.timeout

    def getMaxTimeWarnings(self, agentIndex):
        return 0

class PacmanRules:
    """
    These functions govern how pacman interacts with his environment under
    the classic game rules.
    """
    PACMAN_SPEED=1

    def getLegalActions( state ):
        """
        Returns a list of possible actions.
        """
        possibleActions = Actions.getPossibleActions( state.getPacmanState().configuration, state.data.walls )
        if not(state.getPacmanState().getLaserPower()) and Directions.LASER in possibleActions:
            possibleActions.remove( Directions.LASER )
        if not state.getPacmanState().getBlastPower():
            possibleActions.remove(Directions.BLAST)
        return possibleActions
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action ):
        """
        Edits the state to reflect the results of the action.
        """
        legal = PacmanRules.getLegalActions( state )
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        pacmanState = state.data.agentStates[0]

        # Update Configuration
        vector = Actions.directionToVector( action, PacmanRules.PACMAN_SPEED )
        pacmanState.configuration = pacmanState.configuration.generateSuccessor( vector )

        # Eat
        next = pacmanState.configuration.getPosition()
        nearest = nearestPoint( next )
        if manhattanDistance( nearest, next ) <= 0.5 :
            # Remove food
            PacmanRules.consume( nearest, state )
    applyAction = staticmethod( applyAction )

    def consume( position, state ):
        x,y = position
        # Eat food
        if state.data.food[x][y]:
            state.data.scoreChange += 10
            state.data.food = state.data.food.copy()
            state.data.food[x][y] = False
            state.data._foodEaten = position
            # TODO: cache numFood?
            numFood = state.getNumFood()
            if numFood == 0 and not state.data._lose:
                state.data.scoreChange += 500
                state.data._win = True
        # Eat capsule
        for capsule in state.getCapsules():
            if position == capsule.getPosition():
                state.data.capsules.remove( capsule )
                state.data._capsuleEaten = capsule
                capsule.performAction(state)
            # Reset all ghosts' scared timers
            # for index in range( 1, len( state.data.agentStates ) ):
                # state.data.agentStates[index].scaredTimer = SCARED_TIME
    consume = staticmethod( consume )

class GhostRules:
    """
    These functions dictate how ghosts interact with their environment.
    """
    GHOST_SPEED=1.0
    def getLegalActions( state, ghostIndex ):
        """
        Ghosts cannot stop, and cannot turn around unless they
        reach a dead end, but can turn 90 degrees at intersections.
        """
        agentState = state.data.agentStates[ghostIndex]
        hasLaser = 1
        hasBlast = 1
        if(not(agentState.getLaserPower()) or agentState.scaredTimer > 0):
            hasLaser = 0 #scared ghosts shoot no laser
        if(not(agentState.getBlastPower()) or agentState.scaredTimer > 0):
            hasBlast = 0 #scared ghosts do not use blast

        conf = state.getGhostState( ghostIndex ).configuration
        possibleActions = Actions.getPossibleActions( conf, state.data.walls)
        reverse = Actions.reverseDirection( conf.direction)
        if Directions.STOP in possibleActions:
            possibleActions.remove( Directions.STOP)
        if (not hasLaser) and (Directions.LASER in possibleActions):
            possibleActions.remove( Directions.LASER )
        if (not hasBlast) and (Directions.BLAST in possibleActions):
            possibleActions.remove( Directions.BLAST)
        if reverse in possibleActions and len( possibleActions ) > (1+hasLaser+hasBlast): #2 instead of 1 because of LASER
            possibleActions.remove(reverse)
        return possibleActions
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action, ghostIndex):

        legal = GhostRules.getLegalActions( state, ghostIndex )
        if action not in legal:
            raise Exception("Illegal ghost action " + str(action))

        ghostState = state.data.agentStates[ghostIndex]
        speed = GhostRules.GHOST_SPEED
        if ghostState.scaredTimer > 0: speed /= 2.0
        vector = Actions.directionToVector( action, speed )
        ghostState.configuration = ghostState.configuration.generateSuccessor( vector )
    applyAction = staticmethod( applyAction )

    def decrementTimer(ghostState):
        timer = ghostState.scaredTimer
        if timer == 1:
            ghostState.configuration.pos = nearestPoint( ghostState.configuration.pos )
        ghostState.scaredTimer = max( 0, timer - 1 )
    decrementTimer = staticmethod( decrementTimer )

    def checkDeath( state, agentIndex):
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0: # Pacman just moved; Anyone can kill him
            for index in range( 1, len( state.data.agentStates ) ):
                ghostState = state.data.agentStates[index]
                ghostPosition = ghostState.configuration.getPosition()
                if GhostRules.canKill( pacmanPosition, ghostPosition ):
                    GhostRules.collide( state, ghostState, index )
        else:
            ghostState = state.data.agentStates[agentIndex]
            ghostPosition = ghostState.configuration.getPosition()
            if GhostRules.canKill( pacmanPosition, ghostPosition ):
                GhostRules.collide( state, ghostState, agentIndex )
    checkDeath = staticmethod( checkDeath )

    def checkLaserShot(state,agentIndex):
        """
        Checks for death due to a laser shot.  Assumes that agentIndex
        used a Laser action, and that this action was valid.
        """
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0: # Pacman shot laser moved; can kill any ghost
            for index in range( 1, len( state.data.agentStates ) ):
                ghostState = state.data.agentStates[index]
                ghostPosition = ghostState.configuration.getPosition()
                dist = manhattanDistance(ghostPosition,pacmanPosition)
                if(dist <= LASER_RANGE or state.data.agentStates[agentIndex].getLaserPower() > 1):
                    if GhostRules.canShootLaser( pacmanPosition, ghostPosition, state.getPacmanDirection(), state.getWalls()):
                        GhostRules.laserShot(state, ghostState, index)
        else: #ghost shot laser, check if pacman died
            pacmanState = state.getPacmanState()
            ghostState = state.data.agentStates[agentIndex]
            ghostPosition = ghostState.configuration.getPosition()
            dist = manhattanDistance(ghostPosition,pacmanPosition)
            if(dist <= LASER_RANGE or state.data.agentStates[agentIndex].getLaserPower() > 1): #if pacman is within shooting range of ghost
                #check if ghost can shoot pacman
                if GhostRules.canShootLaser( ghostPosition, pacmanPosition, ghostState.configuration.getDirection(), state.getWalls()):
                    GhostRules.laserShot(state, pacmanState, 0)
    checkLaserShot = staticmethod(checkLaserShot)
    
    def checkBlast(state,agentIndex):
        """
        Checks for death due to an explosion.  Assumes that agentIndex
        used a Blast action, and that this action was valid.
        """
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0: # Pacman used blast; can kill any ghost
            radius = BLAST_RADIUS[state.data.agentStates[agentIndex].getBlastPower()-1]
            for index in range( 1, len( state.data.agentStates ) ):
                ghostState = state.data.agentStates[index]
                ghostPosition = ghostState.configuration.getPosition()
                dist = manhattanDistance(ghostPosition,pacmanPosition)
                if(dist <= radius and dist > COLLISION_TOLERANCE):
                    GhostRules.laserShot(state, ghostState, index) # death rules are same for blast and laser

        else: #ghost used blast, check if pacman died
            radius = BLAST_RADIUS[state.data.agentStates[agentIndex].getBlastPower()-1]
            pacmanState = state.getPacmanState()
            ghostState = state.data.agentStates[agentIndex]
            ghostPosition = ghostState.configuration.getPosition()
            dist = manhattanDistance(ghostPosition,pacmanPosition)
            if(dist <= radius and dist > COLLISION_TOLERANCE): #if pacman is within shooting range of ghost
                #check if ghost can shoot pacman
                GhostRules.laserShot(state, pacmanState, 0)

    checkBlast = staticmethod(checkBlast)

    def collide( state, ghostState, agentIndex):
        if ghostState.scaredTimer > 0:
            state.data.scoreChange += 200
            GhostRules.placeGhost(state, ghostState)
            ghostState.scaredTimer = 0
            # Added for first-person
            state.data._eaten[agentIndex] = True
        else:
            if not state.data._win:
                state.data.scoreChange -= 500
                state.data._lose = True
    collide = staticmethod( collide )

    def laserShot(state, agentState, agentIndex):
        if(agentIndex != 0):
            GhostRules.placeGhost(state, agentState)
            state.data.scoreChange += 100
            agentState.scaredTimer = 0
            # Added for first-person
            state.data._eaten[agentIndex] = True
        else:
            if not state.data._win:
                state.data.scoreChange -= 500
                state.data._lose = True

    laserShot = staticmethod(laserShot)

    def canKill( pacmanPosition, ghostPosition ):
        return manhattanDistance( ghostPosition, pacmanPosition ) <= COLLISION_TOLERANCE
    canKill = staticmethod( canKill )


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

    canShootLaser = staticmethod(canShootLaser)


    def placeGhost(state, ghostState):
        ghostState.configuration = ghostState.start
    placeGhost = staticmethod( placeGhost )

#############################
# FRAMEWORK TO START A GAME #
#############################

def default(str):
    return str + ' [Default: %default]'

def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts

def readCommand( argv ):
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='mediumClassic')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-w', '--pacmanPowers', dest='pacmanPowers',
                      help=default('the powers that Pacman has, eg. laser=1,blast=1'),
                      default='')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default('the ghost agent TYPE(s) in the ghostAgents module to use'),
                      metavar = 'TYPE', default='RandomGhost')
    parser.add_option('-k', '--numghosts', type='int', dest='numGhosts',
                      help=default('the maximum number of ghosts to use'), default=4)
    parser.add_option('-s', '--ghostPowers', dest='ghostPowers',
                      help=default('the list of ghost powers, eg. "{speed=1.5,blast=1},{laser=2}"'),
                      default='')
    parser.add_option('-m', '--powerLimit', type='int', dest='powerLimit',
                      help=default('the maximum number of powers an agent can have'),
                      default=2)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-a','--agentArgs',dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed: random.seed('cs188')

    # Choose a layout
    args['layout'] = layout.getLayout( options.layout )
    if args['layout'] == None: raise Exception("The layout " + options.layout + " cannot be found")

    # Choose a Pacman agent
    noKeyboard = options.gameToReplay == None and (options.textGraphics or options.quietGraphics)
    pacmanType = loadAgent(options.pacman, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    if options.numTraining > 0:
        args['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts: agentOpts['numTraining'] = options.numTraining
    pacman = pacmanType(**agentOpts) # Instantiate Pacman with agentArgs
    args['pacman'] = pacman

    # Don't display training games
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # Choose the ghost agents
    ghostTypes = options.ghost.split(',')
    if len(ghostTypes) == 1:
        ghostType = loadAgent(options.ghost, noKeyboard)
        args['ghosts'] = [ghostType( i+1 ) for i in range( options.numGhosts )]
    else:
        result = []
        for i in range(len(ghostTypes)):
            ghostType = loadAgent(ghostTypes[i], noKeyboard)
            result.append(ghostType(i+1))
        args['ghosts'] = result

    # Choose the agent powers
    args['pacmanPowers'] = parseDictEntries(options.pacmanPowers)
    if args['pacmanPowers'] is None:
        raise Exception('Pacman powers not understood: ' + options.pacmanPowers)

    ghostPowers = options.ghostPowers
    args['ghostPowers'] = parseGhostPowers(ghostPowers)
    if args['ghostPowers'] is None:
        raise Exception('Ghost powers not understood: ' + ghostPowers)

    args['powerLimit'] = options.powerLimit

    # Choose a display format
    if options.quietGraphics:
        import textDisplay
        args['display'] = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        textDisplay.SLEEP_TIME = options.frameTime
        args['display'] = textDisplay.PacmanGraphics()
    else:
        import graphicsDisplay
        args['display'] = graphicsDisplay.PacmanGraphics(options.zoom, frameTime = options.frameTime)
    args['numGames'] = options.numGames
    args['record'] = options.record
    args['catchExceptions'] = options.catchExceptions
    args['timeout'] = options.timeout

    # Special case: recorded games don't use the runGames method or args structure
    if options.gameToReplay != None:
        print 'Replaying recorded game %s.' % options.gameToReplay
        import cPickle
        f = open(options.gameToReplay)
        try: recorded = cPickle.load(f)
        finally: f.close()
        recorded['display'] = args['display']
        replayGame(**recorded)
        sys.exit(0)

    return args

def loadAgent(pacman, nographics):
    # Looks through all pythonPath Directories for the right module,
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir): continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                if nographics and modulename == 'keyboardAgents.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, pacman)
    raise Exception('The agent ' + pacman + ' is not specified in any *Agents.py.')


def parseDictEntries(dictStr):
    result = {}
    if dictStr == '':
        return result
    for power in dictStr.split(','):
        vals = power.split('=')
        if len(vals) != 2:
            return None
        name, value = vals
        result[name] = value
    return result

def parseGhostPowers(s):
    result = []
    while s:
        endIndex = s.find('}')
        if s[0] != '{' or endIndex == -1 or \
           (endIndex + 1 < len(s) and s[endIndex+1] != ','):
            return None
        powers = parseDictEntries(s[1:endIndex])
        if powers is None:
            return None
        result.append(powers)
        s = s[endIndex+2:]
    #print result
    return result #only consider one ghost's power and make all share the same

# TODO: Update to work with runEvent instead of generateSuccessor
# (maybe not necessary, but could make graphics a bit smoother)
# TODO: Interface of newGame has changed to accommodate powers, so
# this will no longer work
def replayGame( layout, actions, display ):
    import pacmanAgents, ghostAgents
    rules = ClassicGameRules()
    agents = [pacmanAgents.GreedyAgent()] + [ghostAgents.RandomGhost(i+1) for i in range(layout.getNumGhosts())]
    game = rules.newGame( layout, agents[0], agents[1:], display )
    state = game.state
    display.initialize(state.data)

    for agent, action in actions:
        # Execute the action
        state = state.generateSuccessor( action )
        # Change the display
        display.update( state.data )
        # Allow for game specific conditions (winning, losing, etc.)
        rules.process(state, game)

    display.finish()

def runGames( layout, pacman, pacmanPowers, ghosts, ghostPowers, powerLimit, display, numGames, record, numTraining = 0, catchExceptions=False, timeout=30 ):
    import __main__
    __main__.__dict__['_display'] = display

    rules = ClassicGameRules(timeout)
    games = []

    for i in range( numGames ):
        beQuiet = i < numTraining
        if beQuiet:
                # Suppress output and graphics
            import textDisplay
            gameDisplay = textDisplay.NullGraphics()
            rules.quiet = True
        else:
            gameDisplay = display
            rules.quiet = False
        game = rules.newGame( layout, pacman, pacmanPowers, ghosts, ghostPowers, powerLimit, gameDisplay, beQuiet, catchExceptions)
        game.run()
        if not beQuiet: games.append(game)

        if record:
            import time, cPickle
            fname = ('recorded-game-%d' % (i + 1)) +  '-'.join([str(t) for t in time.localtime()[1:6]])
            f = file(fname, 'w')
            components = {'layout': layout, 'actions': game.moveHistory}
            cPickle.dump(components, f)
            f.close()

    if (numGames-numTraining) > 0:
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True)/ float(len(wins))
        print 'Average Score:', sum(scores) / float(len(scores))
        print 'Scores:       ', ', '.join([str(score) for score in scores])
        print 'Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), winRate)
        print 'Record:       ', ', '.join([ ['Loss', 'Win'][int(w)] for w in wins])

    return games

if __name__ == '__main__':
    """
    The main function called when pacman.py is run
    from the command line:

    > python pacman.py

    See the usage string for more details.

    > python pacman.py --help
    """
    args = readCommand( sys.argv[1:] ) # Get game components based on input
    runGames( **args )

    # import cProfile
    # cProfile.run("runGames( **args )")
    pass
